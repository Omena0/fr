"""Analysis passes over SSA IR.

Provides:
- Dominator tree (Lengauer-Tarjan simplified)
- Liveness analysis (backward dataflow)
- Loop detection (natural loops via back edges)
- Def-use chains (already implicit in Value.uses)
"""
from __future__ import annotations
from collections import defaultdict
from optimizer.ir import (
    Module, Function, BasicBlock, Instruction, Value, Op,
    TERMINATOR_OPS, SIDE_EFFECT_OPS,
)


# ── Dominator Tree ──────────────────────────────────────────────

class DomTree:
    """Dominator tree for a function's CFG.

    Uses iterative dataflow (simple, correct, fast enough for fr programs).
    """

    def __init__(self, func: Function):
        self.func = func
        # idom[block] = immediate dominator block
        self.idom: dict[BasicBlock, BasicBlock | None] = {}
        # dom_children[block] = blocks immediately dominated by block
        self.dom_children: dict[BasicBlock, list[BasicBlock]] = defaultdict(list)
        # dominance frontier[block] = set of blocks in DF(block)
        self.df: dict[BasicBlock, set[BasicBlock]] = defaultdict(set)
        self._compute()

    def _compute(self):
        blocks = self.func.blocks
        if not blocks:
            return

        entry = blocks[0]
        self.idom[entry] = None

        # Assign post-order numbers
        post_order = []
        visited = set()

        def _dfs(b):
            visited.add(b)
            for s in b.successors:
                if s not in visited:
                    _dfs(s)
            post_order.append(b)

        _dfs(entry)
        post_num = {b: i for i, b in enumerate(post_order)}

        # Iterative dominator computation
        changed = True
        while changed:
            changed = False
            for b in reversed(post_order):
                if b is entry:
                    continue
                new_idom = None
                for p in b.predecessors:
                    if p not in self.idom and p is not entry:
                        continue
                    if new_idom is None:
                        new_idom = p
                    else:
                        new_idom = self._intersect(new_idom, p, post_num)
                if self.idom.get(b) is not new_idom:
                    self.idom[b] = new_idom
                    changed = True

        # Build dom_children
        for b, dom in self.idom.items():
            if dom is not None:
                self.dom_children[dom].append(b)

        # Compute dominance frontier
        for b in blocks:
            if len(b.predecessors) >= 2:
                for p in b.predecessors:
                    runner = p
                    while runner is not None and runner is not self.idom.get(b):
                        self.df[runner].add(b)
                        runner = self.idom.get(runner)

    def _intersect(self, b1, b2, post_num):
        while b1 is not b2:
            while post_num.get(b1, -1) < post_num.get(b2, -1):
                b1 = self.idom.get(b1)
                if b1 is None:
                    return b2
            while post_num.get(b2, -1) < post_num.get(b1, -1):
                b2 = self.idom.get(b2)
                if b2 is None:
                    return b1
        return b1

    def dominates(self, a: BasicBlock, b: BasicBlock) -> bool:
        """Does block a dominate block b?"""
        runner = b
        while runner is not None:
            if runner is a:
                return True
            runner = self.idom.get(runner)
        return False


# ── Liveness Analysis ───────────────────────────────────────────

class LivenessInfo:
    """Backward liveness analysis.

    For each basic block, computes:
    - live_in: set of Values live at block entry
    - live_out: set of Values live at block exit
    """

    def __init__(self, func: Function):
        self.func = func
        self.live_in: dict[BasicBlock, set[Value]] = {}
        self.live_out: dict[BasicBlock, set[Value]] = {}
        self._compute()

    def _compute(self):
        blocks = self.func.blocks

        # Initialize
        for b in blocks:
            self.live_in[b] = set()
            self.live_out[b] = set()

        # Compute gen/kill sets per block
        gen_sets: dict[BasicBlock, set[Value]] = {}
        kill_sets: dict[BasicBlock, set[Value]] = {}

        for b in blocks:
            gen_set = set()
            kill_set = set()
            for inst in b.instructions:
                # Uses: operands not yet killed in this block
                for v in inst.operands:
                    if isinstance(v, Value) and v not in kill_set:
                        gen_set.add(v)
                # Defs: result value
                if inst.result is not None:
                    kill_set.add(inst.result)
            gen_sets[b] = gen_set
            kill_sets[b] = kill_set

        # Fixed-point iteration (backward)
        changed = True
        while changed:
            changed = False
            for b in reversed(blocks):
                # live_out = union of live_in of successors
                new_out = set()
                for s in b.successors:
                    new_out |= self.live_in[s]

                # live_in = gen + (live_out - kill)
                new_in = gen_sets[b] | (new_out - kill_sets[b])

                if new_in != self.live_in[b] or new_out != self.live_out[b]:
                    self.live_in[b] = new_in
                    self.live_out[b] = new_out
                    changed = True

    def is_live_at(self, value: Value, block: BasicBlock) -> bool:
        """Is the value live at the exit of this block?"""
        return value in self.live_out[block]


# ── Live Intervals (for register allocation) ───────────────────

class LiveInterval:
    """Live interval for a single SSA value."""
    __slots__ = ('value', 'start', 'end', 'reg', 'spill_slot', 'crosses_call')

    def __init__(self, value: Value, start: int, end: int):
        self.value = value
        self.start = start
        self.end = end
        self.reg: str | None = None
        self.spill_slot: int | None = None
        self.crosses_call = False

    def overlaps(self, other: LiveInterval) -> bool:
        return self.start < other.end and other.start < self.end

    def __repr__(self):
        reg = f' -> {self.reg}' if self.reg else ''
        spill = f' [spill:{self.spill_slot}]' if self.spill_slot is not None else ''
        return f'Interval({self.value}, [{self.start}, {self.end}){reg}{spill})'


def compute_live_intervals(func: Function) -> list[LiveInterval]:
    """Compute live intervals by numbering all instructions sequentially."""
    intervals: dict[int, LiveInterval] = {}  # value.id → interval
    call_points: list[int] = []  # instruction numbers of call instructions
    inst_num = 0

    # Track block instruction ranges
    block_start: dict[str, int] = {}
    block_end: dict[str, int] = {}

    # Number instructions and record def/use points
    for block in func.blocks:
        block_start[block.label] = inst_num
        for inst in block.instructions:
            # Track call instruction positions — includes ALL ops that emit runtime calls
            if inst.op in (Op.CALL, Op.CALL_EXTERN, Op.CALL_BUILTIN,
                           Op.PRINT, Op.PRINTLN, Op.INPUT,
                           Op.ALLOC_LIST, Op.LIST_GET, Op.LIST_SET,
                           Op.LIST_APPEND, Op.LIST_LEN,
                           Op.ALLOC_STRUCT, Op.STR_CONCAT, Op.TO_STR,
                           Op.TO_BOOL,
                           Op.SQRT, Op.SIN, Op.COS, Op.TAN, Op.ABS,
                           Op.FLOOR, Op.CEIL, Op.ROUND, Op.POW,
                           Op.MIN, Op.MAX,
                           Op.TRY_BEGIN, Op.TRY_END, Op.RAISE):
                call_points.append(inst_num)

            # Record definition point
            if inst.result is not None:
                vid = inst.result.id
                intervals[vid] = LiveInterval(inst.result, inst_num, inst_num + 1)

            # Record use points (extend interval)
            for v in inst.operands:
                if isinstance(v, Value) and v.id in intervals:
                    intervals[v.id].end = max(intervals[v.id].end, inst_num + 1)

            inst_num += 1
        block_end[block.label] = inst_num

    # Fix for loops: extend intervals across back edges.
    # A back edge is a (tail → header) edge where header is numbered before tail.
    # Values live at the header that are defined before the header must stay live
    # through the entire loop (to the end of the tail block).
    for block in func.blocks:
        for succ in block.successors:
            if succ.label in block_start and block_start[succ.label] < block_start[block.label]:
                # Back edge: block → succ (succ is the loop header)
                tail_end = block_end[block.label]
                header_start = block_start[succ.label]
                for iv in intervals.values():
                    if iv.start <= header_start and iv.end > header_start:
                        iv.end = max(iv.end, tail_end)

    # PHI operands are logically used at the end of their predecessor block
    # (where the parallel copy happens), not at the PHI instruction itself.
    for block in func.blocks:
        for phi in block.phi_nodes:
            for operand, pred_block in zip(phi.operands, phi.target_blocks):
                if isinstance(operand, Value) and operand.id in intervals:
                    pred_end = block_end.get(pred_block.label, 0)
                    intervals[operand.id].end = max(intervals[operand.id].end, pred_end)

    # Also extend intervals for params to cover their first use
    for p in func.params:
        if p.id in intervals:
            intervals[p.id].start = 0

    # Mark intervals that span call instructions
    for iv in intervals.values():
        for cp in call_points:
            if iv.start <= cp < iv.end:
                iv.crosses_call = True
                break

    return sorted(intervals.values(), key=lambda iv: iv.start)


# ── Loop Detection ──────────────────────────────────────────────

class Loop:
    """A natural loop in the CFG."""
    __slots__ = ('header', 'blocks', 'back_edges', 'exits', 'depth')

    def __init__(self, header: BasicBlock):
        self.header = header
        self.blocks: set[BasicBlock] = {header}
        self.back_edges: list[tuple[BasicBlock, BasicBlock]] = []
        self.exits: set[BasicBlock] = set()
        self.depth: int = 1

    def contains(self, block: BasicBlock) -> bool:
        return block in self.blocks

    def __repr__(self):
        return f'Loop(header={self.header.label}, depth={self.depth}, blocks={len(self.blocks)})'


class LoopInfo:
    """Detect natural loops and compute loop nesting."""

    def __init__(self, func: Function, dom_tree: DomTree):
        self.func = func
        self.dom_tree = dom_tree
        self.loops: list[Loop] = []
        self._detect()

    def _detect(self):
        # Find back edges: edge (tail → header) where header dominates tail
        back_edges = []
        for block in self.func.blocks:
            for succ in block.successors:
                if self.dom_tree.dominates(succ, block):
                    back_edges.append((block, succ))

        # Build natural loops from back edges
        header_loops: dict[BasicBlock, Loop] = {}
        for tail, header in back_edges:
            if header not in header_loops:
                loop = Loop(header)
                header_loops[header] = loop
            else:
                loop = header_loops[header]
            loop.back_edges.append((tail, header))

            # Collect loop body: all blocks that can reach tail without going through header
            worklist = [tail]
            while worklist:
                b = worklist.pop()
                if b in loop.blocks:
                    continue
                loop.blocks.add(b)
                for p in b.predecessors:
                    if p not in loop.blocks:
                        worklist.append(p)

        self.loops = list(header_loops.values())

        # Compute exits
        for loop in self.loops:
            for b in loop.blocks:
                for s in b.successors:
                    if s not in loop.blocks:
                        loop.exits.add(s)

        # Compute nesting depth
        for i, outer in enumerate(self.loops):
            for inner in self.loops:
                if inner is outer:
                    continue
                if inner.header in outer.blocks and inner.blocks < outer.blocks:
                    inner.depth = max(inner.depth, outer.depth + 1)

    def get_loop_for_block(self, block: BasicBlock) -> Loop | None:
        """Return the innermost loop containing this block."""
        result = None
        for loop in self.loops:
            if block in loop.blocks:
                if result is None or loop.depth > result.depth:
                    result = loop
        return result

    def is_loop_invariant(self, inst: Instruction) -> bool:
        """Is this instruction loop-invariant (all operands defined outside the loop)?"""
        if inst.block is None:
            return False
        loop = self.get_loop_for_block(inst.block)
        if loop is None:
            return False
        if inst.has_side_effects:
            return False
        for v in inst.operands:
            if isinstance(v, Value) and v.defining_inst is not None:
                if v.defining_inst.block in loop.blocks:
                    return False
        return True


# ── Alias Analysis (simple) ─────────────────────────────────────

class AliasResult:
    NO_ALIAS = 0       # Definitely different memory
    MAY_ALIAS = 1      # Unknown
    MUST_ALIAS = 2     # Definitely same memory


def alias_query(a: Instruction, b: Instruction) -> int:
    """Simple alias analysis between two memory operations.

    Since fr has no raw pointers and structs are type-safe, we can be
    very precise: fields of different struct types never alias.
    """
    # Different operations entirely
    if a.op not in (Op.LOAD_FIELD, Op.STORE_FIELD) or \
       b.op not in (Op.LOAD_FIELD, Op.STORE_FIELD):
        return AliasResult.NO_ALIAS

    # Different base structs → no alias
    a_base = a.operands[0] if a.operands else None
    b_base = b.operands[0] if b.operands else None

    if a_base is not None and b_base is not None:
        # Different base values → different structs → no alias
        if a_base is not b_base:
            # Check if same struct type (could alias via different instances)
            a_type = a_base.type
            b_type = b_base.type
            if a_type != b_type:
                return AliasResult.NO_ALIAS
            # Same type but different base → may alias
            return AliasResult.MAY_ALIAS

        # Same base struct, check field index
        if a.imm_int is not None and b.imm_int is not None:
            if a.imm_int != b.imm_int:
                return AliasResult.NO_ALIAS
            return AliasResult.MUST_ALIAS

    return AliasResult.MAY_ALIAS


# ── Combined analysis runner ────────────────────────────────────

class FunctionAnalysis:
    """Run all analyses for a function."""

    def __init__(self, func: Function):
        self.func = func
        self.dom_tree = DomTree(func)
        self.liveness = LivenessInfo(func)
        self.loops = LoopInfo(func, self.dom_tree)
        self.live_intervals = compute_live_intervals(func)

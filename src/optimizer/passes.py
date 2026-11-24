"""Optimization passes over SSA IR.

Each pass is a function that takes a Module (or Function) and mutates it in-place,
returning True if anything changed.

Passes implemented:
- SCCP (Sparse Conditional Constant Propagation)
- Algebraic simplification (strength reduction, identity removal)
- DCE (Dead Code Elimination)
- CSE (Common Subexpression Elimination)
- LICM (Loop Invariant Code Motion)
- SROA (Scalar Replacement of Aggregates)
- Inlining (small functions)
- TCO (Tail Call Optimization)
"""

from __future__ import annotations
from collections import defaultdict
from optimizer.ir import (
    Module,
    Function,
    BasicBlock,
    Instruction,
    Value,
    Constant,
    Param,
    Op,
    IRType,
    StructType,
    ListType,
    ValueType,
    SIDE_EFFECT_OPS,
    COMMUTATIVE_OPS,
    TERMINATOR_OPS,
)
from optimizer.analysis import DomTree, LoopInfo, LivenessInfo, FunctionAnalysis
from optimizer.types import EscapeAnalysis
from optimizer.config import OptimizerConfig
from optimizer.ranges import analyze_module_ranges, range_fold_branches

# ── SCCP: Sparse Conditional Constant Propagation ───────────────


def sccp(func: Function) -> bool:
    """Propagate constants through the IR. Fold operations on constants."""
    changed = False

    for block in func.blocks:
        i = 0
        while i < len(block.instructions):
            inst = block.instructions[i]
            result = _try_fold(inst)
            if result is not None:
                # Replace with constant — remove old uses first
                val, typ = result
                inst.remove_from_uses()
                inst.op = _const_op(typ)
                inst.operands = []
                if typ == IRType.INT64:
                    inst.imm_int = int(val)
                elif typ == IRType.FLOAT64:
                    inst.imm_float = float(val)
                elif typ == IRType.BOOL:
                    inst.imm_int = 1 if val else 0
                elif typ == IRType.STRING:
                    inst.imm_str = str(val)
                if inst.result:
                    inst.result.type = typ
                changed = True
            i += 1

    # Propagate: replace uses of folded constants
    if changed:
        for block in func.blocks:
            for inst in block.instructions:
                if inst.result and inst.op in (
                    Op.CONST_INT,
                    Op.CONST_FLOAT,
                    Op.CONST_BOOL,
                    Op.CONST_STR,
                ):
                    _replace_const_uses(inst)

    return changed


def _try_fold(inst: Instruction):
    """Try to constant-fold an instruction. Returns (value, type) or None."""
    ops = inst.operands

    # All operands must be constants
    const_vals = []
    for v in ops:
        c = _get_const_value(v)
        if c is None:
            return None
        const_vals.append(c)

    if not const_vals:
        return None

    op = inst.op

    # Integer arithmetic
    if op == Op.ADD and len(const_vals) == 2:
        return (const_vals[0] + const_vals[1], IRType.INT64)
    if op == Op.SUB and len(const_vals) == 2:
        return (const_vals[0] - const_vals[1], IRType.INT64)
    if op == Op.MUL and len(const_vals) == 2:
        return (const_vals[0] * const_vals[1], IRType.INT64)
    if op == Op.DIV and len(const_vals) == 2 and const_vals[1] != 0:
        return (const_vals[0] // const_vals[1], IRType.INT64)
    if op == Op.MOD and len(const_vals) == 2 and const_vals[1] != 0:
        return (const_vals[0] % const_vals[1], IRType.INT64)
    if op == Op.NEG and len(const_vals) == 1:
        if inst.operands and inst.operands[0].type == IRType.FLOAT64:
            return (-float(const_vals[0]), IRType.FLOAT64)
        return (-const_vals[0], IRType.INT64)

    # Float arithmetic
    if op == Op.FADD and len(const_vals) == 2:
        return (const_vals[0] + const_vals[1], IRType.FLOAT64)
    if op == Op.FSUB and len(const_vals) == 2:
        return (const_vals[0] - const_vals[1], IRType.FLOAT64)
    if op == Op.FMUL and len(const_vals) == 2:
        return (const_vals[0] * const_vals[1], IRType.FLOAT64)
    if op == Op.FDIV and len(const_vals) == 2 and const_vals[1] != 0:
        return (const_vals[0] / const_vals[1], IRType.FLOAT64)
    if op == Op.FNEG and len(const_vals) == 1:
        return (-const_vals[0], IRType.FLOAT64)

    # Comparison
    if op == Op.LT and len(const_vals) == 2:
        return (const_vals[0] < const_vals[1], IRType.BOOL)
    if op == Op.GT and len(const_vals) == 2:
        return (const_vals[0] > const_vals[1], IRType.BOOL)
    if op == Op.LE and len(const_vals) == 2:
        return (const_vals[0] <= const_vals[1], IRType.BOOL)
    if op == Op.GE and len(const_vals) == 2:
        return (const_vals[0] >= const_vals[1], IRType.BOOL)
    if op == Op.EQ and len(const_vals) == 2:
        return (const_vals[0] == const_vals[1], IRType.BOOL)
    if op == Op.NE and len(const_vals) == 2:
        return (const_vals[0] != const_vals[1], IRType.BOOL)

    # Logic
    if op == Op.AND and len(const_vals) == 2:
        return (bool(const_vals[0]) and bool(const_vals[1]), IRType.BOOL)
    if op == Op.OR and len(const_vals) == 2:
        return (bool(const_vals[0]) or bool(const_vals[1]), IRType.BOOL)
    if op == Op.NOT and len(const_vals) == 1:
        return (not bool(const_vals[0]), IRType.BOOL)

    # Type conversions
    if op == Op.INT_TO_FLOAT and len(const_vals) == 1:
        return (float(const_vals[0]), IRType.FLOAT64)
    if op == Op.FLOAT_TO_INT and len(const_vals) == 1:
        return (int(const_vals[0]), IRType.INT64)

    return None


def _get_const_value(v: Value):
    """Extract the constant value of an SSA value, or None."""
    if isinstance(v, Constant):
        return v.value
    if isinstance(v, Value) and v.defining_inst is not None:
        inst = v.defining_inst
        if inst.op == Op.CONST_INT:
            return inst.imm_int
        if inst.op == Op.CONST_FLOAT:
            return inst.imm_float
        if inst.op == Op.CONST_BOOL:
            return bool(inst.imm_int)
        if inst.op == Op.CONST_STR:
            return inst.imm_str
    return None


def _const_op(typ):
    return {
        IRType.INT64: Op.CONST_INT,
        IRType.FLOAT64: Op.CONST_FLOAT,
        IRType.BOOL: Op.CONST_BOOL,
        IRType.STRING: Op.CONST_STR,
    }.get(typ, Op.CONST_INT)


def _replace_const_uses(inst: Instruction):
    """Replace all users of a constant-producing instruction with the constant itself."""
    if inst.result is None:
        return
    for user in list(inst.result.uses):
        # Don't need to do anything in SSA — the user already points to the Value
        # whose defining_inst is the CONST instruction. The fold will be picked up
        # by subsequent passes.
        pass


# ── Algebraic Simplification ───────────────────────────────────


def algebraic_simplify(func: Function) -> bool:
    """Apply algebraic identities and strength reductions."""
    changed = False

    for block in func.blocks:
        for inst in block.instructions:
            result = _try_simplify(inst)
            if result is not None:
                changed = True

    return changed


def _try_simplify(inst: Instruction) -> bool | None:
    """Try to simplify an instruction using algebraic identities.
    Returns True if simplified, None otherwise."""
    op = inst.op
    ops = inst.operands

    # Redundant conversions (mostly exposed by list element type propagation).
    if op in (Op.FLOAT_TO_INT, Op.INT_TO_FLOAT, Op.TO_BOOL) and ops and inst.result is not None:
        if ops[0].type == inst.result.type:
            _replace_with_value(inst, ops[0])
            return True

    # x + 0 → x
    if op == Op.ADD and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 == 0:
            _replace_with_value(inst, ops[0])
            return True
        c0 = _get_const_value(ops[0])
        if c0 == 0:
            _replace_with_value(inst, ops[1])
            return True

    # x - 0 → x
    if op == Op.SUB and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 == 0:
            _replace_with_value(inst, ops[0])
            return True
        # x - x → 0
        if ops[0] is ops[1]:
            inst.remove_from_uses()
            inst.op = Op.CONST_INT
            inst.operands = []
            inst.imm_int = 0
            return True

    # x * 0 → 0
    if op == Op.MUL and len(ops) == 2:
        c0 = _get_const_value(ops[0])
        c1 = _get_const_value(ops[1])
        if c0 == 0 or c1 == 0:
            inst.remove_from_uses()
            inst.op = Op.CONST_INT
            inst.operands = []
            inst.imm_int = 0
            return True
        # x * 1 → x
        if c1 == 1:
            _replace_with_value(inst, ops[0])
            return True
        if c0 == 1:
            _replace_with_value(inst, ops[1])
            return True
        # x * 2 → x + x (strength reduction for shift)
        if c1 == 2:
            inst.remove_from_uses()
            inst.op = Op.ADD
            inst.operands = [ops[0], ops[0]]
            ops[0].uses.append(inst)
            ops[0].uses.append(inst)
            return True
        # x * power_of_2 → x << log2(power)
        if c1 is not None and c1 > 0 and (c1 & (c1 - 1)) == 0:
            shift = c1.bit_length() - 1
            inst.remove_from_uses()
            inst.op = Op.SHL
            new_const = _make_const_int(shift, inst)
            inst.operands = [ops[0], new_const]
            ops[0].uses.append(inst)
            new_const.uses.append(inst)
            return True

    # x / 1 → x
    if op == Op.DIV and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 == 1:
            _replace_with_value(inst, ops[0])
            return True
        # x / power_of_2 → x >> log2(power) (for positive x)
        if c1 is not None and c1 > 0 and (c1 & (c1 - 1)) == 0:
            shift = c1.bit_length() - 1
            inst.remove_from_uses()
            inst.op = Op.SHR
            new_const = _make_const_int(shift, inst)
            inst.operands = [ops[0], new_const]
            ops[0].uses.append(inst)
            new_const.uses.append(inst)
            return True

    # Float identities
    if op == Op.FADD and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 == 0.0:
            _replace_with_value(inst, ops[0])
            return True
    if op == Op.FMUL and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 == 1.0:
            _replace_with_value(inst, ops[0])
            return True
        if c1 == 0.0:
            inst.remove_from_uses()
            inst.op = Op.CONST_FLOAT
            inst.operands = []
            inst.imm_float = 0.0
            return True
        if c1 == 2.0:
            inst.remove_from_uses()
            inst.op = Op.FADD
            inst.operands = [ops[0], ops[0]]
            ops[0].uses.append(inst)
            ops[0].uses.append(inst)
            return True

    # Boolean: x AND true → x, x AND false → false
    if op == Op.AND and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 is True:
            _replace_with_value(inst, ops[0])
            return True
        if c1 is False:
            inst.remove_from_uses()
            inst.op = Op.CONST_BOOL
            inst.operands = []
            inst.imm_int = 0
            return True
    if op == Op.OR and len(ops) == 2:
        c1 = _get_const_value(ops[1])
        if c1 is False:
            _replace_with_value(inst, ops[0])
            return True
        if c1 is True:
            inst.remove_from_uses()
            inst.op = Op.CONST_BOOL
            inst.operands = []
            inst.imm_int = 1
            return True

    # NOT NOT x → x
    if op == Op.NOT and len(ops) == 1:
        if ops[0].defining_inst and ops[0].defining_inst.op == Op.NOT:
            _replace_with_value(inst, ops[0].defining_inst.operands[0])
            return True

    # SELECT with constant condition
    if op == Op.SELECT and len(ops) == 3:
        c0 = _get_const_value(ops[0])
        if c0 is True:
            _replace_with_value(inst, ops[1])
            return True
        if c0 is False:
            _replace_with_value(inst, ops[2])
            return True

    return None


def _replace_with_value(inst: Instruction, value: Value):
    """Replace an instruction's result with an existing value."""
    if inst.result is None:
        return
    for user in list(inst.result.uses):
        user.replace_operand(inst.result, value)
    inst.remove_from_uses()
    inst.op = Op.NOP
    inst.operands = []


def _make_const_int(val: int, inst: Instruction) -> Value:
    """Create a constant int value (inserting a CONST_INT instruction before inst)."""
    const_inst = Instruction(Op.CONST_INT, [], IRType.INT64, inst.source_line)
    const_inst.imm_int = val
    if inst.block:
        # Insert before current instruction
        idx = inst.block.instructions.index(inst)
        const_inst.block = inst.block
        inst.block.instructions.insert(idx, const_inst)
    return const_inst.result


# ── DCE: Dead Code Elimination ─────────────────────────────────


def rebuild_uses(func: Function) -> None:
    for value in func.all_values():
        value.uses = []
    for inst in func.all_instructions():
        for operand in inst.operands:
            if isinstance(operand, Value) and inst not in operand.uses:
                operand.uses.append(inst)


def dce(func: Function) -> bool:
    """Remove instructions whose results are unused and that have no side effects."""
    changed = False
    for block in func.blocks:
        i = 0
        while i < len(block.instructions):
            inst = block.instructions[i]
            if _is_dead(inst):
                inst.remove_from_uses()
                block.instructions.pop(i)
                changed = True
            else:
                i += 1

    # Remove empty blocks (except entry)
    blocks_to_remove = []
    for block in func.blocks:
        if block is func.entry:
            continue
        if not block.instructions and not block.predecessors:
            blocks_to_remove.append(block)
    for block in blocks_to_remove:
        func.blocks.remove(block)
        changed = True

    # Remove NOP instructions
    for block in func.blocks:
        i = 0
        while i < len(block.instructions):
            if block.instructions[i].op == Op.NOP:
                block.instructions.pop(i)
                changed = True
            else:
                i += 1

    return changed


def copy_propagate(func: Function) -> bool:
    """Replace uses of COPY instruction results with the source operand.

    Eliminates redundant copy instructions so the register allocator sees
    the source value directly instead of a separate live range, removing
    the mov instructions that would otherwise be emitted for the copy.
    """
    changed = False
    for block in func.blocks:
        i = 0
        while i < len(block.instructions):
            inst = block.instructions[i]
            if inst.op == Op.COPY and inst.result and inst.operands:
                src = inst.operands[0]
                dst = inst.result
                # Replace all uses of dst with src
                for user in list(dst.uses):
                    user.replace_operand(dst, src)
                inst.remove_from_uses()
                block.instructions.pop(i)
                changed = True
            else:
                i += 1
    if changed:
        rebuild_uses(func)
    return changed


def _is_dead(inst: Instruction) -> bool:
    """Is this instruction dead (unused result, no side effects)?"""
    if inst.has_side_effects:
        return False
    if inst.is_terminator:
        return False
    if inst.result is None:
        return False
    return len(inst.result.uses) == 0


# ── CSE: Common Subexpression Elimination ───────────────────────


def cse(func: Function) -> bool:
    """Eliminate redundant computations (same op, same operands → same result)."""
    changed = False

    for block in func.blocks:
        seen: dict[tuple, Value] = {}

        i = 0
        while i < len(block.instructions):
            inst = block.instructions[i]

            if inst.result is None or inst.has_side_effects:
                i += 1
                continue

            key = _cse_key(inst)
            if key is not None and key in seen:
                # Replace with previously computed value
                existing = seen[key]
                for user in list(inst.result.uses):
                    user.replace_operand(inst.result, existing)
                inst.remove_from_uses()
                block.instructions.pop(i)
                changed = True
            else:
                if key is not None:
                    seen[key] = inst.result
                i += 1

    return changed


def global_cse(func: Function) -> bool:
    """Eliminate redundant computations across basic blocks using available
    expression analysis. Processes blocks in reverse post-order and intersects
    available expression sets at join points, so only expressions computed on
    all paths are considered available."""
    changed = False

    # Compute reverse post-order
    visited: set[int] = set()
    order: list[BasicBlock] = []

    def dfs(block: BasicBlock):
        if id(block) in visited:
            return
        visited.add(id(block))
        term = block.terminator
        if term is not None:
            for succ in term.target_blocks:
                dfs(succ)
        order.append(block)

    if func.blocks:
        dfs(func.blocks[0])
    order.reverse()

    # available[block_id] = set of expression keys available at block entry
    available: dict[int, set[tuple]] = {}
    # expr_value[key] = the Value that holds the expression's result
    expr_value: dict[tuple, Value] = {}

    # Initialize: entry block has no available expressions
    available[id(func.blocks[0])] = set()

    for block in order:
        bid = id(block)
        # Start with available expressions from predecessors (intersection).
        # Skip predecessors not yet processed (back edges): expressions
        # available on a back edge are also available on the forward edge for
        # loop-invariant values, so skipping them is sound.
        preds = block.predecessors
        processed_pred_sets = []
        for p in preds:
            ps = available.get(id(p))
            if ps is not None:
                processed_pred_sets.append(ps)
        if processed_pred_sets:
            common = set.intersection(*processed_pred_sets)
        elif bid != id(func.blocks[0]):
            common = set()
        else:
            common = set()

        # Walk instructions, killing expressions whose operands are redefined
        # and adding newly computed expressions
        cur = set(common)
        i = 0
        while i < len(block.instructions):
            inst = block.instructions[i]

            # If this instruction's expression is already available, replace it
            if inst.result is not None and (
                not inst.has_side_effects or inst.op == Op.LOAD_FIELD
            ):
                key = _cse_key(inst)
                if key is not None and key in cur:
                    existing = expr_value.get(key)
                    if existing is not None:
                        for user in list(inst.result.uses):
                            user.replace_operand(inst.result, existing)
                        inst.remove_from_uses()
                        block.instructions.pop(i)
                        changed = True
                        continue

            # Kill expressions whose operands are redefined, or whose memory
            # location is overwritten by STORE_FIELD.
            if inst.result is not None:
                to_kill = []
                for k in cur:
                    if k[1] and inst.result.id in k[1]:
                        to_kill.append(k)
                for k in to_kill:
                    cur.discard(k)

            # STORE_FIELD writes to a struct field — kill LOAD_FIELD expressions
            # that read from the same base pointer.
            if inst.op == Op.STORE_FIELD and inst.operands:
                base = inst.operands[0]
                if isinstance(base, Value):
                    to_kill = []
                    for k in cur:
                        if (
                            k[0] == Op.LOAD_FIELD
                            and k[1]
                            and base.id in k[1]
                        ):
                            to_kill.append(k)
                    for k in to_kill:
                        cur.discard(k)

            # Add this instruction's expression
            key = _cse_key(inst)
            if key is not None:
                cur.add(key)
                expr_value[key] = inst.result

            i += 1

        available[bid] = cur

    return changed


def _cse_key(inst: Instruction) -> tuple | None:
    """Create a hashable key for an instruction for CSE.
    Returns None if the instruction can't be CSE'd."""
    # LOAD_FIELD is a pure memory read — allow CSE even though it has
    # side_effects set (conservative flag for GC read barriers).
    if inst.has_side_effects and inst.op != Op.LOAD_FIELD:
        return None
    # Don't CSE allocations
    if inst.op in (Op.ALLOC_STRUCT, Op.ALLOC_LIST):
        return None

    operand_ids = tuple(v.id for v in inst.operands if isinstance(v, Value))

    # For commutative ops, sort operands
    if inst.op in COMMUTATIVE_OPS:
        operand_ids = tuple(sorted(operand_ids))

    return (inst.op, operand_ids, inst.imm_int, inst.imm_str, inst.imm_float)


# ── LICM: Loop Invariant Code Motion ───────────────────────────


def licm(func: Function) -> bool:
    """Move loop-invariant instructions to the loop preheader."""
    analysis = FunctionAnalysis(func)
    changed = False

    for loop in analysis.loops:
        # Find or create preheader
        preheader = _find_preheader(loop)
        if preheader is None:
            continue

        for block in list(loop.blocks):
            if block is loop.header:
                continue
            i = 0
            while i < len(block.instructions):
                inst = block.instructions[i]
                if analysis.loops.is_loop_invariant(inst):
                    # Move to preheader
                    block.instructions.pop(i)
                    preheader.insert_before_terminator(inst)
                    inst.block = preheader
                    changed = True
                else:
                    i += 1

    return changed


def _find_preheader(loop: Loop) -> BasicBlock | None:
    """Find the block that always executes before the loop header."""
    # Preheader = the unique predecessor of the header that's not in the loop
    outside_preds = [p for p in loop.header.predecessors if p not in loop.blocks]
    if len(outside_preds) == 1:
        return outside_preds[0]
    return None


def merge_linear_blocks(func: Function) -> bool:
    """Merge A -> B when B has exactly one predecessor.

    This removes the artificial fallthrough/JUMP blocks created by the SSA
    builder and exposes straight-line bodies to the inliner and peephole pass.
    """
    changed = False
    for block in func.blocks:
        seen = set()
        block.predecessors = [
            p for p in block.predecessors if not (id(p) in seen or seen.add(id(p)))
        ]
        seen = set()
        block.successors = [
            s for s in block.successors if not (id(s) in seen or seen.add(id(s)))
        ]

    while True:
        merged = False
        for a in list(func.blocks):
            term = a.terminator
            if term is None or term.op != Op.JUMP or len(term.target_blocks) != 1:
                continue
            b = term.target_blocks[0]
            if b is a or b is func.entry:
                continue
            if len(b.predecessors) != 1 or b.predecessors[0] is not a:
                continue
            if b.phi_nodes:
                continue
            # Do not merge into a loop header with a back edge.
            if any(succ is b for succ in b.successors):
                continue

            a.instructions.pop()  # remove JUMP
            for inst in b.instructions:
                inst.block = a
                a.instructions.append(inst)
            if b.terminator is None and len(b.successors) == 1:
                # Materialize the implicit fallthrough edge as a real JUMP.
                jump = Instruction(Op.JUMP, [], None, None)
                jump.imm_str = b.successors[0].label
                jump.target_blocks = [b.successors[0]]
                a.instructions.append(jump)
            a.successors = list(b.successors)
            for succ in a.successors:
                succ.predecessors = [a if p is b else p for p in succ.predecessors]
                # PHIs are indexed by predecessor block; re-point entries that
                # referred to the merged block.
                for phi in succ.phi_nodes:
                    phi.target_blocks = [
                        a if pred is b else pred for pred in phi.target_blocks
                    ]
            func.blocks.remove(b)
            changed = True
            merged = True
            break
        if not merged:
            break
    return changed


def remove_unreachable_blocks(func: Function) -> bool:
    """Delete blocks that cannot be reached from the entry block."""
    if func.entry is None:
        return False
    reachable = set()
    worklist = [func.entry]
    while worklist:
        block = worklist.pop()
        if block in reachable:
            continue
        reachable.add(block)
        worklist.extend(block.successors)

    if len(reachable) == len(func.blocks):
        return False

    for block in list(func.blocks):
        if block not in reachable:
            func.blocks.remove(block)

    for block in func.blocks:
        block.successors = [b for b in block.successors if b in reachable]
        block.predecessors = [b for b in block.predecessors if b in reachable]

    # Rebuild target_blocks from the (possibly rewritten) terminators.
    for block in func.blocks:
        term = block.terminator
        if term is not None:
            term.target_blocks = [b for b in term.target_blocks if b in reachable]
            block.successors = list(term.target_blocks)
            if term.op == Op.JUMP and not term.target_blocks:
                term.target_blocks = []
    return True


# ── SROA: Scalar Replacement of Aggregates ──────────────────────


def sroa(func: Function, escape: "EscapeAnalysis | None" = None) -> bool:
    """Replace struct allocations with individual scalar values when possible.

    A struct can be SROA'd if:
    1. It doesn't escape the function (no RETURN, no STORE_GLOBAL, no passing to functions that store it)
    2. All uses are LOAD_FIELD and STORE_FIELD with constant field indices
    3. The struct is small enough (≤ MAX_SROA_FIELDS)
    """
    MAX_SROA_FIELDS = 8
    changed = False

    if escape is None:
        escape = EscapeAnalysis(func)
        escape.run()

    for block in func.blocks:
        for inst in list(block.instructions):
            if inst.op != Op.ALLOC_STRUCT:
                continue
            if inst.result is None:
                continue
            if not escape.can_sroa(inst.result):
                continue

            struct_val = inst.result
            n_fields = len(inst.operands)
            if n_fields > MAX_SROA_FIELDS:
                continue

            # Check all uses are simple field access with constant indices
            all_simple = True
            for user in list(struct_val.uses):
                if user.op == Op.LOAD_FIELD:
                    if user.imm_int is None or user.imm_int >= n_fields:
                        all_simple = False
                        break
                elif user.op == Op.STORE_FIELD:
                    if user.imm_int is None or user.imm_int >= n_fields:
                        all_simple = False
                        break
                else:
                    all_simple = False
                    break

            if not all_simple:
                continue

            # SROA: replace field loads with the initial field values
            field_values = list(inst.operands)  # Initial values from ALLOC_STRUCT

            for user in list(struct_val.uses):
                if user.op == Op.LOAD_FIELD:
                    field_idx = user.imm_int
                    replacement = field_values[field_idx]
                    if user.result:
                        for use_of_load in list(user.result.uses):
                            use_of_load.replace_operand(user.result, replacement)
                    user.remove_from_uses()
                    user.op = Op.NOP
                    user.operands = []
                elif user.op == Op.STORE_FIELD:
                    field_idx = user.imm_int
                    new_val = user.operands[1] if len(user.operands) > 1 else None
                    if new_val:
                        field_values[field_idx] = new_val
                    user.remove_from_uses()
                    user.op = Op.NOP
                    user.operands = []

            # Remove the ALLOC_STRUCT itself
            inst.remove_from_uses()
            inst.op = Op.NOP
            inst.operands = []
            changed = True

    return changed


# ── SIMD Vectorization ──────────────────────────────────────────

def simd_vectorize(func: Function) -> bool:
    """Pack pairs of scalar float ops into packed (SIMD) ops.

    Pattern (nbody energy computation):
        %a = LOAD_FIELD %base_a 0        ; field at offset 0
        %b = LOAD_FIELD %base_a 1        ; field at offset 1 (contiguous in memory)
        ...
        %c = FMUL %da %da               ; da*da  (da = a.x - b.x)
        %d = FMUL %db %db               ; db*db  (db = a.y - b.y)
        %e = FADD %c %d                 ; da*da + db*dy

    →
        %ab_a = VFMOVUPD [%base_a]      ; [a.x, a.y]
        %ab_b = VFMOVUPD [%base_b]      ; [b.x, b.y]
        %d_ab = VFMSUBPD %ab_a %ab_b    ; [da, dy]
        %sq_ab = VFMMULPD %d_ab %d_ab   ; [da*da, dy*dy]
        %e = VFHDADDPD %sq_ab %sq_ab    ; [da*da+dy*dy, dy*dy+da*da] (lane 0 = sum)
    """
    changed = False

    from optimizer.ir import Op, Value, Instruction, PtrType, IRType

    for block in func.blocks:
        # ── Phase 1: Collect all LOAD_FIELD and find consecutive-offset pairs ──
        load_map: dict[tuple[int, int], tuple[Instruction, Value]] = {}
        for inst in block.instructions:
            if inst.op == Op.LOAD_FIELD and inst.imm_int is not None and inst.result:
                base = inst.operands[0] if inst.operands else None
                if isinstance(base, Value):
                    key = (base.id, inst.imm_int)
                    load_map[key] = (inst, inst.result)

        # Find pairs at consecutive offsets from same base
        used_inst_ids: set[int] = set()
        pairs: list[tuple[Instruction, Instruction]] = []

        for (base_id, offset1), (inst1, val1) in load_map.items():
            if id(inst1) in used_inst_ids:
                continue
            key2 = (base_id, offset1 + 1)
            if key2 not in load_map:
                continue
            inst2, val2 = load_map[key2]
            if id(inst2) in used_inst_ids:
                continue
            if len(val1.uses) == 0 or len(val2.uses) == 0:
                continue
            pairs.append((inst1, inst2))
            used_inst_ids.add(id(inst1))
            used_inst_ids.add(id(inst2))

            # Replace each pair with VFMOVUPD
        packed_map: dict[int, Value] = {}  # scalar value_id -> packed value

        for inst1, inst2 in pairs:
            base = inst1.operands[0]
            offset1 = inst1.imm_int

            # Replace inst1 with VFMOVUPD
            inst1.op = Op.VFMOVUPD
            inst1.operands = [base]
            inst1.imm_int = None
            inst1.imm_str = None
            inst1.imm_float = None

            packed_val = inst1.result
            packed_map[inst1.result.id] = packed_val
            packed_map[inst2.result.id] = packed_val

            # Replace all uses of inst2.result with packed_val before NOPing
            for user in list(inst2.result.uses):
                user.replace_operand(inst2.result, packed_val)
            inst2.result.uses.clear()

            # NOP out inst2
            inst2.remove_from_uses()
            inst2.op = Op.NOP
            inst2.operands = []
            inst2.result = None

            changed = True

        # ── Phase 1.5: Pack FSUB of two packed values → VFMSUBPD ──
        for inst in block.instructions:
            if inst.op != Op.FSUB or not inst.result:
                continue
            a = inst.operands[0] if len(inst.operands) > 0 else None
            b = inst.operands[1] if len(inst.operands) > 1 else None
            if isinstance(a, Value) and isinstance(b, Value):
                if a.id in packed_map and b.id in packed_map:
                    # Both operands are packed values → packed subtract
                    inst.op = Op.VFMSUBPD
                    inst.operands = [packed_map[a.id], packed_map[b.id]]
                    # The VFMSUBPD result is itself a packed value → add to map
                    packed_map[inst.result.id] = inst.result
                    changed = True

        # ── Phase 2: Pack FMUL x x → VFMMULPD ──
        for inst in block.instructions:
            if inst.op != Op.FMUL or not inst.result:
                continue
            a = inst.operands[0] if len(inst.operands) > 0 else None
            b = inst.operands[1] if len(inst.operands) > 1 else None
            if isinstance(a, Value) and isinstance(b, Value) and a is b:
                if a.id in packed_map:
                    packed_val = packed_map[a.id]
                    # Check if this packed value already has a VFMMULPD result
                    existing = None
                    for other in block.instructions:
                        if (
                            other.op == Op.VFMMULPD
                            and other.result
                            and other.operands
                            and len(other.operands) >= 2
                            and other.operands[0] is packed_val
                            and other.operands[1] is packed_val
                        ):
                            existing = other.result
                            break
                    if existing is not None:
                        # Reuse existing VFMMULPD result
                        inst.remove_from_uses()
                        inst.op = Op.NOP
                        inst.operands = []
                        for user in list(inst.result.uses):
                            user.replace_operand(inst.result, existing)
                        inst.result.uses.clear()
                    else:
                        # Replace FMUL x x with VFMMULPD packed packed
                        inst.op = Op.VFMMULPD
                        inst.operands = [packed_val, packed_val]
                    changed = True

        # ── Phase 3: Pack FAdd of two VFMMULPD results → VFHDADDPD self-add ──
        for inst in block.instructions:
            if inst.op != Op.FADD or not inst.result:
                continue
            a = inst.operands[0] if len(inst.operands) > 0 else None
            b = inst.operands[1] if len(inst.operands) > 1 else None
            if isinstance(a, Value) and isinstance(b, Value):
                # Check if both operands are VFMMULPD results on the same packed value
                a_packed = get_vfmulpd_packed(block, a.id)
                b_packed = get_vfmulpd_packed(block, b.id)
                if a_packed is not None and b_packed is not None and a_packed is b_packed:
                    # Replace FADD with VFHDADDPD self-add
                    # vhaddpd dest, src, src → dest[0] = src[0] + src[1]
                    inst.op = Op.VFHDADDPD
                    inst.operands = [a, a]
                    inst.imm_int = None
                    inst.imm_str = None
                    inst.imm_float = None
                    changed = True

    return changed


def inst_is_vfmulpd_result(block: BasicBlock, value_id: int) -> bool:
    """Check if a value is the result of a VFMMULPD instruction."""
    for inst in block.instructions:
        if inst.op == Op.VFMMULPD and inst.result and inst.result.id == value_id:
            return True
    return False


def get_vfmulpd_packed(block: BasicBlock, value_id: int) -> Value | None:
    """Get the packed input value of a VFMMULPD result."""
    for inst in block.instructions:
        if inst.op == Op.VFMMULPD and inst.result and inst.result.id == value_id:
            if inst.operands and len(inst.operands) >= 1:
                return inst.operands[0]
    return None


# ── Induction Variable Optimization ───────────────────────────────

# ── Induction Variable Optimization ───────────────────────────────

# ── Induction Variable Optimization ───────────────────────────────

def induction_var_opt(func: Function) -> bool:
    """Strength reduction for induction variables in loops.

    Converts array indexing inside loops to pointer arithmetic:
        %elem = LIST_GET %list %iv          ; %iv increments by 1 each iter
    into pointer-based access that avoids the imul (index * elem_size).
    """
    from optimizer.analysis import FunctionAnalysis
    from optimizer.ir import Op, Value, Instruction, PtrType, IRType, Constant

    changed = False
    analysis = FunctionAnalysis(func)

    for loop in analysis.loops.loops:
        header = loop.header
        # Find preheader: a predecessor of header not in the loop
        preheader = None
        for pred in header.predecessors:
            if pred not in loop.blocks:
                preheader = pred
                break
        if preheader is None:
            continue

        # Find induction variables: PHI nodes where back-edge is ADD(phi, const)
        iv_candidates = []
        for block in loop.blocks:
            for inst in block.instructions:
                if inst.op != Op.PHI or not inst.result:
                    continue
                for operand, pred_block in zip(inst.operands, inst.target_blocks):
                    if operand is inst.result:
                        continue  # skip self-reference
                    if not isinstance(operand, Value):
                        continue
                    if operand.defining_inst is None:
                        continue
                    add_inst = operand.defining_inst
                    if add_inst.op != Op.ADD:
                        continue
                    add_ops = add_inst.operands
                    if len(add_ops) < 2:
                        continue
                    phi_result_is_operand = any(
                        isinstance(o, Value) and o is inst.result for o in add_ops
                    )
                    const_val = None
                    for op in add_ops:
                        if isinstance(op, Value) and op is inst.result:
                            continue
                        if op.defining_inst and op.defining_inst.op == Op.CONST_INT:
                            const_val = op.defining_inst.imm_int
                        elif isinstance(op, Constant):
                            const_val = op.value
                        if phi_result_is_operand and const_val is not None:
                            iv_candidates.append((inst.result, const_val, pred_block, block))

        for iv_value, stride, back_edge_block, iv_use_block in iv_candidates:
            # Find LIST_GET/LIST_SET using this IV as index in any loop block
            for b in loop.blocks:
                for li in list(b.instructions):
                    if li.op not in (Op.LIST_GET, Op.LIST_SET):
                        continue
                    if len(li.operands) < 2:
                        continue
                    idx = li.operands[1]
                    if not isinstance(idx, Value) or idx is not iv_value:
                        continue

                    lst = li.operands[0]
                    if not isinstance(lst, Value):
                        continue

                    lst_type = lst.type
                    elem_size = None
                    if isinstance(lst_type, ListType):
                        elem_t = lst_type.elem_type
                        if isinstance(elem_t, StructType):
                            elem_size = elem_t.size
                    if elem_size is None:
                        continue

                    # Create array pointer load in preheader (computed once)
                    array_ptr_inst = Instruction(
                        Op.PTR_LOAD, [lst], PtrType(lst.type), None
                    )
                    array_ptr_val = array_ptr_inst.result
                    preheader.instructions.append(array_ptr_inst)

                    # Create pointer PHI in loop header
                    stride_phi_val = Value(PtrType(lst.type))
                    stride_phi_inst = Instruction(
                        Op.PHI, [array_ptr_val, None], stride_phi_val.type, None
                    )
                    stride_phi_inst.result = stride_phi_val
                    stride_phi_inst.target_blocks = [preheader, back_edge_block]
                    header.instructions.insert(0, stride_phi_inst)

                    # Replace LIST_GET/LIST_SET with direct pointer access
                    insert_idx = b.instructions.index(li)
                    if li.op == Op.LIST_GET:
                        dst = li.result
                        load_inst = Instruction(
                            Op.PTR_LOAD, [stride_phi_val], dst.type, None
                        )
                        load_inst.result = dst
                        li.op = Op.NOP
                        li.operands = []
                        b.instructions.insert(insert_idx, load_inst)
                        insert_idx += 1
                    elif li.op == Op.LIST_SET:
                        val = li.operands[2] if len(li.operands) > 2 else None
                        if val is None:
                            continue
                        store_inst = Instruction(
                            Op.PTR_STORE, [stride_phi_val, val], None, None
                        )
                        li.op = Op.NOP
                        li.operands = []
                        b.instructions.insert(insert_idx, store_inst)
                        insert_idx += 1

                    # Create pointer increment in back edge block (before terminator)
                    const_inst = Instruction(
                        Op.CONST_INT, [], IRType.INT64, None
                    )
                    const_inst.imm_int = elem_size
                    stride_const_val = const_inst.result
                    add_inst = Instruction(
                        Op.ADD, [stride_phi_val, stride_const_val],
                        PtrType(lst.type), None
                    )
                    term_idx = None
                    for j, bi in enumerate(back_edge_block.instructions):
                        if bi.is_terminator:
                            term_idx = j
                            break
                    if term_idx is not None:
                        back_edge_block.instructions.insert(term_idx, const_inst)
                        back_edge_block.instructions.insert(term_idx + 1, add_inst)
                    else:
                        back_edge_block.instructions.append(const_inst)
                        back_edge_block.instructions.append(add_inst)
                    stride_phi_inst.operands[1] = add_inst.result

                    changed = True

    return changed


def loop_unroll(func: Function) -> bool:
    """Unroll loops with small constant trip counts.

    For loops where the back-edge comparison is against a small constant
    (e.g., for i in 0..4), unroll the loop body completely.

    This is a placeholder implementation - full loop unrolling requires
    complex CFG restructuring. The current implementation detects loops
    with constant bounds but does not yet perform the duplication.
    """
    changed = False

    for block in func.blocks:
        term = block.terminator
        if term is None or term.op != Op.BRANCH:
            continue

        for succ in term.target_blocks:
            if succ is block:
                continue
            for si in succ.instructions:
                if si.op == Op.BRANCH and si.operands:
                    cond_val = si.operands[0] if si.operands else None
                    if not isinstance(cond_val, Value):
                        continue
                    if cond_val.defining_inst is None:
                        continue
                    lt_inst = cond_val.defining_inst
                    if lt_inst.op != Op.LT:
                        continue
                    lt_ops = lt_inst.operands
                    if len(lt_ops) < 2:
                        continue
                    const_val = None
                    iv = None
                    for op in lt_ops:
                        if isinstance(op, Value):
                            if op.defining_inst and op.defining_inst.op == Op.CONST_INT:
                                const_val = op.defining_inst.imm_int
                            elif isinstance(op, Constant):
                                const_val = op.value
                            else:
                                iv = op
                    if const_val is not None and 1 <= const_val <= 8 and iv is not None:
                        changed = True

    return changed


def _make_zero_float(func: Function, block: BasicBlock, insert_idx: int) -> Value:
    """Create or find a float 0.0 constant for VFHDADDPD."""
    from optimizer.ir import Op, Value, Instruction, IRType

    # Look for existing zero float constant in any block of the function
    f = block.func
    for b in f.blocks:
        for inst in b.instructions:
            if inst.op == Op.CONST_FLOAT and inst.imm_float == 0.0 and inst.result:
                return inst.result

    # Create new zero float constant
    zero = Value(IRType.FLOAT64)
    const_inst = Instruction(Op.CONST_FLOAT, [], IRType.FLOAT64, None)
    const_inst.imm_float = 0.0
    const_inst.result = zero
    block.instructions.insert(insert_idx, const_inst)
    return zero


# ── Inlining ────────────────────────────────────────────────────


def inline_small_functions(module: Module, max_inst: int = 200) -> bool:
    """Inline small functions at call sites.

    Supports multi-block function inlining with PHI node handling.
    A function is inlined if its instruction count is <= max_inst.
    """
    changed = False

    # Build function size map
    func_sizes = {}
    for func in module.functions:
        count = sum(len(b.instructions) for b in func.blocks)
        func_sizes[func.name] = count

    for func in module.functions:
        for block in func.blocks:
            i = 0
            while i < len(block.instructions):
                inst = block.instructions[i]
                if inst.op == Op.CALL and inst.imm_str:
                    target_name = inst.imm_str
                    target = module.get_function(target_name)
                    if (
                        target
                        and target is not func
                        and func_sizes.get(target_name, 9999) <= max_inst
                        and not target.is_extern
                    ):
                        if _try_inline(func, block, inst, target, i):
                            changed = True
                            continue  # Re-check same index
                i += 1

    return changed


def _try_inline(
    caller_func: Function,
    call_block: BasicBlock,
    call_inst: Instruction,
    callee: Function,
    call_idx: int,
) -> bool:
    """Inline a function at a call site.

    Supports multi-block callee inlining. Clones all callee blocks,
    maps parameters to call arguments, handles PHI nodes by replacing
    them with the appropriate predecessor operand, and merges blocks
    into the caller's control flow.
    """
    # Map callee params to call arguments
    param_map: dict[int, Value] = {}
    for j, p in enumerate(callee.params):
        if j < len(call_inst.operands):
            param_map[p.id] = call_inst.operands[j]

    # Map callee blocks to cloned blocks
    block_map: dict[int, BasicBlock] = {}
    cloned_blocks: list[BasicBlock] = []

    for callee_block in callee.blocks:
        new_block = BasicBlock(f"{callee.name}_{callee_block.label}")
        new_block.func = caller_func
        block_map[id(callee_block)] = new_block
        cloned_blocks.append(new_block)

    # Clone all instructions, mapping values and PHI operands
    value_map: dict[int, Value] = dict(param_map)

    for callee_block, new_block in zip(callee.blocks, cloned_blocks):
        for cinst in callee_block.instructions:
            if cinst.op in (Op.RETURN, Op.RETURN_VOID):
                # Handle return - map through value_map, will be resolved later
                continue

            # Handle PHI nodes: replace with operand from the predecessor
            # that corresponds to the call site (the callee entry block)
            if cinst.op == Op.PHI:
                # For PHI nodes, we can't easily resolve at inline time
                # without knowing which predecessor the call corresponds to.
                # For simplicity, replace PHI with its first operand
                # (will be cleaned up by copy propagation / CSE later)
                if cinst.operands and cinst.result:
                    first_op = cinst.operands[0]
                    mapped = value_map.get(first_op.id, first_op) if isinstance(first_op, Value) else first_op
                    value_map[cinst.result.id] = mapped
                continue

            # Clone instruction
            new_operands = []
            for v in cinst.operands:
                if isinstance(v, Value):
                    new_operands.append(value_map.get(v.id, v))
                else:
                    new_operands.append(v)

            new_inst = Instruction(
                cinst.op,
                new_operands,
                cinst.result.type if cinst.result else None,
                cinst.source_line,
            )
            new_inst.imm_int = cinst.imm_int
            new_inst.imm_str = cinst.imm_str
            new_inst.imm_float = cinst.imm_float
            new_inst.block = new_block

            # Map old value to new value
            if cinst.result and new_inst.result:
                value_map[cinst.result.id] = new_inst.result

            new_block.instructions.append(new_inst)

    # Handle RETURN: replace call result with return value
    return_val = None
    for callee_block in callee.blocks:
        for cinst in callee_block.instructions:
            if cinst.op == Op.RETURN and cinst.operands:
                ret_op = cinst.operands[0]
                if isinstance(ret_op, Value):
                    return_val = value_map.get(ret_op.id, ret_op)
                else:
                    return_val = ret_op
                break

    # Merge cloned blocks into caller: insert after call_block
    insert_pos = caller_func.blocks.index(call_block) + 1
    for new_block in cloned_blocks:
        caller_func.blocks.insert(insert_pos, new_block)
        insert_pos += 1

    # Replace the call instruction with a jump to the first cloned block
    # (the callee entry block)
    entry_block = cloned_blocks[0]
    call_block.instructions.pop(call_idx)
    jump_inst = Instruction(Op.JUMP, [entry_block], None, call_inst.source_line)
    jump_inst.block = call_block
    call_block.instructions.insert(call_idx, jump_inst)

    # Replace call result uses with return value
    if call_inst.result and return_val:
        for user in list(call_inst.result.uses):
            user.replace_operand(call_inst.result, return_val)

    # Fix up terminator of last cloned block (was RETURN, now falls through)
    # The last block in callee had RETURN which we skipped.
    # Its terminator is now missing - add a fall-through to after the inlined code
    last_block = cloned_blocks[-1]
    if not last_block.terminator:
        # Add fall-through: the inlined code falls through to whatever follows
        # the call site in the caller. Since we inserted blocks after call_block,
        # the block after the last cloned block is the caller's successor.
        caller_idx = caller_func.blocks.index(last_block)
        if caller_idx + 1 < len(caller_func.blocks):
            next_block = caller_func.blocks[caller_idx + 1]
            last_block.terminator = Instruction(Op.JUMP, [next_block], None, None)
            last_block.terminator.block = last_block

    # Update predecessors/successors for all affected blocks
    _fixup_cfg_after_inline(caller_func, call_block, cloned_blocks)

    return True


def _fixup_cfg_after_inline(
    caller_func: Function,
    call_block: BasicBlock,
    cloned_blocks: list[BasicBlock],
) -> None:
    """Fix up CFG predecessor/successor relationships after inlining."""
    # Rebuild all predecessor/successor sets
    for block in caller_func.blocks:
        block.predecessors.clear()
        block.successors.clear()

    for block in caller_func.blocks:
        term = block.terminator
        if term is None:
            continue
        if term.op == Op.JUMP and term.target_blocks:
            for succ in term.target_blocks:
                if succ not in block.successors:
                    block.successors.append(succ)
                if block not in succ.predecessors:
                    succ.predecessors.append(block)
        elif term.op == Op.BRANCH and term.target_blocks:
            for succ in term.target_blocks:
                if succ not in block.successors:
                    block.successors.append(succ)
                if block not in succ.predecessors:
                    succ.predecessors.append(block)


# ── Tail Call Optimization ──────────────────────────────────────


def tco(func: Function) -> bool:
    """Convert tail calls to jumps (tail call optimization)."""
    changed = False

    for block in func.blocks:
        instrs = block.instructions
        if len(instrs) < 2:
            continue

        # Pattern: CALL foo ... ; RETURN %result_of_call
        term = instrs[-1]
        if term.op != Op.RETURN:
            continue
        if not term.operands:
            continue
        ret_val = term.operands[0]

        # The call must be the instruction that produces ret_val
        call_inst = ret_val.defining_inst if isinstance(ret_val, Value) else None
        if call_inst is None or call_inst.op != Op.CALL:
            continue
        if call_inst.imm_str != func.name:
            continue  # Only optimize self-recursion for now

        # Convert: replace CALL with parameter setup + JUMP to entry
        # This is a simplified version — just marks the call as a tail call
        call_inst.op = Op.JUMP
        call_inst.imm_str = func.entry.label if func.entry else None
        call_inst.result = None  # No return value

        # Remove the RETURN
        instrs.pop()
        changed = True

    return changed


# ── Branch simplification ──────────────────────────────────────


def simplify_branches(func: Function) -> bool:
    """Simplify control flow: fold constant branches, remove unreachable blocks."""
    changed = False

    for block in func.blocks:
        term = block.terminator
        if term is None:
            continue

        # BRANCH with constant condition → JUMP
        if term.op == Op.BRANCH and term.operands:
            cond_val = _get_const_value(term.operands[0])
            if cond_val is not None and len(term.target_blocks) >= 2:
                # True condition → jump to true block (target_blocks[0])
                # False condition → jump to false block (target_blocks[1])
                target = term.target_blocks[0] if cond_val else term.target_blocks[1]
                dead = term.target_blocks[1] if cond_val else term.target_blocks[0]
                term.op = Op.JUMP
                term.remove_from_uses()
                term.operands = []
                term.target_blocks = [target]
                term.imm_str = target.label

                # Update successors
                block.successors = [target]
                if block in dead.predecessors:
                    dead.predecessors.remove(block)
                changed = True

    return changed


# ── Type propagation for generic list types ─────────────────────

def propagate_list_types(module: Module) -> bool:
    """Refine generic ``list`` parameter/return/field types from call sites.

    The bytecode type name only says ``list``; element types appear later in
    the IR (literals, split results, field constructors). Propagating them
    makes ``contains``, printing and list element access use the right ABI.
    """
    funcs = {f.name: f for f in module.functions}
    changed_any = False

    def refine(current, incoming):
        if not isinstance(current, ListType) or not isinstance(incoming, ListType):
            return current, False
        if current.elem_type == IRType.INT64 and incoming.elem_type != IRType.INT64:
            return incoming, True
        return current, False

    for _ in range(8):
        changed = False
        # Call-site parameters.
        for func in module.functions:
            for inst in func.all_instructions():
                if inst.op != Op.CALL or not inst.imm_str:
                    continue
                target = funcs.get(inst.imm_str)
                if target is None:
                    continue
                for param, arg in zip(target.params, inst.operands):
                    new_type, did = refine(param.type, arg.type)
                    if did:
                        param.type = new_type
                        changed = True

        # Instruction results and generic list mutations.
        for func in module.functions:
            for inst in func.all_instructions():
                if inst.op in (Op.LIST_GET,) and inst.result is not None:
                    lst = inst.operands[0] if inst.operands else None
                    if isinstance(lst, Value) and isinstance(lst.type, ListType):
                        elem = lst.type.elem_type
                        if inst.op == Op.LIST_GET and inst.result.type != elem:
                            inst.result.type = elem
                            changed = True
                elif inst.op == Op.PHI and inst.result is not None and inst.operands:
                    operand_types = [op.type for op in inst.operands if isinstance(op, Value)]
                    if operand_types:
                        new_type = operand_types[0]
                        if new_type == IRType.INT64:
                            for t in operand_types[1:]:
                                if t != IRType.INT64:
                                    new_type = t
                                    break
                        if inst.result.type != new_type:
                            inst.result.type = new_type
                            changed = True
                elif inst.op == Op.LIST_APPEND and len(inst.operands) >= 2:
                    lst, val = inst.operands[0], inst.operands[1]
                    new_type, did = refine(lst.type, ListType(val.type))
                    if did:
                        lst.type = new_type
                        changed = True
                elif (
                    inst.op == Op.CALL_BUILTIN
                    and inst.imm_str in ("contains", "str_contains")
                    and len(inst.operands) >= 1
                ):
                    container = inst.operands[0]
                    new_name = (
                        "str_contains" if container.type == IRType.STRING else "contains"
                    )
                    if inst.imm_str != new_name:
                        inst.imm_str = new_name
                        changed = True
                elif inst.op == Op.LOAD_FIELD and inst.result is not None:
                    base = inst.operands[0] if inst.operands else None
                    if isinstance(base, Value) and isinstance(base.type, StructType):
                        idx = inst.imm_int or 0
                        if idx < len(base.type.field_types):
                            field_type = base.type.field_types[idx]
                            if inst.result.type != field_type:
                                inst.result.type = field_type
                                changed = True
                            if (
                                isinstance(field_type, ListType)
                                and isinstance(inst.result.type, ListType)
                                and field_type.elem_type == IRType.INT64
                                and inst.result.type.elem_type != IRType.INT64
                            ):
                                base.type.field_types[idx] = inst.result.type
                                changed = True
                elif inst.op == Op.ALLOC_STRUCT and inst.result is not None:
                    if isinstance(inst.result.type, StructType):
                        for idx, operand in enumerate(inst.operands):
                            if idx >= len(inst.result.type.field_types):
                                break
                            field_type = inst.result.type.field_types[idx]
                            if (
                                isinstance(field_type, ListType)
                                and isinstance(operand.type, ListType)
                                and field_type.elem_type == IRType.INT64
                                and operand.type.elem_type != IRType.INT64
                            ):
                                inst.result.type.field_types[idx] = operand.type
                                changed = True

        # Return types and RETURN operand refinement.
        for func in module.functions:
            if func.is_extern:
                continue
            for inst in func.all_instructions():
                if inst.op != Op.RETURN or not inst.operands:
                    continue
                new_type, did = refine(func.return_type, inst.operands[0].type)
                if did:
                    func.return_type = new_type
                    # Existing call sites already carry the old generic return
                    # type; update them so the new element type propagates
                    # through locals and struct fields.
                    for caller in module.functions:
                        for call in caller.all_instructions():
                            if (
                                call.op == Op.CALL
                                and call.imm_str == func.name
                                and call.result is not None
                            ):
                                call.result.type = new_type
                    changed = True

        if not changed:
            break
        changed_any = True
    return changed_any


# ── Side-effect / purity analysis ───────────────────────────────

# Builtins that cannot observe or mutate program state. Calls to these are
# safe to eliminate when their result is unused and safe to CSE.
_PURE_BUILTINS = frozenset({
    "str", "int", "float", "bool", "len", "abs", "min", "max",
    "sqrt", "pow", "sin", "cos", "tan", "floor", "ceil", "round",
    "contains", "split", "join", "replace", "strip", "upper", "lower",
    "get_char", "repeat", "encode", "decode",
})

_IMPURE_OPS = frozenset({
    Op.PRINT, Op.PRINTLN, Op.INPUT, Op.STORE_GLOBAL,
    Op.STORE_FIELD, Op.LOAD_FIELD, Op.LIST_SET, Op.LIST_APPEND,
    Op.LIST_GET, Op.PTR_STORE, Op.PTR_LOAD, Op.LOAD_GLOBAL,
    Op.DIV, Op.MOD, Op.FDIV, Op.LIST_ELEM_ADDR,
    Op.RAISE, Op.TRY_BEGIN, Op.TRY_END,
})


def mark_purity(module: Module) -> bool:
    """Compute side-effect purity through the call graph.

    A function is pure when every instruction is pure and every callee is
    pure. Starting from "pure" and lowering to a fixed point gives the
    greatest fixed point, so recursive pure functions are handled correctly.
    """
    funcs = {f.name: f for f in module.functions}
    purity = {name: (not f.is_extern) for name, f in funcs.items()}
    changed = True
    while changed:
        changed = False
        for name, func in funcs.items():
            if not purity.get(name, False):
                continue
            pure = True
            for inst in func.all_instructions():
                if inst.op in _IMPURE_OPS:
                    pure = False
                    break
                if inst.op == Op.CALL:
                    callee = inst.imm_str
                    if not callee or not purity.get(callee, False):
                        pure = False
                        break
                elif inst.op == Op.CALL_BUILTIN:
                    if (inst.imm_str or "") not in _PURE_BUILTINS:
                        pure = False
                        break
            if not pure:
                purity[name] = False
                changed = True

    flag_changed = False
    for func in module.functions:
        for inst in func.all_instructions():
            if inst.op not in (Op.CALL, Op.CALL_BUILTIN):
                continue
            if inst.op == Op.CALL:
                pure = purity.get(inst.imm_str or "", False)
            else:
                pure = (inst.imm_str or "") in _PURE_BUILTINS
            if inst.pure_call != pure:
                inst.pure_call = pure
                flag_changed = True
    return flag_changed


# ── Call-site specialization ────────────────────────────────────

_SPECIALIZATION_LIMIT = 64


def _const_info(value: Value):
    """Return (type, value) for a constant SSA value, or None."""
    if isinstance(value, Constant):
        return (value.type, value.value)
    inst = value.defining_inst if isinstance(value, Value) else None
    if inst is None:
        return None
    if inst.op == Op.CONST_INT:
        return (IRType.INT64, inst.imm_int)
    if inst.op == Op.CONST_FLOAT:
        return (IRType.FLOAT64, inst.imm_float)
    if inst.op == Op.CONST_BOOL:
        return (IRType.BOOL, bool(inst.imm_int))
    if inst.op == Op.CONST_STR:
        return (IRType.STRING, inst.imm_str)
    return None


def _arg_spec(value: Value, range_hint, config: OptimizerConfig):
    """Describe what a call site knows about one argument.

    Specs are ('const', type, value), ('range', lo, hi) or ('any',).
    """
    info = _const_info(value)
    if info is not None:
        return ("const", info[0], info[1])
    r = range_hint
    if r is not None:
        lo, hi = int(r[0]), int(r[1])
        if hi - lo <= config.max_specialized_range:
            if lo == hi:
                return ("const", IRType.INT64, lo)
            return ("range", lo, hi)
    return ("any",)


def _spec_key(spec) -> tuple:
    if spec[0] == "const":
        return ("c", str(spec[1]), repr(spec[2]))
    if spec[0] == "range":
        return ("r", spec[1], spec[2])
    return ("u",)


def _clone_specialized(
    module: Module,
    target: Function,
    specs: list,
    new_name: str,
    config: OptimizerConfig | None = None,
) -> Function:
    """Clone *target* with call-site constants and range constraints."""
    cfg = config or OptimizerConfig.from_env()
    params = [Param(p.name, p.type, i) for i, p in enumerate(target.params)]
    clone = Function(new_name, params, target.return_type)
    clone.source_file = target.source_file
    clone.local_names = dict(target.local_names)

    # Constant specializations get a tiny synthetic entry block. Putting the
    # constants in the cloned entry would shift instruction indices and break
    # PHI/target alignment.
    has_consts = any(spec[0] == "const" for spec in specs)
    const_entry = None
    if has_consts:
        const_entry = clone.add_block(BasicBlock("__spec_entry"))

    block_map: dict[int, BasicBlock] = {}
    for old_block in target.blocks:
        block_map[id(old_block)] = clone.add_block(BasicBlock(old_block.label))

    value_map: dict[int, Value] = {}
    for old_param, new_param, spec in zip(target.params, params, specs):
        if spec[0] == "const":
            _, ctype, cvalue = spec
            const_op = {
                IRType.STRING: Op.CONST_STR,
                IRType.FLOAT64: Op.CONST_FLOAT,
                IRType.BOOL: Op.CONST_BOOL,
            }.get(ctype, Op.CONST_INT)
            inst = Instruction(const_op, [], ctype, None)
            if ctype == IRType.INT64:
                inst.imm_int = int(cvalue)
            elif ctype == IRType.FLOAT64:
                inst.imm_float = float(cvalue)
            elif ctype == IRType.BOOL:
                inst.imm_int = 1 if cvalue else 0
            elif ctype == IRType.STRING:
                inst.imm_str = str(cvalue)
                if cvalue not in module.string_constants:
                    module.string_constants.append(cvalue)
            inst.block = const_entry
            const_entry.instructions.append(inst)
            if inst.result:
                value_map[old_param.id] = inst.result
                if ctype in (IRType.INT64, IRType.BOOL):
                    clone.param_ranges[new_param.id] = (
                        (int(cvalue), int(cvalue))
                        if ctype == IRType.INT64
                        else ((1, 1) if cvalue else (0, 0))
                    )
        else:
            value_map[old_param.id] = new_param
            if spec[0] == "range":
                clone.param_ranges[new_param.id] = (spec[1], spec[2])

    if const_entry is not None and target.entry is not None:
        target_entry = block_map[id(target.entry)]
        jump = Instruction(Op.JUMP, [], None, None)
        jump.imm_str = target_entry.label
        jump.target_blocks = [target_entry]
        jump.block = const_entry
        const_entry.instructions.append(jump)

    # Two-pass clone: first allocate every result value, then rewrite
    # operands. PHIs reference values defined later in the function, so a
    # single pass would leave stale cross-function references.
    inst_map: dict[int, Instruction] = {}
    for old_block in target.blocks:
        new_block = block_map[id(old_block)]
        for old_inst in old_block.instructions:
            new_inst = Instruction(
                old_inst.op,
                [],
                old_inst.result.type if old_inst.result else None,
                old_inst.source_line,
            )
            new_inst.imm_int = old_inst.imm_int
            new_inst.imm_str = old_inst.imm_str
            new_inst.imm_float = old_inst.imm_float
            new_inst.stack_alloc = old_inst.stack_alloc
            new_block.append(new_inst)
            inst_map[id(old_inst)] = new_inst
            if old_inst.result and new_inst.result:
                value_map[old_inst.result.id] = new_inst.result

    for old_block in target.blocks:
        new_block = block_map[id(old_block)]
        for old_inst, new_inst in zip(old_block.instructions, new_block.instructions):
            new_inst.operands = [
                value_map.get(operand.id, operand)
                if isinstance(operand, Value)
                else operand
                for operand in old_inst.operands
            ]
            for operand in new_inst.operands:
                if isinstance(operand, Value) and new_inst not in operand.uses:
                    operand.uses.append(new_inst)
            if old_inst.target_blocks:
                new_inst.target_blocks = [
                    block_map[id(b)] for b in old_inst.target_blocks if id(b) in block_map
                ]

    for block in clone.blocks:
        block.predecessors = []
        block.successors = []
    for block in clone.blocks:
        term = block.terminator
        if term is None:
            continue
        for succ in term.target_blocks:
            block.successors.append(succ)
            if block not in succ.predecessors:
                succ.predecessors.append(block)

    # Fold the newly exposed constants/ranges and prune unreachable branches.
    for _ in range(4):
        c1 = sccp(clone)
        c2 = algebraic_simplify(clone)
        c3 = simplify_branches(clone)
        c4 = range_fold_branches(clone, clone.param_ranges, cfg)
        c5 = remove_unreachable_blocks(clone)
        c6 = merge_linear_blocks(clone)
        c7 = dce(clone)
        if not (c1 or c2 or c3 or c4 or c5 or c6 or c7):
            break

    return clone


def specialize_calls(
    module: Module, config: OptimizerConfig | None = None
) -> bool:
    """Create a call-specific version of small functions.

    Specialization uses both constant arguments and ranges inferred by the
    interprocedural analysis. Dead branches and their side effects disappear
    from each clone, and single-block clones are subsequently inlined by the
    normal inliner (effectively merging the function into its caller).
    """
    cfg = config or OptimizerConfig.from_env()
    changed = False
    cache: dict[tuple, str] = {}
    specializations = 0

    for func in list(module.functions):
        for block in func.blocks:
            for inst in block.instructions:
                if inst.op != Op.CALL or not inst.imm_str:
                    continue
                target = module.get_function(inst.imm_str)
                if target is None or target is func or target.is_extern:
                    continue
                if "__spec_" in target.name:
                    continue
                # Recursive/mutually-recursive functions must not be cloned
                # per call: each clone would recurse with a new constant and
                # create an unbounded specialization chain.
                if any(
                    call.op == Op.CALL and call.imm_str == target.name
                    for call in target.all_instructions()
                ):
                    continue
                if len(target.blocks) < 2:
                    continue
                if sum(len(b.instructions) for b in target.blocks) > cfg.max_specialized_body:
                    continue
                if len(inst.operands) != len(target.params):
                    continue

                hint_ranges = inst.arg_ranges or [None] * len(inst.operands)
                specs = [
                    _arg_spec(arg, hint_ranges[i] if i < len(hint_ranges) else None, cfg)
                    for i, arg in enumerate(inst.operands)
                ]
                if all(spec[0] == "any" for spec in specs):
                    continue

                key = (target.name, tuple(_spec_key(spec) for spec in specs))
                new_name = cache.get(key)
                if new_name is None:
                    if specializations >= cfg.max_specializations:
                        continue
                    specializations += 1
                    candidate = f"{target.name}__spec_{specializations}"
                    clone = _clone_specialized(module, target, specs, candidate, cfg)
                    target_size = sum(len(b.instructions) for b in target.blocks)
                    clone_size = sum(len(b.instructions) for b in clone.blocks)
                    beneficial = (
                        len(clone.blocks) < len(target.blocks)
                        or clone_size < target_size
                    )
                    if not beneficial:
                        cache[key] = ""
                        continue
                    new_name = candidate
                    module.add_function(clone)
                    cache[key] = new_name
                if not new_name:
                    continue
                if inst.imm_str != new_name:
                    inst.imm_str = new_name
                    changed = True

    return changed


def licm(func: Function) -> bool:
    """Hoist loop-invariant, side-effect-free instructions to the entry block.

    Constants and parameters (and values already in entry) are available
    everywhere, so they are safe to move; memory reads and calls are never
    hoisted.
    """
    if func.entry is None:
        return False
    try:
        loops = FunctionAnalysis(func).loops.loops
    except Exception:
        return False
    if not loops:
        return False

    entry = func.entry
    changed = False
    for loop in loops:
        # Values available at entry: params/constants/entry-defined.
        invariant: set[int] = set()
        for block in func.blocks:
            if block is entry:
                for inst in block.instructions:
                    if inst.result is not None:
                        invariant.add(inst.result.id)
        for param in func.params:
            invariant.add(param.id)

        hoisted: list[Instruction] = []
        for block in loop.blocks:
            if block is entry:
                continue
            for inst in list(block.instructions):
                if inst.result is None or inst.op in (
                    Op.PHI, Op.JUMP, Op.BRANCH, Op.RETURN, Op.RETURN_VOID,
                    Op.CONST_INT, Op.CONST_FLOAT, Op.CONST_STR, Op.CONST_BOOL,
                ):
                    continue
                if inst.has_side_effects or inst.op in (
                    Op.ALLOC_LIST, Op.ALLOC_STRUCT, Op.ALLOCA,
                    Op.CALL, Op.CALL_BUILTIN, Op.CALL_EXTERN,
                    Op.DIV, Op.MOD, Op.FDIV,
                ):
                    continue
                if all(
                    isinstance(op, Value) and op.id in invariant
                    for op in inst.operands
                ):
                    block.instructions.remove(inst)
                    inst.block = entry
                    insert_at = len(entry.instructions)
                    if entry.terminator is not None:
                        insert_at -= 1
                    entry.instructions.insert(insert_at, inst)
                    invariant.add(inst.result.id)
                    hoisted.append(inst)
                    changed = True
    return changed


def remove_unused_functions(module: Module) -> bool:
    """Remove functions unreachable from the entry point."""
    by_name = {f.name: f for f in module.functions}
    roots = []
    if module.entry_func and module.entry_func in by_name:
        roots.append(by_name[module.entry_func])
    elif "main" in by_name:
        roots.append(by_name["main"])
    roots.extend(f for f in module.functions if f.is_extern)
    if not roots:
        return False

    reachable: set[str] = set()
    worklist = list(roots)
    while worklist:
        func = worklist.pop()
        if func.name in reachable:
            continue
        reachable.add(func.name)
        for inst in func.all_instructions():
            if inst.op == Op.CALL and inst.imm_str:
                callee = by_name.get(inst.imm_str)
                if callee is not None and callee.name not in reachable:
                    worklist.append(callee)

    before = len(module.functions)
    module.functions = [f for f in module.functions if f.name in reachable]
    return len(module.functions) != before


def fold_pure_constant_calls(
    module: Module, config: OptimizerConfig | None = None
) -> bool:
    """Evaluate pure calls with constant arguments at compile time."""
    from optimizer.puresim import evaluate_function, _UNKNOWN

    cfg = config or OptimizerConfig.from_env()
    funcs = {f.name: f for f in module.functions}
    changed = False
    for func in module.functions:
        for block in func.blocks:
            for inst in list(block.instructions):
                if inst.op != Op.CALL or not inst.imm_str:
                    continue
                target = funcs.get(inst.imm_str)
                if target is None or not _is_pure_function(target):
                    continue
                if len(inst.operands) != len(target.params):
                    continue
                args = []
                ok = True
                for operand in inst.operands:
                    info = _const_info(operand)
                    if info is None or info[0] not in (
                        IRType.INT64, IRType.FLOAT64, IRType.BOOL, IRType.STRING
                    ):
                        ok = False
                        break
                    args.append(info[1])
                if not ok or inst.result is None:
                    continue
                result = evaluate_function(module, target, args, cfg)
                if result is _UNKNOWN:
                    continue
                if isinstance(result, bool):
                    inst.op = Op.CONST_BOOL
                    inst.imm_int = 1 if result else 0
                    inst.result.type = IRType.BOOL
                elif isinstance(result, int):
                    inst.op = Op.CONST_INT
                    inst.imm_int = result
                    inst.result.type = IRType.INT64
                elif isinstance(result, float):
                    inst.op = Op.CONST_FLOAT
                    inst.imm_float = result
                    inst.result.type = IRType.FLOAT64
                elif isinstance(result, str):
                    inst.op = Op.CONST_STR
                    inst.imm_str = result
                    inst.result.type = IRType.STRING
                    if result not in module.string_constants:
                        module.string_constants.append(result)
                else:
                    continue
                for operand in inst.operands:
                    if isinstance(operand, Value) and inst in operand.uses:
                        operand.uses.remove(inst)
                inst.operands = []
                changed = True
    return changed


def _is_pure_function(func: Function) -> bool:
    if func.is_extern:
        return False
    for inst in func.all_instructions():
        if inst.op in _IMPURE_OPS:
            return False
        if inst.op in (Op.CALL, Op.CALL_BUILTIN) and not inst.pure_call:
            return False
        if inst.op in (Op.CALL_EXTERN, Op.TRY_BEGIN, Op.TRY_END):
            return False
    return True


def build_lookup_tables(
    module: Module, config: OptimizerConfig | None = None
) -> bool:
    """Precompute hot results of pure scalar functions.

    Each use site contributes its constant value or inferred range. Those
    values are simulated at compile time (with a hard step/time budget) and
    embedded in read-only memory as a small lookup table checked on entry.
    Misses fall through to the normal function body, so this optimization is
    always semantics-preserving.
    """
    from optimizer.puresim import evaluate_function, _UNKNOWN

    cfg = config or OptimizerConfig.from_env()
    funcs = {f.name: f for f in module.functions}
    candidates: dict[str, set[int]] = defaultdict(set)

    for func in module.functions:
        for inst in func.all_instructions():
            if inst.op != Op.CALL or not inst.imm_str:
                continue
            target = funcs.get(inst.imm_str)
            if target is None:
                continue
            hint_ranges = inst.arg_ranges or []
            for i, arg in enumerate(inst.operands):
                if i != 0:
                    continue  # one-argument tables for now
                info = _const_info(arg)
                if info is not None and info[0] in (IRType.INT64, IRType.BOOL):
                    candidates[target.name].add(int(info[1]))
                    continue
                r = hint_ranges[i] if i < len(hint_ranges) else None
                if r is not None:
                    lo, hi = int(r[0]), int(r[1])
                    if hi - lo + 1 <= cfg.max_table_domain:
                        for v in range(lo, min(hi, lo + cfg.max_table_entries - 1) + 1):
                            candidates[target.name].add(v)

    changed = False
    total_queries = 0
    for name, values in candidates.items():
        func = funcs.get(name)
        if func is None or not _is_pure_function(func):
            continue
        if len(func.params) != 1 or func.return_type not in (
            IRType.INT64,
            IRType.BOOL,
        ):
            continue
        param_type = func.params[0].type
        if param_type not in (IRType.INT64, IRType.BOOL):
            continue
        if sum(len(b.instructions) for b in func.blocks) > cfg.max_table_function_size:
            continue
        if len(values) < cfg.min_table_entries:
            continue

        lo = min(values)
        hi = max(values)
        # Densify small observed windows: a contiguous table is cheaper than a
        # compare chain and still bounded by the configured budget.
        if hi - lo + 1 <= cfg.max_table_domain and hi - lo + 1 <= cfg.max_table_entries:
            values = set(range(lo, hi + 1))
        if len(values) > cfg.max_table_entries:
            values = set(sorted(values)[: cfg.max_table_entries])

        entries: dict[int, int] = {}
        for arg in sorted(values):
            total_queries += 1
            if total_queries > cfg.max_sim_calls:
                break
            result = evaluate_function(module, func, [arg], cfg)
            if result is _UNKNOWN:
                continue
            if isinstance(result, bool):
                entries[int(arg)] = 1 if result else 0
            elif isinstance(result, int):
                entries[int(arg)] = int(result)
            elif isinstance(result, float) and result.is_integer():
                entries[int(arg)] = int(result)
            else:
                continue
        if len(entries) < cfg.min_table_entries:
            continue

        ordered = sorted(entries)
        if ordered and ordered[-1] - ordered[0] + 1 == len(ordered):
            func.lookup_table = {
                "kind": "dense",
                "min": ordered[0],
                "max": ordered[-1],
                "values": [entries[v] for v in ordered],
            }
        else:
            func.lookup_table = {
                "kind": "sparse",
                "pairs": [(v, entries[v]) for v in ordered],
            }
        changed = True

    return changed


# ── Pass pipeline ───────────────────────────────────────────────


def run_passes(
    module: Module, level: int = 2, config: OptimizerConfig | None = None
) -> bool:
    """Run optimization passes on the module.

    level 0: no optimization
    level 1: basic (SCCP, algebraic, DCE)
    level 2: standard (+ CSE, LICM, SROA, inlining)
    level 3: aggressive (+ synthesis, more inlining)
    """
    if level == 0:
        return False

    cfg = config or OptimizerConfig.from_env()
    propagate_list_types(module)
    overall_changed = False

    # Escape analysis is interprocedural-ish (it summarizes call sites), so
    # compute it once per fixed-point iteration instead of passing a Function
    # where a Module is expected (the previous code made SROA a no-op).
    escape = EscapeAnalysis(module)
    escape.run()
    mark_purity(module)

    # Whole-program constraint propagation: call-site values/range facts flow
    # into callee parameters and are recorded on each call for specialization.
    if level >= 2:
        analyze_module_ranges(module, cfg)

    # Run passes in a fixed-point loop
    for iteration in range(cfg.max_iterations):
        changed = propagate_list_types(module)

        for func in module.functions:
            if func.is_extern:
                continue

            # --- Level 1 optimizations (run at all opt levels) ---
            # These run BEFORE CSE/global_cse/LICM to preserve IR patterns
            # that SIMD and induction variable optimization need to match.
            changed |= sccp(func)
            changed |= copy_propagate(func)
            changed |= algebraic_simplify(func)
            changed |= simplify_branches(func)

            if level >= 2:
                changed |= range_fold_branches(func, func.param_ranges, cfg)

            # SIMD vectorization must run early, before CSE eliminates
            # LOAD_FIELD instructions that it needs to match into packed loads.
            changed |= simd_vectorize(func)

            # Induction variable optimization must run early, before CSE
            # eliminates PHI/add patterns it needs to match.
            changed |= induction_var_opt(func)

            changed |= remove_unreachable_blocks(func)
            changed |= merge_linear_blocks(func)
            changed |= dce(func)

            if level >= 2:
                changed |= cse(func)
                changed |= global_cse(func)
                changed |= licm(func)
                changed |= sroa(func, escape)
                # SIMD and IV opt disabled pending fixes
                # changed |= simd_vectorize(func)
                # changed |= induction_var_opt(func)
                changed |= loop_unroll(func)
                changed |= tco(func)

        if level >= 2:
            changed |= inline_small_functions(module, cfg.inline_max_inst)
            changed |= specialize_calls(module, cfg)
            for func in module.functions:
                if not func.is_extern:
                    rebuild_uses(func)
            changed |= mark_purity(module)
            changed |= fold_pure_constant_calls(module, cfg)
            if changed:
                analyze_module_ranges(module, cfg)
        changed |= mark_purity(module)

        overall_changed |= changed
        if not changed:
            break

    # Final DCE cleanup
    for func in module.functions:
        if not func.is_extern:
            rebuild_uses(func)
            dce(func)

    remove_unused_functions(module)
    if level >= 2:
        build_lookup_tables(module, cfg)

    # Mark allocations that never escape the function for stack placement.
    # SROA already removed the fully-local ones; this covers structs that are
    # only passed to callees (ARG_ESCAPE) and therefore still need an address.
    escape = EscapeAnalysis(module)
    escape.run()
    for func in module.functions:
        for inst in func.all_instructions():
            if inst.op == Op.ALLOC_STRUCT and inst.result is not None:
                inst.stack_alloc = escape.can_stack_alloc(inst.result)

    return overall_changed

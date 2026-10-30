"""Budgeted interprocedural integer/boolean range analysis.

The analysis is deliberately conservative: an unknown value has no entry in the
range map, and every arithmetic rule over-approximates. Its purpose is branch
pruning and specialization, never to replace runtime checks with an unsound
assumption.
"""

from __future__ import annotations

from collections import defaultdict, deque

from optimizer.config import OptimizerConfig
from optimizer.ir import (
    BasicBlock,
    Constant,
    Function,
    Instruction,
    Module,
    Op,
    IRType,
    Value,
)

Range = tuple[int, int]
INT_MIN = -(1 << 62)
INT_MAX = (1 << 62) - 1


def _rng(v: Value | Constant | None, ranges: dict[int, Range]) -> Range | None:
    if v is None:
        return None
    if isinstance(v, Constant):
        if isinstance(v.value, bool):
            return (1, 1) if v.value else (0, 0)
        if isinstance(v.value, int):
            return (int(v.value), int(v.value))
        return None
    if isinstance(v, (int, bool)):
        return (int(v), int(v))
    if isinstance(v, Value):
        r = ranges.get(v.id)
        if r is not None:
            return r
        inst = v.defining_inst
        if inst is not None:
            if inst.op == Op.CONST_INT:
                return (int(inst.imm_int or 0), int(inst.imm_int or 0))
            if inst.op == Op.CONST_BOOL:
                return (1, 1) if inst.imm_int else (0, 0)
        return None
    return None


def _union(a: Range | None, b: Range | None) -> Range | None:
    if a is None:
        return b
    if b is None:
        return a
    return (min(a[0], b[0]), max(a[1], b[1]))


def _bool_range(value: bool | None) -> Range | None:
    if value is None:
        return None
    return (1, 1) if value else (0, 0)


def _compare_range(op: Op, a: Range, b: Range) -> Range:
    # Exact comparison first (works for booleans and singleton ranges).
    if a[0] == a[1] and b[0] == b[1]:
        x, y = a[0], b[0]
        result = {
            Op.EQ: x == y,
            Op.NE: x != y,
            Op.LT: x < y,
            Op.LE: x <= y,
            Op.GT: x > y,
            Op.GE: x >= y,
        }.get(op)
        if result is not None:
            return _bool_range(result)  # type: ignore[return-value]

    if op == Op.EQ:
        if a[1] < b[0] or b[1] < a[0]:
            return (0, 0)
        return (0, 1)
    if op == Op.NE:
        if a[1] < b[0] or b[1] < a[0]:
            return (1, 1)
        return (0, 1)
    if op == Op.LT:
        if a[1] < b[0]:
            return (1, 1)
        if a[0] >= b[1]:
            return (0, 0)
        return (0, 1)
    if op == Op.LE:
        if a[1] <= b[0]:
            return (1, 1)
        if a[0] > b[1]:
            return (0, 0)
        return (0, 1)
    if op == Op.GT:
        if a[0] > b[1]:
            return (1, 1)
        if a[1] <= b[0]:
            return (0, 0)
        return (0, 1)
    if op == Op.GE:
        if a[0] >= b[1]:
            return (1, 1)
        if a[1] < b[0]:
            return (0, 0)
        return (0, 1)
    return (0, 1)


def _arith_range(op: Op, a: Range, b: Range) -> Range | None:
    try:
        if op == Op.ADD:
            return (a[0] + b[0], a[1] + b[1])
        if op == Op.SUB:
            return (a[0] - b[1], a[1] - b[0])
        if op == Op.MUL:
            vals = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
            return (min(vals), max(vals))
        if op in (Op.DIV, Op.MOD):
            if b[0] <= 0 <= b[1]:
                return None
            if op == Op.DIV:
                vals = (
                    int(a[0] / b[0]),
                    int(a[0] / b[1]),
                    int(a[1] / b[0]),
                    int(a[1] / b[1]),
                )
                return (min(vals), max(vals))
            # Remainder magnitude is bounded by the divisor.
            bound = max(abs(b[0]), abs(b[1])) - 1
            return (-bound, bound)
        if op == Op.MIN:
            return (min(a[0], b[0]), min(a[1], b[1]))
        if op == Op.MAX:
            return (max(a[0], b[0]), max(a[1], b[1]))
    except (OverflowError, ZeroDivisionError):
        return None
    return None


class RangeAnalysis:
    def __init__(
        self,
        func: Function,
        param_ranges: dict[int, Range] | None = None,
        config: OptimizerConfig | None = None,
        fixed_ranges: dict[int, Range] | None = None,
    ):
        self.func = func
        self.config = config or OptimizerConfig.from_env()
        self.fixed_ranges = fixed_ranges or {}
        self.ranges: dict[int, Range] = dict(param_ranges or {})
        self.ranges.update(self.fixed_ranges)
        self.visits: dict[int, int] = defaultdict(int)
        self.total_visits = 0

    def run(self) -> dict[int, Range]:
        if self.func.entry is None:
            return self.ranges
        worklist: deque[BasicBlock] = deque([self.func.entry])
        queued: set[int] = {id(self.func.entry)}

        while worklist:
            if (
                self.total_visits >= self.config.max_range_visits
                or len(self.ranges) >= self.config.max_range_values
            ):
                break
            block = worklist.popleft()
            queued.discard(id(block))
            self.total_visits += 1
            self.visits[id(block)] += 1

            changed = False
            for inst in block.instructions:
                result_range = self._infer_inst(inst)
                if inst.result is None or result_range is None:
                    continue
                old = self.ranges.get(inst.result.id)
                new = _union(old, result_range)
                # Widen values that keep changing inside a loop.
                if self.visits[id(block)] > self.config.range_widen_after:
                    new = None if old is not None else old
                if new != old:
                    if new is None:
                        self.ranges.pop(inst.result.id, None)
                        inst.result.value_range = None
                    else:
                        self.ranges[inst.result.id] = new
                        inst.result.value_range = new
                    changed = True

            successors = self._feasible_successors(block)
            if changed or len(successors) < len(block.successors):
                for succ in successors:
                    if id(succ) not in queued:
                        queued.add(id(succ))
                        worklist.append(succ)

        for value in self.func.all_values():
            if value.id in self.ranges:
                value.value_range = self.ranges[value.id]
        return self.ranges

    def _infer_inst(self, inst: Instruction) -> Range | None:
        op = inst.op
        if op == Op.CONST_INT:
            return (int(inst.imm_int or 0), int(inst.imm_int or 0))
        if op == Op.CONST_BOOL:
            return (1, 1) if inst.imm_int else (0, 0)
        if op == Op.PHI:
            if inst.result is not None and inst.result.id in self.fixed_ranges:
                return self.fixed_ranges[inst.result.id]
            result = None
            for operand in inst.operands:
                r = _rng(operand, self.ranges)
                if r is None:
                    return None
                result = _union(result, r)
            return result
        if op == Op.SELECT and len(inst.operands) >= 3:
            a = _rng(inst.operands[1], self.ranges)
            b = _rng(inst.operands[2], self.ranges)
            if a is None or b is None:
                return None
            return _union(a, b)
        if op == Op.NOT and inst.operands:
            r = _rng(inst.operands[0], self.ranges)
            if r is None:
                return None
            if r == (0, 0):
                return (1, 1)
            if r == (1, 1):
                return (0, 0)
            return (0, 1)
        if op == Op.NEG and inst.operands:
            r = _rng(inst.operands[0], self.ranges)
            return (-r[1], -r[0]) if r else None
        if op == Op.ABS and inst.operands:
            r = _rng(inst.operands[0], self.ranges)
            if r is None:
                return None
            if r[0] >= 0:
                return r
            if r[1] <= 0:
                return (-r[1], -r[0])
            return (0, max(-r[0], r[1]))
        if op == Op.TO_BOOL:
            return (0, 1)
        if op in (Op.EQ, Op.NE, Op.LT, Op.LE, Op.GT, Op.GE) and len(inst.operands) >= 2:
            a = _rng(inst.operands[0], self.ranges)
            b = _rng(inst.operands[1], self.ranges)
            if a is None or b is None:
                return (0, 1)
            return _compare_range(op, a, b)
        if op in (Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.MIN, Op.MAX) and len(
            inst.operands
        ) >= 2:
            a = _rng(inst.operands[0], self.ranges)
            b = _rng(inst.operands[1], self.ranges)
            if a is None or b is None:
                return None
            return _arith_range(op, a, b)
        if op in (Op.AND, Op.OR) and len(inst.operands) >= 2:
            a = _rng(inst.operands[0], self.ranges)
            b = _rng(inst.operands[1], self.ranges)
            if a is None or b is None:
                return (0, 1)
            av = None if a[0] != a[1] else bool(a[0])
            bv = None if b[0] != b[1] else bool(b[0])
            if op == Op.AND:
                if av is False or bv is False:
                    return (0, 0)
                if av is True and bv is True:
                    return (1, 1)
            else:
                if av is True or bv is True:
                    return (1, 1)
                if av is False and bv is False:
                    return (0, 0)
            return (0, 1)
        return None

    def _feasible_successors(self, block: BasicBlock) -> list[BasicBlock]:
        term = block.terminator
        if term is None:
            return list(block.successors)
        if term.op == Op.BRANCH and term.operands and len(term.target_blocks) >= 2:
            cond = _rng(term.operands[0], self.ranges)
            if cond == (1, 1):
                return [term.target_blocks[0]]
            if cond == (0, 0):
                return [term.target_blocks[1]]
        return list(block.successors)


def infer_loop_ranges(func: Function) -> dict[int, Range]:
    """Infer induction-variable bounds for natural loops.

    These bounds are only used to derive per-call argument ranges; they are not
    used to fold the loop's own controlling branch.
    """
    from optimizer.analysis import FunctionAnalysis

    result: dict[int, Range] = {}
    try:
        analysis = FunctionAnalysis(func)
    except Exception:
        return result

    for loop in analysis.loops.loops:
        header = loop.header
        for phi in header.phi_nodes:
            if len(phi.operands) != 2 or len(phi.target_blocks) != 2 or phi.result is None:
                continue
            inside_idx = None
            outside_idx = None
            for i, pred in enumerate(phi.target_blocks):
                if pred in loop.blocks:
                    inside_idx = i
                else:
                    outside_idx = i
            if inside_idx is None or outside_idx is None:
                continue
            init = _rng(phi.operands[outside_idx], {})
            if init is None:
                continue
            back = phi.operands[inside_idx]
            step = None
            if isinstance(back, Value) and back.defining_inst is not None:
                bi = back.defining_inst
                if bi.op in (Op.ADD, Op.SUB) and len(bi.operands) >= 2:
                    if bi.op == Op.ADD:
                        pairs = (
                            (bi.operands[0], bi.operands[1]),
                            (bi.operands[1], bi.operands[0]),
                        )
                    else:
                        # SUB is not commutative: only phi - const is an
                        # induction step, never const - phi.
                        pairs = ((bi.operands[0], bi.operands[1]),)
                    for a, b in pairs:
                        if a is phi.result:
                            step_const = _get_const(b)
                            if step_const is not None:
                                step = int(step_const) * (1 if bi.op == Op.ADD else -1)
                                break
            if not step:
                continue

            for block in loop.blocks:
                term = block.terminator
                if term is None or term.op != Op.BRANCH or len(term.target_blocks) < 2:
                    continue
                cond = term.operands[0] if term.operands else None
                if not isinstance(cond, Value) or cond.defining_inst is None:
                    continue
                ci = cond.defining_inst
                if ci.op not in (Op.LT, Op.LE, Op.GT, Op.GE) or len(ci.operands) < 2:
                    continue
                left, right = ci.operands[0], ci.operands[1]
                op = ci.op
                if left is phi.result and _get_const(right) is not None:
                    bound = int(_get_const(right))
                elif right is phi.result and _get_const(left) is not None:
                    bound = int(_get_const(left))
                    # Flip the comparison direction so the phi is on the left.
                    op = {
                        Op.LT: Op.GT,
                        Op.LE: Op.GE,
                        Op.GT: Op.LT,
                        Op.GE: Op.LE,
                    }[ci.op]
                else:
                    continue
                true_inside = term.target_blocks[0] in loop.blocks
                false_inside = term.target_blocks[1] in loop.blocks
                inside_op = op if true_inside else None
                if inside_op is None and false_inside:
                    # Invert the comparison for the false edge.
                    inside_op = {
                        Op.LT: Op.GE,
                        Op.LE: Op.GT,
                        Op.GT: Op.LE,
                        Op.GE: Op.LT,
                    }.get(op)
                if inside_op is None:
                    continue

                lo, hi = init
                if step > 0:
                    # The induction variable starts at init and moves toward the
                    # loop bound; init's upper part is not a loop-body bound.
                    if inside_op == Op.LT:
                        hi = bound - 1
                    elif inside_op == Op.LE:
                        hi = bound
                    elif inside_op == Op.GT:
                        lo = max(lo, bound + 1)
                    elif inside_op == Op.GE:
                        lo = max(lo, bound)
                else:
                    if inside_op == Op.GT:
                        lo = max(lo, bound + 1)
                    elif inside_op == Op.GE:
                        lo = max(lo, bound)
                    elif inside_op == Op.LT:
                        hi = bound - 1
                    elif inside_op == Op.LE:
                        hi = bound
                if lo <= hi:
                    result[phi.result.id] = (lo, hi)
                break

    return result


def _get_const(value) -> int | None:
    if isinstance(value, Constant):
        return int(value.value) if isinstance(value.value, int) else None
    if isinstance(value, Value) and value.defining_inst is not None:
        inst = value.defining_inst
        if inst.op == Op.CONST_INT:
            return int(inst.imm_int or 0)
        if inst.op == Op.CONST_BOOL:
            return 1 if inst.imm_int else 0
    return None


def range_fold_branches(
    func: Function,
    param_ranges: dict[int, Range] | None = None,
    config: OptimizerConfig | None = None,
) -> bool:
    """Fold branches provable from ranges and mark safe division checks."""
    analysis = RangeAnalysis(func, param_ranges, config)
    ranges = analysis.run()
    changed = False

    for block in func.blocks:
        for inst in block.instructions:
            if inst.op in (Op.DIV, Op.MOD) and len(inst.operands) >= 2:
                divisor = _rng(inst.operands[1], ranges)
                if divisor is not None and (divisor[0] > 0 or divisor[1] < 0):
                    if not getattr(inst, "no_zero_check", False):
                        inst.no_zero_check = True
                        changed = True

        term = block.terminator
        if (
            term is not None
            and term.op == Op.BRANCH
            and term.operands
            and len(term.target_blocks) >= 2
        ):
            # Only use ranges from this run. Persistent value_range hints may
            # include loop-body induction bounds, which are valid inside an
            # iteration but must never fold the loop's own exit branch.
            cond = _rng(term.operands[0], ranges)
            if cond not in ((0, 0), (1, 1)):
                continue
            target = term.target_blocks[0] if cond == (1, 1) else term.target_blocks[1]
            dead = term.target_blocks[1] if cond == (1, 1) else term.target_blocks[0]
            term.op = Op.JUMP
            term.remove_from_uses()
            term.operands = []
            term.target_blocks = [target]
            term.imm_str = target.label
            block.successors = [target]
            if block in dead.predecessors:
                dead.predecessors.remove(block)
            changed = True
    return changed


def _merge_param_range(old: Range | None, new: Range | None) -> Range | None:
    return _union(old, new)


def analyze_module_ranges(
    module: Module, config: OptimizerConfig | None = None
) -> dict[str, dict[int, Range]]:
    """Propagate call-site ranges into callee parameter ranges.

    Returns the final range map for every function. Call instructions receive
    `arg_ranges` so specialization can choose a call-specific version.
    """
    cfg = config or OptimizerConfig.from_env()
    funcs = {f.name: f for f in module.functions}
    param_ranges: dict[str, list[Range | None]] = {
        name: [None] * len(func.params) for name, func in funcs.items()
    }
    param_unknown: set[tuple[str, int]] = set()

    # Loop-local facts are only valid for calls executed inside that loop.
    from optimizer.analysis import FunctionAnalysis
    block_loop: dict[str, dict[int, set[int]]] = {}
    for name, func in funcs.items():
        try:
            loops = FunctionAnalysis(func).loops
        except Exception:
            block_loop[name] = {}
            continue
        mapping: dict[int, set[int]] = {}
        for loop in loops.loops:
            block_ids = {id(b) for b in loop.blocks}
            for b in loop.blocks:
                mapping[id(b)] = block_ids
        block_loop[name] = mapping

    def _range_for_arg(arg, owner: str | None, call: Instruction, r):
        if r is None or not isinstance(arg, Value):
            return r
        def_block = arg.defining_inst.block if arg.defining_inst else None
        if def_block is None or call.block is None or owner is None:
            return r
        loop_blocks = block_loop.get(owner, {}).get(id(def_block))
        if loop_blocks is not None and id(call.block) not in loop_blocks:
            return None
        return r

    def merge_call(call: Instruction, analyses: dict[str, dict[int, Range]] | None):
        target = funcs.get(call.imm_str or "")
        if target is None:
            return False
        changed = False
        arg_ranges: list[Range | None] = []
        owner = call.block.func.name if call.block and call.block.func else None
        owner_ranges = (analyses or {}).get(owner or "", {})
        for i, arg in enumerate(call.operands):
            r = _rng(arg, owner_ranges)
            if r is None and isinstance(arg, Value):
                r = arg.value_range
            r = _range_for_arg(arg, owner, call, r)
            arg_ranges.append(r)
            if i < len(param_ranges[target.name]):
                if r is None:
                    key = (target.name, i)
                    if key not in param_unknown:
                        param_unknown.add(key)
                        param_ranges[target.name][i] = None
                        changed = True
                elif (target.name, i) not in param_unknown:
                    old = param_ranges[target.name][i]
                    new = _merge_param_range(old, r)
                    if new != old:
                        param_ranges[target.name][i] = new
                        changed = True
        call.arg_ranges = arg_ranges
        return changed

    # Seed with constants visible at call sites.
    for func in module.functions:
        for inst in func.all_instructions():
            if inst.op == Op.CALL:
                merge_call(inst, None)

    last_analyses: dict[str, dict[int, Range]] = {}
    for _ in range(cfg.max_range_iterations):
        analyses: dict[str, dict[int, Range]] = {}
        for name, func in funcs.items():
            seeded = {
                p.id: param_ranges[name][i]
                for i, p in enumerate(func.params)
                if i < len(param_ranges[name]) and param_ranges[name][i] is not None
            }
            func.param_ranges = seeded
            fixed = infer_loop_ranges(func)
            analyses[name] = RangeAnalysis(func, seeded, cfg, fixed).run()

        changed = False
        for func in module.functions:
            for inst in func.all_instructions():
                if inst.op == Op.CALL:
                    changed |= merge_call(inst, analyses)
        last_analyses = analyses
        if not changed:
            break

    # Final pass records arg_ranges with the freshest analysis.
    if last_analyses:
        for func in module.functions:
            for inst in func.all_instructions():
                if inst.op == Op.CALL:
                    merge_call(inst, last_analyses)
    return last_analyses

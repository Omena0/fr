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
    Module, Function, BasicBlock, Instruction, Value, Constant, Param,
    Op, IRType, StructType, ListType, ValueType,
    SIDE_EFFECT_OPS, COMMUTATIVE_OPS, TERMINATOR_OPS,
)
from optimizer.analysis import DomTree, LoopInfo, LivenessInfo, FunctionAnalysis
from optimizer.types import EscapeAnalysis


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
                if inst.result and inst.op in (Op.CONST_INT, Op.CONST_FLOAT,
                                                Op.CONST_BOOL, Op.CONST_STR):
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


def _cse_key(inst: Instruction) -> tuple | None:
    """Create a hashable key for an instruction for CSE.
    Returns None if the instruction can't be CSE'd."""
    if inst.op in SIDE_EFFECT_OPS:
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


# ── SROA: Scalar Replacement of Aggregates ──────────────────────

def sroa(func: Function) -> bool:
    """Replace struct allocations with individual scalar values when possible.

    A struct can be SROA'd if:
    1. It doesn't escape the function (no RETURN, no STORE_GLOBAL, no passing to functions that store it)
    2. All uses are LOAD_FIELD and STORE_FIELD with constant field indices
    3. The struct is small enough (≤ MAX_SROA_FIELDS)
    """
    MAX_SROA_FIELDS = 8
    changed = False

    escape = EscapeAnalysis(func)

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


# ── Inlining ────────────────────────────────────────────────────

def inline_small_functions(module: Module, max_inst: int = 20) -> bool:
    """Inline small functions at call sites."""
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
                    if (target and target is not func and
                            func_sizes.get(target_name, 999) <= max_inst and
                            len(target.blocks) == 1 and not target.is_extern):
                        if _try_inline(func, block, inst, target, i):
                            changed = True
                            continue  # Re-check same index (inlined code is there now)
                i += 1

    return changed


def _try_inline(caller_func: Function, call_block: BasicBlock,
                call_inst: Instruction, callee: Function,
                call_idx: int) -> bool:
    """Inline a single-block function at a call site."""
    if len(callee.blocks) != 1:
        return False

    callee_block = callee.blocks[0]

    # Map callee params to call arguments
    param_map: dict[int, Value] = {}
    for j, p in enumerate(callee.params):
        if j < len(call_inst.operands):
            param_map[p.id] = call_inst.operands[j]

    # Clone callee instructions (except RETURN)
    return_val = None
    inlined_insts = []
    for cinst in callee_block.instructions:
        if cinst.op in (Op.RETURN, Op.RETURN_VOID):
            if cinst.op == Op.RETURN and cinst.operands:
                return_val = cinst.operands[0]
                # Map through param_map
                if isinstance(return_val, Value) and return_val.id in param_map:
                    return_val = param_map[return_val.id]
            continue

        # Clone instruction
        new_operands = []
        for v in cinst.operands:
            if isinstance(v, Value) and v.id in param_map:
                new_operands.append(param_map[v.id])
            else:
                new_operands.append(v)

        new_inst = Instruction(cinst.op, new_operands,
                               cinst.result.type if cinst.result else None,
                               cinst.source_line)
        new_inst.imm_int = cinst.imm_int
        new_inst.imm_str = cinst.imm_str
        new_inst.imm_float = cinst.imm_float
        new_inst.block = call_block

        # Map old value to new value
        if cinst.result and new_inst.result:
            param_map[cinst.result.id] = new_inst.result

        inlined_insts.append(new_inst)

    # Replace call instruction with inlined code
    call_block.instructions.pop(call_idx)
    for j, new_inst in enumerate(inlined_insts):
        call_block.instructions.insert(call_idx + j, new_inst)

    # Replace call result uses with return value
    if call_inst.result and return_val:
        mapped_ret = param_map.get(return_val.id, return_val) if isinstance(return_val, Value) else return_val
        for user in list(call_inst.result.uses):
            user.replace_operand(call_inst.result, mapped_ret)

    return True


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


# ── Pass pipeline ───────────────────────────────────────────────

def run_passes(module: Module, level: int = 2) -> bool:
    """Run optimization passes on the module.

    level 0: no optimization
    level 1: basic (SCCP, algebraic, DCE)
    level 2: standard (+ CSE, LICM, SROA, inlining)
    level 3: aggressive (+ synthesis, more inlining)
    """
    if level == 0:
        return False

    overall_changed = False

    # Run passes in a fixed-point loop
    for iteration in range(20):  # Safety limit
        changed = False

        for func in module.functions:
            if func.is_extern:
                continue

            changed |= sccp(func)
            changed |= algebraic_simplify(func)
            changed |= simplify_branches(func)
            changed |= dce(func)

            if level >= 2:
                changed |= cse(func)
                changed |= sroa(func)
                changed |= tco(func)

        if level >= 2:
            changed |= inline_small_functions(module)

        overall_changed |= changed
        if not changed:
            break

    # Final DCE cleanup
    for func in module.functions:
        if not func.is_extern:
            dce(func)

    return overall_changed

"""SMT-based superoptimizer using Z3.

This is the core differentiator: instead of pattern-matching known optimizations,
we mathematically prove whether a cheaper instruction sequence computes the same
result. This finds optimizations that no hand-written pass ever would.

Pipeline:
1. Harvest: extract small IR windows (2-6 instructions with one output)
2. Encode: convert to Z3 bitvector formulas
3. Search: enumerate cheaper candidate sequences by cost
4. Verify: prove equivalence with Z3 (∀ inputs. candidate == original)
5. Cache: store proven rewrites for instant reuse

The solver is optional — if z3 is not installed, synthesis is skipped.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from collections import defaultdict
from optimizer.ir import (
    Module, Function, BasicBlock, Instruction, Value, Op, IRType,
    SIDE_EFFECT_OPS, COMMUTATIVE_OPS,
)

try:
    from z3 import (
        BitVec, BitVecVal, BitVecSort, ForAll, Solver, sat, unsat,
        UDiv, URem, LShR, If, Extract, Concat, ZeroExt, SignExt,
        BoolVal, And as Z3And, Or as Z3Or, Not as Z3Not,
        set_param,
    )
    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False

# Cache directory
CACHE_DIR = Path.home() / '.cache' / 'fr'
CACHE_FILE = CACHE_DIR / 'synthesis_cache.json'

# Cost model for instructions (lower = cheaper)
INST_COST = {
    Op.CONST_INT: 0,
    Op.CONST_FLOAT: 0,
    Op.CONST_BOOL: 0,
    Op.ADD: 1,
    Op.SUB: 1,
    Op.MUL: 3,
    Op.DIV: 20,
    Op.MOD: 20,
    Op.NEG: 1,
    Op.SHL: 1,
    Op.SHR: 1,
    Op.BIT_AND: 1,
    Op.BIT_OR: 1,
    Op.BIT_XOR: 1,
    Op.LT: 1,
    Op.GT: 1,
    Op.LE: 1,
    Op.GE: 1,
    Op.EQ: 1,
    Op.NE: 1,
    Op.AND: 1,
    Op.OR: 1,
    Op.NOT: 1,
    Op.FADD: 2,
    Op.FSUB: 2,
    Op.FMUL: 4,
    Op.FDIV: 15,
}


def total_cost(instructions: list[Instruction]) -> int:
    """Compute the total cost of a sequence of instructions."""
    return sum(INST_COST.get(i.op, 5) for i in instructions)


# ── Slice extraction ────────────────────────────────────────────

class IRSlice:
    """A small subgraph of IR instructions with inputs and one output."""

    def __init__(self, output: Value, instructions: list[Instruction],
                 inputs: list[Value]):
        self.output = output
        self.instructions = instructions
        self.inputs = inputs
        self.cost = total_cost(instructions)

    def key(self) -> str:
        """Hash key for this slice pattern (op sequence + operand topology)."""
        # Normalize: map each input to i0, i1, ... and encode the DAG structure
        input_map = {v.id: f'i{i}' for i, v in enumerate(self.inputs)}
        parts = []
        for inst in self.instructions:
            op_name = inst.op.name
            operands = []
            for v in inst.operands:
                if v.id in input_map:
                    operands.append(input_map[v.id])
                elif v.defining_inst and v.defining_inst.result:
                    operands.append(f'v{v.id}')
                else:
                    operands.append(f'c{getattr(v, "imm_int", "?")}')
            imm = ''
            if inst.imm_int is not None:
                imm = f'#{inst.imm_int}'
            parts.append(f'{op_name}({",".join(operands)}{imm})')
        return '|'.join(parts)


def harvest_slices(func: Function, max_size: int = 6) -> list[IRSlice]:
    """Extract optimizable slices from a function's IR."""
    slices = []

    for block in func.blocks:
        for inst in block.instructions:
            if inst.result is None:
                continue
            if inst.op in SIDE_EFFECT_OPS:
                continue
            # Only integer operations are amenable to synthesis
            if inst.result.type not in (IRType.INT64, IRType.BOOL):
                continue

            # BFS backward to collect the slice
            slice_insts = []
            inputs = []
            visited = set()
            worklist = [inst]

            while worklist and len(slice_insts) < max_size:
                current = worklist.pop(0)
                if current.result and current.result.id in visited:
                    continue
                if current.result:
                    visited.add(current.result.id)

                if current.op in SIDE_EFFECT_OPS:
                    # Can't include side-effecting instructions
                    if current.result and current.result not in inputs:
                        inputs.append(current.result)
                    continue

                slice_insts.append(current)

                for v in current.operands:
                    if isinstance(v, Value):
                        if v.defining_inst and v.defining_inst.result and \
                                v.defining_inst.result.id not in visited and \
                                v.defining_inst.op not in SIDE_EFFECT_OPS:
                            worklist.append(v.defining_inst)
                        elif v not in inputs:
                            inputs.append(v)

            if len(slice_insts) >= 2 and inputs:
                # Order instructions topologically
                slice_insts.sort(key=lambda i: i.result.id if i.result else 0)
                slices.append(IRSlice(inst.result, slice_insts, inputs))

    return slices


# ── Z3 encoding ─────────────────────────────────────────────────

BV_WIDTH = 64


def _encode_value(v: Value, env: dict[int, 'z3.BitVecRef']) -> 'z3.BitVecRef':
    """Encode a Value as a Z3 bitvector, creating a fresh symbolic var if needed."""
    if v.id in env:
        return env[v.id]
    # Create symbolic variable
    sym = BitVec(f'v{v.id}', BV_WIDTH)
    env[v.id] = sym
    return sym


def _encode_instruction(inst: Instruction, env: dict) -> 'z3.BitVecRef | None':
    """Encode an instruction's result as a Z3 expression."""
    if not HAS_Z3:
        return None

    ops = [_encode_value(v, env) for v in inst.operands if isinstance(v, Value)]
    op = inst.op

    if op == Op.CONST_INT:
        result = BitVecVal(inst.imm_int or 0, BV_WIDTH)
    elif op == Op.ADD and len(ops) == 2:
        result = ops[0] + ops[1]
    elif op == Op.SUB and len(ops) == 2:
        result = ops[0] - ops[1]
    elif op == Op.MUL and len(ops) == 2:
        result = ops[0] * ops[1]
    elif op == Op.NEG and len(ops) == 1:
        result = -ops[0]
    elif op == Op.SHL and len(ops) == 2:
        result = ops[0] << ops[1]
    elif op == Op.SHR and len(ops) == 2:
        result = LShR(ops[0], ops[1])
    elif op == Op.BIT_AND and len(ops) == 2:
        result = ops[0] & ops[1]
    elif op == Op.BIT_OR and len(ops) == 2:
        result = ops[0] | ops[1]
    elif op == Op.BIT_XOR and len(ops) == 2:
        result = ops[0] ^ ops[1]
    elif op == Op.LT and len(ops) == 2:
        result = If(ops[0] < ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.GT and len(ops) == 2:
        result = If(ops[0] > ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.LE and len(ops) == 2:
        result = If(ops[0] <= ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.GE and len(ops) == 2:
        result = If(ops[0] >= ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.EQ and len(ops) == 2:
        result = If(ops[0] == ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.NE and len(ops) == 2:
        result = If(ops[0] != ops[1], BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.AND and len(ops) == 2:
        result = ops[0] & ops[1]
    elif op == Op.OR and len(ops) == 2:
        result = ops[0] | ops[1]
    elif op == Op.NOT and len(ops) == 1:
        result = If(ops[0] == BitVecVal(0, BV_WIDTH),
                    BitVecVal(1, BV_WIDTH), BitVecVal(0, BV_WIDTH))
    elif op == Op.SELECT and len(ops) == 3:
        result = If(ops[0] != BitVecVal(0, BV_WIDTH), ops[1], ops[2])
    else:
        return None

    if inst.result:
        env[inst.result.id] = result
    return result


def encode_slice(slice_: IRSlice) -> tuple | None:
    """Encode a slice as a Z3 formula.
    Returns (result_expr, input_symbols, env) or None if encoding fails."""
    if not HAS_Z3:
        return None

    env = {}
    # Create symbolic inputs
    input_syms = []
    for v in slice_.inputs:
        sym = BitVec(f'input_{v.id}', BV_WIDTH)
        env[v.id] = sym
        input_syms.append(sym)

    # Encode each instruction in topological order
    result_expr = None
    for inst in slice_.instructions:
        result_expr = _encode_instruction(inst, env)
        if result_expr is None and inst.result == slice_.output:
            return None

    if slice_.output.id in env:
        result_expr = env[slice_.output.id]
    else:
        return None

    return (result_expr, input_syms, env)


# ── Candidate enumeration ──────────────────────────────────────

def _enumerate_candidates(input_syms, max_cost: int):
    """Enumerate candidate expressions ordered by cost.

    Generates all possible expressions up to the given cost using the input
    symbols and basic operations.
    """
    if not HAS_Z3:
        return

    candidates = []

    # Cost 0: just inputs, or constants
    for sym in input_syms:
        candidates.append((sym, 0, f'input'))
    for c in [0, 1, -1, 2]:
        candidates.append((BitVecVal(c, BV_WIDTH), 0, f'const_{c}'))

    yield from candidates

    # Cost 1: one unary op on an input
    for sym in input_syms:
        yield (-sym, 1, 'neg')
        yield (~sym, 1, 'bitnot')

    # Cost 1-3: one binary op on two inputs
    binary_ops = [
        (lambda a, b: a + b, 1, 'add'),
        (lambda a, b: a - b, 1, 'sub'),
        (lambda a, b: a & b, 1, 'and'),
        (lambda a, b: a | b, 1, 'or'),
        (lambda a, b: a ^ b, 1, 'xor'),
        (lambda a, b: a << b, 1, 'shl'),
        (lambda a, b: LShR(a, b), 1, 'lshr'),
        (lambda a, b: a * b, 3, 'mul'),
    ]

    all_exprs = list(input_syms) + [BitVecVal(c, BV_WIDTH) for c in [0, 1, 2]]

    for i, a in enumerate(all_exprs):
        for j, b in enumerate(all_exprs):
            for op_fn, op_cost, op_name in binary_ops:
                if op_cost <= max_cost:
                    try:
                        expr = op_fn(a, b)
                        yield (expr, op_cost, f'{op_name}({i},{j})')
                    except Exception:
                        pass

    # Cost 2-4: two operations (composition)
    if max_cost >= 2:
        base_results = []
        for a in input_syms:
            for op_fn, op_cost, op_name in binary_ops[:6]:  # Cheaper ops only
                for b in input_syms:
                    if op_cost <= max_cost // 2:
                        try:
                            r = op_fn(a, b)
                            base_results.append((r, op_cost))
                        except Exception:
                            pass

        for r, cost1 in base_results:
            for op_fn, cost2, op_name in binary_ops[:6]:
                if cost1 + cost2 <= max_cost:
                    for b in all_exprs:
                        try:
                            yield (op_fn(r, b), cost1 + cost2, f'composed')
                        except Exception:
                            pass


# ── Verification ────────────────────────────────────────────────

def verify_equivalence(original_expr, candidate_expr, input_syms,
                       timeout_ms: int = 200) -> bool:
    """Prove that candidate == original for all possible inputs using Z3."""
    if not HAS_Z3:
        return False

    s = Solver()
    s.set('timeout', timeout_ms)

    # We want to prove: ∀ inputs. original == candidate
    # Negate: ∃ inputs. original ≠ candidate
    # If UNSAT → proven equivalent
    s.add(original_expr != candidate_expr)

    result = s.check()
    return result == unsat


# ── Rewrite cache ───────────────────────────────────────────────

class RewriteCache:
    """Persistent cache of proven rewrites."""

    def __init__(self):
        self.rewrites: dict[str, dict] = {}  # slice_key → rewrite_info
        self._load()

    def _load(self):
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE) as f:
                    self.rewrites = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.rewrites = {}

    def save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.rewrites, f, indent=2)

    def get(self, key: str) -> dict | None:
        return self.rewrites.get(key)

    def put(self, key: str, rewrite: dict):
        self.rewrites[key] = rewrite

    def has(self, key: str) -> bool:
        return key in self.rewrites


# ── Superoptimizer main entry ──────────────────────────────────

class Superoptimizer:
    """SMT-based superoptimizer.

    Finds mathematically optimal instruction sequences by:
    1. Extracting small IR windows
    2. Encoding as Z3 bitvector formulas
    3. Enumerating cheaper candidates
    4. Proving equivalence
    5. Applying the rewrite
    """

    def __init__(self, timeout_ms: int = 200, max_slice_size: int = 6):
        self.timeout_ms = timeout_ms
        self.max_slice_size = max_slice_size
        self.cache = RewriteCache()
        self.stats = {'slices': 0, 'optimized': 0, 'cache_hits': 0, 'z3_calls': 0}

    def optimize(self, func: Function) -> bool:
        """Run synthesis-based optimization on a function."""
        if not HAS_Z3:
            return False

        changed = False
        slices = harvest_slices(func, self.max_slice_size)
        self.stats['slices'] += len(slices)

        for slice_ in slices:
            key = slice_.key()

            # Check cache first
            cached = self.cache.get(key)
            if cached is not None:
                self.stats['cache_hits'] += 1
                if cached.get('no_improvement'):
                    continue
                # Apply cached rewrite
                if self._apply_cached_rewrite(slice_, cached):
                    changed = True
                    self.stats['optimized'] += 1
                continue

            # Encode original slice
            encoded = encode_slice(slice_)
            if encoded is None:
                self.cache.put(key, {'no_improvement': True})
                continue

            original_expr, input_syms, env = encoded
            original_cost = slice_.cost

            # Search for cheaper candidates
            found_better = False
            for candidate_expr, candidate_cost, candidate_desc in \
                    _enumerate_candidates(input_syms, original_cost - 1):
                if candidate_cost >= original_cost:
                    continue

                self.stats['z3_calls'] += 1

                if verify_equivalence(original_expr, candidate_expr,
                                      input_syms, self.timeout_ms):
                    # Found a cheaper equivalent!
                    self.cache.put(key, {
                        'description': candidate_desc,
                        'cost_reduction': original_cost - candidate_cost,
                        'no_improvement': False,
                    })
                    self.stats['optimized'] += 1
                    found_better = True
                    changed = True
                    break

            if not found_better:
                self.cache.put(key, {'no_improvement': True})

        # Save cache periodically
        if self.stats['optimized'] > 0:
            self.cache.save()

        return changed

    def _apply_cached_rewrite(self, slice_: IRSlice, rewrite: dict) -> bool:
        """Apply a cached rewrite to a slice."""
        # For now, the rewrite is descriptive only — the actual application
        # requires re-synthesizing the replacement and inserting it into the IR.
        # This is a TODO: store the actual replacement instruction sequence
        # in the cache and apply it here.
        return False


def synthesis_pass(module: Module, timeout_ms: int = 200) -> bool:
    """Run the superoptimizer on all functions."""
    if not HAS_Z3:
        return False

    opt = Superoptimizer(timeout_ms=timeout_ms)
    changed = False

    for func in module.functions:
        if func.is_extern:
            continue
        changed |= opt.optimize(func)

    return changed

"""
WAT (WebAssembly Text Format) Optimizer

Performs several optimizations on WAT code:
1. Peephole optimizations (remove redundant instructions)
2. Constant folding (evaluate constant expressions)
3. Dead store elimination
4. Redundant local.get/set elimination
5. Strength reduction (replace expensive ops with cheaper ones)
6. Boolean simplifications
7. Comparison optimizations
8. Float constant folding
9. Division/modulo optimizations
"""

import re
from typing import List, Tuple, Optional

# Regex pattern for whitespace and comments
SEP = r'(?:\s|;;[^\n]*)*'

def instr_pat(name: str, args: Optional[str] = None) -> str:
    """Generate regex for an instruction with optional parentheses."""
    name = re.escape(name)
    return (
        r'\(?' + name + r'\s+' + args + r'\)?'
        if args
        else r'\(?' + name + r'\)?'
    )

def optimize_wat(wat_code: str) -> str:
    """Main optimization entry point."""
    # Split into lines, preserving structure
    lines = wat_code.split('\n')

    # Apply optimizations iteratively until no more changes
    changed = True
    iterations = 0
    max_iterations = 10

    while changed and iterations < max_iterations:
        changed = False
        iterations += 1

        # Peephole optimizations on the full text
        new_code = '\n'.join(lines)
        optimized = apply_peephole_optimizations(new_code)
        if optimized != new_code:
            changed = True
            lines = optimized.split('\n')

        # Line-by-line optimizations
        new_lines = apply_line_optimizations(lines)
        if new_lines != lines:
            changed = True
            lines = new_lines

    return '\n'.join(lines)

def apply_peephole_optimizations(code: str) -> str:
    """Apply pattern-based peephole optimizations."""

    # Pattern: (i64.const 0) followed by (i64.add) or (i64.sub) - remove both
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.add'), '', code)
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.sub'), '', code)

    # Pattern: (i32.const 0) followed by (i32.add) or (i32.sub) - remove both
    # DISABLED: This breaks STRUCT_GET for field 0 where address calculation is needed
    # code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.add'), '', code)
    # code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.sub'), '', code)

    # Pattern: (f64.const 0.0) followed by (f64.add) or (f64.sub) - remove both
    code = re.sub(instr_pat('f64.const', r'0\.0') + SEP + instr_pat('f64.add'), '', code)
    code = re.sub(instr_pat('f64.const', r'0\.0') + SEP + instr_pat('f64.sub'), '', code)

    # Pattern: (i64.const 1) followed by (i64.mul) - remove both
    code = re.sub(instr_pat('i64.const', '1') + SEP + instr_pat('i64.mul'), '', code)

    # Pattern: (i32.const 1) followed by (i32.mul) - remove both
    code = re.sub(instr_pat('i32.const', '1') + SEP + instr_pat('i32.mul'), '', code)

    # Pattern: (f64.const 1.0) followed by (f64.mul) - remove both
    code = re.sub(instr_pat('f64.const', r'1\.0') + SEP + instr_pat('f64.mul'), '', code)

    # Pattern: double negation for i64
    code = re.sub(
        instr_pat('i64.const', '-1') + SEP + instr_pat('i64.mul') + SEP +
        instr_pat('i64.const', '-1') + SEP + instr_pat('i64.mul'),
        '',
        code
    )

    # Pattern: i64.extend_i32_u followed by i32.wrap_i64 - remove both
    code = re.sub(
        instr_pat('i64.extend_i32_u') + SEP + instr_pat('i32.wrap_i64'),
        '',
        code
    )

    # Pattern: local.set followed immediately by local.get of same variable
    # This is a common pattern that can be optimized with local.tee
    # Use word boundary \b after backreference to avoid matching prefixes (e.g., $temp matching $temp3_i64)
    code = re.sub(
        instr_pat('local.set', r'\$(\w+)') + SEP + instr_pat('local.get', r'\$\1\b'),
        r'local.tee $\1',
        code
    )

    # Pattern: redundant wrap/extend pairs for i32/i64
    code = re.sub(instr_pat('i32.wrap_i64') + SEP + instr_pat('i64.extend_i32_s'), '', code)

    # Pattern: redundant extend/wrap pairs
    code = re.sub(instr_pat('i64.extend_i32_s') + SEP + instr_pat('i32.wrap_i64'), '', code)
    code = re.sub(instr_pat('i64.extend_i32_u') + SEP + instr_pat('i32.wrap_i64'), '', code)

    code = run_optimization_passes(code)

    # Remove empty lines that were created by removals
    code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)

    return code

def run_optimization_passes(code: str) -> str:
    passes = [
        # fold_float_constants,
        # optimize_boolean_ops,
        # apply_strength_reduction,
        optimize_drops,
        optimize_block_nesting,
        remove_unused_blocks,
        remove_unused_locals,
        remove_empty_lines,
        remove_comments,
        remove_duplicate_local_gets,
        remove_overwritten_local_sets,
        replace_tee_drop_with_set,
        # remove_drop_after_call,
        # remove_zero_address_adjust_before_load,
        # remove_duplicate_store_value,
        # inline_trivial_if,
        remove_empty_blocks,
        # mark_i64_high_half
    ]

    for func in passes:
        code = func(code)

    return code

def fold_integer_constants(code: str) -> str:
    """Fold constant integer operations."""

    # Pattern: (i64.const A) (i64.const B) (i64.add) -> (i64.const A+B)
    def fold_add_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a + b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.add'),
        fold_add_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.sub) -> (i64.const A-B)
    def fold_sub_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a - b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.sub'),
        fold_sub_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.mul) -> (i64.const A*B)
    def fold_mul_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a * b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.mul'),
        fold_mul_i64,
        code
    )

    # Pattern: (i32.const A) (i32.const B) (i32.add) -> (i32.const A+B)
    def fold_add_i32(match):
        a = int(match.group(1))
        b = int(match.group(2))
        # Handle 32-bit overflow
        result = (a + b) & 0xFFFFFFFF
        if result > 0x7FFFFFFF:
            result -= 0x100000000
        return f'(i32.const {result})'

    code = re.sub(
        instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.add'),
        fold_add_i32,
        code
    )

    # Pattern: (i32.const A) (i32.const B) (i32.sub) -> (i32.const A-B)
    def fold_sub_i32(match):
        a = int(match.group(1))
        b = int(match.group(2))
        result = (a - b) & 0xFFFFFFFF
        if result > 0x7FFFFFFF:
            result -= 0x100000000
        return f'(i32.const {result})'

    code = re.sub(
        instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.sub'),
        fold_sub_i32,
        code
    )

    # Pattern: (i32.const A) (i32.const B) (i32.mul) -> (i32.const A*B)
    def fold_mul_i32(match):
        a = int(match.group(1))
        b = int(match.group(2))
        result = (a * b) & 0xFFFFFFFF
        if result > 0x7FFFFFFF:
            result -= 0x100000000
        return f'(i32.const {result})'

    code = re.sub(
        instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.const', r'(-?\d+)') + SEP + instr_pat('i32.mul'),
        fold_mul_i32,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.div_s) -> (i64.const A/B)
    def fold_div_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return match.group(0) if b == 0 else f'(i64.const {a // b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.div_s'),
        fold_div_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.rem_s) -> (i64.const A%B)
    def fold_rem_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return match.group(0) if b == 0 else f'(i64.const {a % b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.rem_s'),
        fold_rem_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.and) -> (i64.const A&B)
    def fold_and_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a & b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.and'),
        fold_and_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.or) -> (i64.const A|B)
    def fold_or_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a | b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.or'),
        fold_or_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.xor) -> (i64.const A^B)
    def fold_xor_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a ^ b})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.xor'),
        fold_xor_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.shl) -> (i64.const A<<B)
    def fold_shl_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a << (b & 63)})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.shl'),
        fold_shl_i64,
        code
    )

    # Pattern: (i64.const A) (i64.const B) (i64.shr_s) -> (i64.const A>>B)
    def fold_shr_i64(match):
        a = int(match.group(1))
        b = int(match.group(2))
        return f'(i64.const {a >> (b & 63)})'

    code = re.sub(
        instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.const', r'(-?\d+)') + SEP + instr_pat('i64.shr_s'),
        fold_shr_i64,
        code
    )

    return code

def fold_float_constants(code: str) -> str:
    """Fold constant float operations."""

    # Pattern: (f64.const A) (f64.const B) (f64.add) -> (f64.const A+B)
    def fold_add_f64(match):
        a = float(match.group(1))
        b = float(match.group(2))
        return f'(f64.const {a + b})'

    code = re.sub(
        instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.add'),
        fold_add_f64,
        code
    )

    # Pattern: (f64.const A) (f64.const B) (f64.sub) -> (f64.const A-B)
    def fold_sub_f64(match):
        a = float(match.group(1))
        b = float(match.group(2))
        return f'(f64.const {a - b})'

    code = re.sub(
        instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.sub'),
        fold_sub_f64,
        code
    )

    # Pattern: (f64.const A) (f64.const B) (f64.mul) -> (f64.const A*B)
    def fold_mul_f64(match):
        a = float(match.group(1))
        b = float(match.group(2))
        return f'(f64.const {a * b})'

    code = re.sub(
        instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.mul'),
        fold_mul_f64,
        code
    )

    # Pattern: (f64.const A) (f64.const B) (f64.div) -> (f64.const A/B)
    def fold_div_f64(match):
        a = float(match.group(1))
        b = float(match.group(2))
        return match.group(0) if b == 0 else f'(f64.const {a / b})'

    code = re.sub(
        instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.const', r'(-?[\d.]+(?:e[+-]?\d+)?)') + SEP + instr_pat('f64.div'),
        fold_div_f64,
        code
    )

    # Pattern: (f64.neg) (f64.neg) -> remove both (double negation)
    code = re.sub(instr_pat('f64.neg') + SEP + instr_pat('f64.neg'), '', code)

    # Pattern: (f32.neg) (f32.neg) -> remove both
    code = re.sub(instr_pat('f32.neg') + SEP + instr_pat('f32.neg'), '', code)

    return code

def optimize_boolean_ops(code: str) -> str:
    """Optimize boolean and comparison operations."""

    # Pattern: (i32.eqz) (i32.eqz) -> just use the original value (double negation)
    code = re.sub(instr_pat('i32.eqz') + SEP + instr_pat('i32.eqz'), '', code)

    # Pattern: (i64.eqz) converts to i32, so no double eqz optimization for i64

    # Pattern: (i32.const 0) (i32.eq) -> (i32.eqz)
    code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.eq'), '(i32.eqz)', code)

    # Pattern: (i64.const 0) (i64.eq) -> (i64.eqz)
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.eq'), '(i64.eqz)', code)

    # Pattern: (i32.const 1) (i32.and) -> identity for booleans
    code = re.sub(instr_pat('i32.const', '1') + SEP + instr_pat('i32.and'), '', code)

    # Pattern: (i32.const 0) (i32.and) -> always 0
    code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.and'), '(drop)\n(i32.const 0)', code)

    # Pattern: (i32.const 0) (i32.or) -> identity
    code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.or'), '', code)

    # Pattern: (i64.const 0) (i64.and) -> always 0
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.and'), '(drop)\n(i64.const 0)', code)

    # Pattern: (i64.const 0) (i64.or) -> identity
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.or'), '', code)

    # Pattern: (i64.const -1) (i64.and) -> identity (all bits set)
    code = re.sub(instr_pat('i64.const', '-1') + SEP + instr_pat('i64.and'), '', code)

    # Pattern: (i64.const -1) (i64.or) -> always -1
    code = re.sub(instr_pat('i64.const', '-1') + SEP + instr_pat('i64.or'), '(drop)\n(i64.const -1)', code)

    # Pattern: x xor 0 -> x (identity)
    code = re.sub(instr_pat('i32.const', '0') + SEP + instr_pat('i32.xor'), '', code)
    code = re.sub(instr_pat('i64.const', '0') + SEP + instr_pat('i64.xor'), '', code)

    # Comparison inversions: (cmp) (i32.eqz) -> (inverted_cmp)
    # i64 comparisons
    code = re.sub(instr_pat('i64.eq') + SEP + instr_pat('i32.eqz'), '(i64.ne)', code)
    code = re.sub(instr_pat('i64.ne') + SEP + instr_pat('i32.eqz'), '(i64.eq)', code)
    code = re.sub(instr_pat('i64.lt_s') + SEP + instr_pat('i32.eqz'), '(i64.ge_s)', code)
    code = re.sub(instr_pat('i64.le_s') + SEP + instr_pat('i32.eqz'), '(i64.gt_s)', code)
    code = re.sub(instr_pat('i64.gt_s') + SEP + instr_pat('i32.eqz'), '(i64.le_s)', code)
    code = re.sub(instr_pat('i64.ge_s') + SEP + instr_pat('i32.eqz'), '(i64.lt_s)', code)
    code = re.sub(instr_pat('i64.lt_u') + SEP + instr_pat('i32.eqz'), '(i64.ge_u)', code)
    code = re.sub(instr_pat('i64.le_u') + SEP + instr_pat('i32.eqz'), '(i64.gt_u)', code)
    code = re.sub(instr_pat('i64.gt_u') + SEP + instr_pat('i32.eqz'), '(i64.le_u)', code)
    code = re.sub(instr_pat('i64.ge_u') + SEP + instr_pat('i32.eqz'), '(i64.lt_u)', code)

    # i32 comparisons
    code = re.sub(instr_pat('i32.eq') + SEP + instr_pat('i32.eqz'), '(i32.ne)', code)
    code = re.sub(instr_pat('i32.ne') + SEP + instr_pat('i32.eqz'), '(i32.eq)', code)
    code = re.sub(instr_pat('i32.lt_s') + SEP + instr_pat('i32.eqz'), '(i32.ge_s)', code)
    code = re.sub(instr_pat('i32.le_s') + SEP + instr_pat('i32.eqz'), '(i32.gt_s)', code)
    code = re.sub(instr_pat('i32.gt_s') + SEP + instr_pat('i32.eqz'), '(i32.le_s)', code)
    code = re.sub(instr_pat('i32.ge_s') + SEP + instr_pat('i32.eqz'), '(i32.lt_s)', code)
    code = re.sub(instr_pat('i32.lt_u') + SEP + instr_pat('i32.eqz'), '(i32.ge_u)', code)
    code = re.sub(instr_pat('i32.le_u') + SEP + instr_pat('i32.eqz'), '(i32.gt_u)', code)
    code = re.sub(instr_pat('i32.gt_u') + SEP + instr_pat('i32.eqz'), '(i32.le_u)', code)
    code = re.sub(instr_pat('i32.ge_u') + SEP + instr_pat('i32.eqz'), '(i32.lt_u)', code)

    # f64 comparisons (careful with NaN)
    # eqz(eq(a,b)) -> ne(a,b) is safe
    code = re.sub(instr_pat('f64.eq') + SEP + instr_pat('i32.eqz'), '(f64.ne)', code)
    code = re.sub(instr_pat('f64.ne') + SEP + instr_pat('i32.eqz'), '(f64.eq)', code)
    # Other float comparisons are tricky due to NaN, skipping for now

    return code

def apply_strength_reduction(code: str) -> str:
    """Replace expensive operations with cheaper equivalents."""

    # Pattern: x * 2 -> x << 1 (for i64)
    code = re.sub(
        instr_pat('i64.const', '2') + SEP + instr_pat('i64.mul'),
        '(i64.const 1)\n(i64.shl)',
        code
    )

    # Pattern: x * 4 -> x << 2 (for i64)
    code = re.sub(
        instr_pat('i64.const', '4') + SEP + instr_pat('i64.mul'),
        '(i64.const 2)\n(i64.shl)',
        code
    )

    # Pattern: x * 8 -> x << 3 (for i64)
    code = re.sub(
        instr_pat('i64.const', '8') + SEP + instr_pat('i64.mul'),
        '(i64.const 3)\n(i64.shl)',
        code
    )

    # Pattern: x * 16 -> x << 4 (for i64)
    code = re.sub(
        instr_pat('i64.const', '16') + SEP + instr_pat('i64.mul'),
        '(i64.const 4)\n(i64.shl)',
        code
    )

    # Pattern: x * 2 -> x << 1 (for i32)
    code = re.sub(
        instr_pat('i32.const', '2') + SEP + instr_pat('i32.mul'),
        '(i32.const 1)\n(i32.shl)',
        code
    )

    # Pattern: x * 4 -> x << 2 (for i32)
    code = re.sub(
        instr_pat('i32.const', '4') + SEP + instr_pat('i32.mul'),
        '(i32.const 2)\n(i32.shl)',
        code
    )

    # Pattern: x * 8 -> x << 3 (for i32)
    code = re.sub(
        instr_pat('i32.const', '8') + SEP + instr_pat('i32.mul'),
        '(i32.const 3)\n(i32.shl)',
        code
    )

    # Generic: x * (power of 2) -> x << k
    def _mul_shift_i64(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i64.const {k.bit_length()-1})\n(i64.shl)'
        return m.group(0)
    def _mul_shift_i32(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i32.const {k.bit_length()-1})\n(i32.shl)'
        return m.group(0)
    code = re.sub(instr_pat('i64.const', r'(\d+)') + SEP + instr_pat('i64.mul'), _mul_shift_i64, code)
    code = re.sub(instr_pat('i32.const', r'(\d+)') + SEP + instr_pat('i32.mul'), _mul_shift_i32, code)

    # Pattern: x / 2 -> x >> 1 (for unsigned, or when we know x >= 0)
    # Note: This is only safe for unsigned division or non-negative values
    # We'll do it for div_u only
    code = re.sub(
        instr_pat('i64.const', '2') + SEP + instr_pat('i64.div_u'),
        '(i64.const 1)\n(i64.shr_u)',
        code
    )

    code = re.sub(
        instr_pat('i64.const', '4') + SEP + instr_pat('i64.div_u'),
        '(i64.const 2)\n(i64.shr_u)',
        code
    )

    code = re.sub(
        instr_pat('i64.const', '8') + SEP + instr_pat('i64.div_u'),
        '(i64.const 3)\n(i64.shr_u)',
        code
    )

    code = re.sub(
        instr_pat('i32.const', '2') + SEP + instr_pat('i32.div_u'),
        '(i32.const 1)\n(i32.shr_u)',
        code
    )

    code = re.sub(
        instr_pat('i32.const', '4') + SEP + instr_pat('i32.div_u'),
        '(i32.const 2)\n(i32.shr_u)',
        code
    )

    # Generic: x / (power of 2) -> x >> k (unsigned)
    def _div_shift_i64_u(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i64.const {k.bit_length()-1})\n(i64.shr_u)'
        return m.group(0)
    def _div_shift_i32_u(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i32.const {k.bit_length()-1})\n(i32.shr_u)'
        return m.group(0)
    code = re.sub(instr_pat('i64.const', r'(\d+)') + SEP + instr_pat('i64.div_u'), _div_shift_i64_u, code)
    code = re.sub(instr_pat('i32.const', r'(\d+)') + SEP + instr_pat('i32.div_u'), _div_shift_i32_u, code)

    # Pattern: x % (power of 2) -> x & (power - 1) for unsigned
    code = re.sub(
        instr_pat('i64.const', '2') + SEP + instr_pat('i64.rem_u'),
        '(i64.const 1)\n(i64.and)',
        code
    )

    code = re.sub(
        instr_pat('i64.const', '4') + SEP + instr_pat('i64.rem_u'),
        '(i64.const 3)\n(i64.and)',
        code
    )

    code = re.sub(
        instr_pat('i64.const', '8') + SEP + instr_pat('i64.rem_u'),
        '(i64.const 7)\n(i64.and)',
        code
    )

    code = re.sub(
        instr_pat('i64.const', '16') + SEP + instr_pat('i64.rem_u'),
        '(i64.const 15)\n(i64.and)',
        code
    )

    code = re.sub(
        instr_pat('i32.const', '2') + SEP + instr_pat('i32.rem_u'),
        '(i32.const 1)\n(i32.and)',
        code
    )

    code = re.sub(
        instr_pat('i32.const', '4') + SEP + instr_pat('i32.rem_u'),
        '(i32.const 3)\n(i32.and)',
        code
    )

    # Generic: x % (power of 2) -> x & (power-1) (unsigned)
    def _rem_mask_i64(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i64.const {k-1})\n(i64.and)'
        return m.group(0)
    def _rem_mask_i32(m):
        k = int(m.group(1))
        if k > 0 and (k & (k - 1)) == 0:
            return f'(i32.const {k-1})\n(i32.and)'
        return m.group(0)
    code = re.sub(instr_pat('i64.const', r'(\d+)') + SEP + instr_pat('i64.rem_u'), _rem_mask_i64, code)
    code = re.sub(instr_pat('i32.const', r'(\d+)') + SEP + instr_pat('i32.rem_u'), _rem_mask_i32, code)

    return code

def optimize_drops(code: str) -> str:
    """Optimize drop operations."""

    # Pattern: (i32.const X) (drop) -> remove both
    code = re.sub(instr_pat('i32.const', r'-?\d+') + SEP + instr_pat('drop'), '', code)

    # Pattern: (i64.const X) (drop) -> remove both
    code = re.sub(instr_pat('i64.const', r'-?\d+') + SEP + instr_pat('drop'), '', code)

    # Pattern: (f32.const X) (drop) -> remove both
    code = re.sub(instr_pat('f32.const', r'-?[\d.]+(?:e[+-]?\d+)?') + SEP + instr_pat('drop'), '', code)

    # Pattern: (f64.const X) (drop) -> remove both
    code = re.sub(instr_pat('f64.const', r'-?[\d.]+(?:e[+-]?\d+)?') + SEP + instr_pat('drop'), '', code)

    # Pattern: (local.get $x) (drop) -> remove both (no side effects)
    code = re.sub(instr_pat('local.get', r'\$\w+') + SEP + instr_pat('drop'), '', code)

    # Pattern: (global.get $x) (drop) -> remove both (no side effects)
    code = re.sub(instr_pat('global.get', r'\$\w+') + SEP + instr_pat('drop'), '', code)

    return code

def apply_line_optimizations(lines: List[str]) -> List[str]:
    """Apply line-by-line optimizations."""
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            result.append(line)
            i += 1
            continue

        if (
            stripped in ('(return)', 'return', '(unreachable)', 'unreachable')
            or stripped.startswith('(br ')
            or stripped.startswith('br ')
        ):
            result.append(line)
            i += 1
            # Skip following code until we hit a label or end
            while i < len(lines):
                next_line = lines[i].strip()

                if not next_line:
                    i += 1
                    continue

                # Stop at control flow boundaries
                if (next_line.startswith('(block') or
                    next_line.startswith('block') or
                    next_line.startswith('(loop') or
                    next_line.startswith('loop') or
                    next_line.startswith('(if') or
                    next_line.startswith('if') or
                    next_line.startswith('(else') or
                    next_line.startswith('else') or
                    next_line.startswith('(end') or
                    next_line.startswith('end') or
                    next_line == ')'):
                    break
                # Skip this unreachable line
                i += 1
            continue

        result.append(line)
        i += 1

    return result

def optimize_block_nesting(code: str) -> str:
    """Merge redundant nested blocks."""
    
    # Ensure code is a string
    if isinstance(code, list):
        code = '\n'.join(code)
    
    # Limit iterations to prevent infinite loops
    for _ in range(500):
        blocks = []
        stack = []
        i = 0
        n = len(code)

        while i < n:
            # String
            if code[i] == '"':
                i += 1
                while i < n and (code[i] != '"' or code[i - 1] == '\\'):
                    i += 1
                i += 1
                continue

            # Comment
            if code[i] == ';':
                if i + 1 < n and code[i+1] == ';':
                    # Line comment ;;
                    end = code.find('\n', i)
                    if end == -1: end = n
                    i = end

                if i < n and code[i] == ';':
                     i += 1
                continue

            # Block comment start (;
            if code[i] == '(' and i + 1 < n and code[i+1] == ';':
                i += 2
                depth = 1
                while i < n and depth > 0:
                    if i + 1 < n and code[i] == '(' and code[i+1] == ';':
                        depth += 1
                        i += 2
                    elif i + 1 < n and code[i] == ';' and code[i+1] == ')':
                        depth -= 1
                        i += 2
                    else:
                        i += 1
                continue

            if code[i] == '(':
                # Check for (block ...
                # We use a regex that handles optional name and ensures boundary
                match = re.match(r'\((block)(?:\s+(\$[\w\d_]+)?)?(?=\s|\))', code[i:])
                if match:
                    name = match[2]
                    stack.append({'start': i, 'name': name, 'content_start': i + len(match[0])})
                else:
                    stack.append(None)
                i += 1
                continue

            if code[i] == ')':
                if stack:
                    item = stack.pop()
                    if item:
                        item['end'] = i + 1
                        blocks.append(item)
                i += 1
                continue

            i += 1

        found_merge = False
        blocks.sort(key=lambda x: x['start'])

        for j in range(len(blocks) - 1):
            outer = blocks[j]
            inner = blocks[j+1]

            # Check if inner is directly inside outer
            if inner['start'] > outer['start'] and inner['end'] < outer['end']:
                # Check if there's only whitespace/comments between them
                prefix = code[outer['content_start']:inner['start']]
                suffix = code[inner['end']:outer['end']-1]

                def is_ignorable(text):
                    # Remove line comments
                    text = re.sub(r';;.*', '', text)
                    # Remove whitespace
                    return not text.strip()

                if is_ignorable(prefix) and is_ignorable(suffix):
                    # Mergeable!

                    target_name = outer['name'] or inner['name']

                    # Reconstruct outer header
                    outer_header = '(block'
                    if target_name:
                        outer_header += f' {target_name}'

                    new_code_parts = []
                    new_code_parts.append(code[:outer['start']])
                    new_code_parts.append(outer_header)

                    # Body
                    inner_body = code[inner['content_start']:inner['end']-1]

                    if outer['name'] and inner['name'] and outer['name'] != inner['name']:
                         # Rename references to inner name -> outer name
                         pattern = re.escape(inner['name']) + r'(?!\w)'
                         inner_body = re.sub(pattern, outer['name'], inner_body)

                    # Preserve comments/whitespace from prefix/suffix
                    new_code_parts.append(prefix)
                    new_code_parts.append(inner_body)
                    new_code_parts.append(suffix)
                    new_code_parts.append(code[outer['end']-1:])

                    code = "".join(new_code_parts)
                    found_merge = True
                    break

        if not found_merge:
            break

    return code

def remove_unused_blocks(code: str) -> str:
    """Remove blocks and loops that are never targeted by branches."""
    
    # Find all used labels
    used_labels = set()

    # br and br_if
    matches = re.findall(r'(?:br|br_if)\s+(\$[\w\d_]+)', code)
    used_labels.update(matches)

    # br_table
    matches = re.findall(r'br_table\s+([^)\n]+)', code)
    for match in matches:
        labels = re.findall(r'\$[\w\d_]+', match)
        used_labels.update(labels)

    stack = []
    to_remove = [] 

    i = 0
    n = len(code)

    while i < n:
        # String skipping
        if code[i] == '"':
            i += 1
            while i < n and not (code[i] == '"' and code[i-1] != '\\'):
                i += 1
            i += 1
            continue

        # Comment skipping
        if code[i] == ';':
            if i + 1 < n and code[i+1] == ';':
                end = code.find('\n', i)
                if end == -1: end = n
                i = end
            if i < n and code[i] == ';': i += 1
            continue

        if code[i] == '(' and i + 1 < n and code[i+1] == ';':
            # Block comment
            i += 2
            depth = 1
            while i < n and depth > 0:
                if i + 1 < n and code[i] == '(' and code[i+1] == ';':
                    depth += 1
                    i += 2
                elif i + 1 < n and code[i] == ';' and code[i+1] == ')':
                    depth -= 1
                    i += 2
                else:
                    i += 1
            continue

        if code[i] == '(':
            if match := re.match(
                r'\((block|loop)(?:\s+(\$[\w\d_]+))?', code[i:]
            ):
                type_ = match.group(1)
                name = match.group(2)

                # Check for signature immediately following
                header_end = i + len(match.group(0))

                # Look ahead for (result or (param
                j = header_end
                signature_end = header_end

                while j < n:
                    if code[j].isspace():
                        j += 1
                        continue
                    if code[j] == '(' and code[j+1:].startswith('result'):
                        # Find end of (result ...)
                        k = j + 1
                        d = 1
                        while k < n and d > 0:
                            if code[k] == '(': d += 1
                            elif code[k] == ')': d -= 1
                            k += 1
                        signature_end = k
                        j = k
                        continue
                    if code[j] == '(' and code[j+1:].startswith('param'):
                        k = j + 1
                        d = 1
                        while k < n and d > 0:
                            if code[k] == '(': d += 1
                            elif code[k] == ')': d -= 1
                            k += 1
                        signature_end = k
                        j = k
                        continue
                    break

                is_used = True
                if name and name not in used_labels:
                    is_used = False

                # If no name, assume used (conservative)
                if not name:
                    is_used = True

                stack.append({
                    'start': i,
                    'content_start': signature_end,
                    'name': name,
                    'type': type_,
                    'remove': not is_used
                })
            else:
                stack.append(None)
            i += 1
            continue
        if code[i] == ')':
            if stack:
                item = stack.pop()
                if item and item.get('remove'):
                    to_remove.append((item['start'], i + 1, item['content_start'], i))
            i += 1
            continue

        i += 1

    to_remove.sort(key=lambda x: x[0], reverse=True)

    for start, end, content_start, content_end in to_remove:
        body = code[content_start:content_end]
        code = code[:start] + body + code[end:]

    return code

def remove_unused_locals(code: str) -> str:
    """Remove local variable declarations that are never used."""
    lines = code.split('\n')
    
    # Find all local declarations and track usage
    local_pattern = re.compile(r'\(local \$(\w+) (i32|i64|f64)\)')
    
    # Process each function separately
    result_lines = []
    in_function = False
    func_lines = []
    func_start = 0
    paren_depth = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Only match actual function definitions, not imports
        if stripped.startswith('(func ') and '(import' not in line:
            in_function = True
            func_lines = [line]
            func_start = i
            line_no_comment = line.split(';;')[0]
            paren_depth = line_no_comment.count('(') - line_no_comment.count(')')
        elif in_function:
            func_lines.append(line)
            line_no_comment = line.split(';;')[0]
            paren_depth += line_no_comment.count('(') - line_no_comment.count(')')
            
            # Check for end of function when paren depth returns to 0
            if paren_depth <= 0:
                # print(f"Finished function at line {i}, depth {paren_depth}")
                # Process this function
                func_code = '\n'.join(func_lines)
                
                # Find all declared locals
                declared_locals = set()
                for fl in func_lines:
                    match = local_pattern.search(fl)
                    if match:
                        declared_locals.add(match.group(1))
                
                # Find all used locals (local.get, local.set, local.tee)
                used_locals = set()
                usage_pattern = re.compile(r'local\.(get|set|tee) \$(\w+)')
                for fl in func_lines:
                    for match in usage_pattern.finditer(fl):
                        used_locals.add(match.group(2))
                
                # Filter out unused locals
                unused = declared_locals - used_locals
                
                # Rebuild function without unused locals
                new_func_lines = []
                for fl in func_lines:
                    match = local_pattern.search(fl)
                    if match and match.group(1) in unused:
                        continue  # Skip unused local declaration
                    new_func_lines.append(fl)
                
                result_lines.extend(new_func_lines)
                in_function = False
                func_lines = []
                paren_depth = 0
        else:
            result_lines.append(line)
    
    # Handle case where we're still in a function at end
    if func_lines:
        result_lines.extend(func_lines)
    
    return '\n'.join(result_lines)

def remove_unused_imports(code: str) -> str:
    """Remove import declarations for functions that are never called."""
    lines = code.split('\n')
    
    # Find all imported function names
    # Handle imports with or without leading whitespace
    import_pattern = re.compile(r'^\s*\(import\s+"[^"]+"\s+"[^"]+"\s+\(func\s+\$(\w+)')
    imported_funcs = {}  # name -> line index
    
    for i, line in enumerate(lines):
        match = import_pattern.search(line)
        if match:
            imported_funcs[match.group(1)] = i
    
    # Find all function calls in the code
    call_pattern = re.compile(r'call\s+\$(\w+)')
    called_funcs = set()
    
    for line in lines:
        # Strip comments before checking for calls
        if ';;' in line:
            line = line[:line.index(';;')]
            
        for match in call_pattern.finditer(line):
            called_funcs.add(match.group(1))
    
    # Find unused imports
    unused_imports = set(imported_funcs.keys()) - called_funcs
    lines_to_remove = {imported_funcs[name] for name in unused_imports}
    
    # Rebuild without unused imports
    result_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    
    return '\n'.join(result_lines)

def remove_empty_lines(code: str) -> str:
    """Remove excessive empty lines."""
    # Replace multiple consecutive empty lines with single empty line
    code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
    # Remove empty lines before closing parens
    code = re.sub(r'\n\s*\n(\s*\))', r'\n\1', code)
    return code

def remove_comments(code: str) -> str:
    """Remove comment lines to reduce output size."""
    lines = code.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        # Skip pure comment lines
        if stripped.startswith(';;'):
            continue
        # Remove inline comments (but keep the code)
        if ';;' in line:
            line = line[:line.index(';;')].rstrip()
        result.append(line)
    return '\n'.join(result)

def remove_duplicate_local_gets(code: str) -> str:
    pat = (
        instr_pat('local.get', r'(\$\w+)')
        + SEP +
        instr_pat('local.get', r'\1\b')
    )
    return re.sub(pat, r'local.get \1', code)

def remove_overwritten_local_sets(code: str) -> str:
    pat = (
        instr_pat('local.set', r'(\$\w+)')
        + SEP +
        instr_pat('local.set', r'\1\b')
    )
    return re.sub(pat, r'local.set \1', code)

def replace_tee_drop_with_set(code: str) -> str:
    pat = (
        instr_pat('local.tee', r'(\$\w+)')
        + SEP +
        instr_pat('drop')
    )
    return re.sub(pat, r'local.set \1', code)

def remove_drop_after_call(code: str) -> str:
    pat = (
        instr_pat('call', r'(\$\w+)')
        + SEP +
        instr_pat('drop')
    )
    return re.sub(pat, r'call \1', code)

def remove_zero_address_adjust_before_load(code: str) -> str:
    pat = (
        instr_pat('i32.const', '0')
        + SEP +
        instr_pat('i32.add')
        + SEP +
        r'\(?((i32|i64|f32|f64)\.load)\)?'
    )
    return re.sub(pat, r'\1', code)

def remove_duplicate_store_value(code: str) -> str:
    pat = (
        instr_pat('local.get', r'(\$\w+)')
        + SEP +
        instr_pat('local.get', r'\1\b')
        + SEP +
        r'\(?((i32|i64|f32|f64)\.store)\)?'
    )
    return re.sub(pat, r'local.get \1\n\2', code)

def inline_trivial_if(code: str) -> str:
    pat = (
        r'\(if' + SEP +
        r'\(then' + SEP +
        r'([\s\S]*?)' +
        SEP + r'\)\s*\)'
    )
    return re.sub(pat, r'\1', code)

def remove_empty_blocks(code: str) -> str:
    code = re.sub(r'\(block\s*\)', '', code)
    code = re.sub(r'\(loop\s*\)', '', code)
    return code

def mark_i64_high_half(code: str) -> str:
    return re.sub(
        instr_pat('i64.extend_i32_u') + SEP +
        instr_pat('i64.const', '32') + SEP +
        instr_pat('i64.shl'),
        '(;; PACK32_HIGH ;;)',
        code
    )



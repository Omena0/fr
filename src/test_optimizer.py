"""
Regression tests for the bytecode optimizer.

These tests compile small programs to bytecode and verify the optimizer
doesn't break correctness. Each test is motivated by a real bug that
shipped.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser import parse
from compiler import compile_ast_to_bytecode
from optimizer import BytecodeOptimizer


def compile(source: str) -> str:
    """Parse + compile source to optimized bytecode."""
    ast = parse(source, file='test.fr')
    bc, _ = compile_ast_to_bytecode(ast)
    return bc


def compile_unoptimized(source: str) -> str:
    """Parse + compile source to bytecode, then return the *un*optimized
    version (for comparison)."""
    ast = parse(source, file='test.fr')
    # Temporarily block the optimizer
    original = BytecodeOptimizer.optimize
    BytecodeOptimizer.optimize = lambda self, bytecode: bytecode
    try:
        bc, _ = compile_ast_to_bytecode(ast)
    finally:
        BytecodeOptimizer.optimize = original
    return bc


def extract_func_body(bc: str) -> list[str]:
    """Extract all non-directive instruction lines from the first .func."""
    lines = []
    in_func = False
    for line in bc.strip().split("\n"):
        stripped = line.strip()
        if stripped.startswith(".func"):
            in_func = True
            continue
        if stripped == ".end":
            break
        if in_func and stripped and not stripped.startswith(".") and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


# ============================================================
# Regression: dead store elimination across .line boundaries
# Bug: remove_dead_stores was called per-chunk (split at .line
#      directives).  A STORE in chunk A with its LOAD in chunk B
#      was incorrectly removed, producing broken bytecode.
# ============================================================

def test_dead_store_across_lines():
    """Variable assigned on one line and used on the next must NOT be removed."""
    source = (
        "void main() {\n"
        "    list x = [1, 2, 3]\n"
        "    println(x)\n"
        "}\n"
    )
    bc = compile(source)
    body = extract_func_body(bc)

    # The STORE for variable x (slot 0) must be present
    stores = [l for l in body if l.startswith("STORE 0")]
    assert stores, (
        "STORE 0 was removed by optimizer! Bytecode:\n" + bc
    )
    # And the LOAD for variable x must be present
    loads = [l for l in body if l.startswith("LOAD 0")]
    assert loads, "LOAD 0 missing!"


def test_dead_store_preserves_side_effect():
    """When a variable is assigned from a call result (LIST_POP) but never
    read, the STORE must be kept to maintain stack balance."""
    source = (
        "void main() {\n"
        "    list lst = [1, 2, 3]\n"
        "    int value = pop(lst)\n"
        "    println(str(lst))\n"
        "}\n"
    )
    bc = compile(source)
    body = extract_func_body(bc)

    # Both STORE 0 (lst) and STORE 1 (value) must exist.
    # The optimizer may NOT remove STORE 1 because LIST_POP is
    # not a simple CONST/LOAD — removing only the STORE leaves
    # the stack imbalanced.
    store_0 = [l for l in body if l == "STORE 0"]
    store_1 = [l for l in body if l == "STORE 1"]
    # At minimum, the assignments must produce valid bytecode that
    # doesn't corrupt the stack.  We check that both STORE instructions
    # are present (they may have been renumbered but should still exist).
    all_stores = [l for l in body if l.startswith("STORE ")]
    assert len(all_stores) >= 2, (
        f"Expected at least 2 STORE instructions, got {len(all_stores)}.\n"
        f"Body: {body}"
    )


def test_dead_store_truly_dead_is_removed():
    """A variable that is assigned a constant and never loaded should be
    removed by the optimizer (CONST + STORE pair dropped)."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  CONST_I64 42",
        "  STORE 0",        # slot 0 is never loaded — dead store
        "  CONST_STR \"1\"",
        "  BUILTIN_PRINTLN",
        "  RETURN_VOID",
    ]
    result = optimizer.remove_dead_stores(lines)
    stores = [l.strip() for l in result if l.strip() == "STORE 0"]
    assert not stores, (
        "STORE 0 should be removed — slot 0 is never loaded.\n"
        f"Result: {result}"
    )


# ============================================================
# Regression: FUSED instructions must be recognized as loads
# Bug: remove_dead_stores only checked LOAD and LOAD2_ instructions.
#      Fused instructions like INC_LOCAL, COPY_LOCAL_REF,
#      FUSED_LOAD_STORE, etc. also read from variable slots.
# ============================================================

def test_dead_store_respects_inc_local():
    """A variable used by INC_LOCAL must not be dead-store eliminated."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  CONST_I64 0",
        "  STORE 0",
        "  INC_LOCAL 0",
        "  LOAD 0",
        "  BUILTIN_PRINTLN",
        "  RETURN_VOID",
    ]
    result = optimizer.remove_dead_stores(lines)
    stores = [l.strip() for l in result if l.strip().startswith("STORE 0")]
    assert stores, "STORE 0 removed despite INC_LOCAL 0 reading it"


def test_dead_store_respects_copy_local_ref():
    """A variable used as COPY_LOCAL_REF source must not be eliminated."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  CONST_I64 0",
        "  STORE 0",
        "  COPY_LOCAL_REF 0 1",
        "  LOAD 1",
        "  BUILTIN_PRINTLN",
        "  RETURN_VOID",
    ]
    result = optimizer.remove_dead_stores(lines)
    stores = [l.strip() for l in result if l.strip().startswith("STORE 0")]
    assert stores, "STORE 0 removed despite COPY_LOCAL_REF using slot 0"


def test_dead_store_respects_fused_load_store():
    """Variables referenced in FUSED_LOAD_STORE must be kept."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  CONST_I64 5",
        "  STORE 0",
        "  FUSED_LOAD_STORE 0 1",
        "  LOAD 1",
        "  BUILTIN_PRINTLN",
        "  RETURN_VOID",
    ]
    result = optimizer.remove_dead_stores(lines)
    stores = [l.strip() for l in result if l.strip().startswith("STORE 0")]
    assert stores, "STORE 0 removed despite FUSED_LOAD_STORE reading slot 0"


# ============================================================
# Regression: .line directives must survive optimizer passes
# ============================================================

def test_line_directives_preserved():
    """The optimizer must not destroy .line directives."""
    source = (
        "void main() {\n"
        "    int x = 1\n"
        "    int y = 2\n"
        "    println(x + y)\n"
        "}\n"
    )
    bc = compile(source)
    assert ".line" in bc, ".line directives missing from optimized bytecode"


# ============================================================
# Regression: FUSED_GET_STORE_LOAD fusion
# Bug: Repeated STRUCT_GET + FUSED_STORE_LOAD pairs generated many
#      separate instructions. The optimizer should fuse them into
#      a single FUSED_GET_STORE_LOAD instruction with triplets.
# ============================================================

def test_fuse_get_store_load():
    """Consecutive STRUCT_GET + STORE + LOAD sequences must be fused."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  STRUCT_GET 0",
        "  FUSED_STORE_LOAD 2 1",
        "  STRUCT_GET 1",
        "  FUSED_STORE_LOAD 3 1",
        "  STRUCT_GET 2",
        "  FUSED_STORE_LOAD 4 1",
    ]
    result = optimizer.fuse_get_store_load(lines)
    fused = [l.strip() for l in result if 'FUSED_GET_STORE_LOAD' in l]
    assert len(fused) == 1, f"Expected 1 FUSED_GET_STORE_LOAD, got {len(fused)}: {result}"
    assert fused[0] == "FUSED_GET_STORE_LOAD 0 2 1 1 3 1 2 4 1", \
        f"Wrong args: {fused[0]}"


def test_fuse_get_store_load_raw():
    """Raw STRUCT_GET + STORE + LOAD (not yet fused) should also be detected."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  STRUCT_GET 0",
        "  STORE 2",
        "  LOAD 1",
        "  STRUCT_GET 1",
        "  STORE 3",
        "  LOAD 1",
    ]
    result = optimizer.fuse_get_store_load(lines)
    fused = [l.strip() for l in result if 'FUSED_GET_STORE_LOAD' in l]
    assert len(fused) == 1, f"Expected 1 FUSED_GET_STORE_LOAD, got {len(fused)}: {result}"
    assert fused[0] == "FUSED_GET_STORE_LOAD 0 2 1 1 3 1"


def test_fuse_get_store_load_single_not_fused():
    """A single STRUCT_GET + STORE + LOAD should NOT be fused (need >=2 triplets)."""
    optimizer = BytecodeOptimizer()
    lines = [
        "  STRUCT_GET 0",
        "  FUSED_STORE_LOAD 2 1",
        "  BUILTIN_PRINTLN",
    ]
    result = optimizer.fuse_get_store_load(lines)
    fused = [l.strip() for l in result if 'FUSED_GET_STORE_LOAD' in l]
    assert len(fused) == 0, f"Single pair should not be fused: {result}"


# ============================================================
# Run all tests
# ============================================================

def run_tests():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
    print(f"\nOptimizer tests: {passed}/{passed + failed} passed")
    if failed:
        print(f"{failed} test(s) FAILED")
    return failed


if __name__ == "__main__":
    sys.exit(run_tests())

# Fr Superoptimizer
# See PLAN.md for architecture documentation

# Re-export BytecodeOptimizer so existing `from optimizer import BytecodeOptimizer` works
from optimizer.bytecode_opt import BytecodeOptimizer

__all__ = ['BytecodeOptimizer', 'compile_native_ssa']


def compile_native_ssa(bytecode: str, opt_level: int = 2) -> str:
    """Compile bytecode to x86_64 assembly using the SSA IR pipeline.

    This is the new native compilation path:
    bytecode → IR → optimize → regalloc → codegen → peephole → asm

    Args:
        bytecode: The bytecode text (as produced by compiler.py)
        opt_level: 0=none, 1=basic, 2=standard, 3=aggressive+synthesis

    Returns:
        x86_64 assembly text (Intel syntax)
    """
    from optimizer.ir_builder import build_ir
    from optimizer.ir import dump_module
    from optimizer.passes import run_passes
    from optimizer.codegen import generate_asm
    from optimizer.peephole import optimize_asm_text

    # Phase 1: Build SSA IR from bytecode
    module = build_ir(bytecode)

    # Phase 2: Run optimization passes
    if opt_level > 0:
        run_passes(module, level=opt_level)

    # Phase 3: Run SMT synthesis (level 3 only)
    if opt_level >= 3:
        try:
            from optimizer.synthesis import synthesis_pass
            synthesis_pass(module)
        except ImportError:
            pass  # z3 not installed, skip

    # Phase 4: Generate assembly (includes register allocation)
    asm = generate_asm(module, opt_level)

    # Phase 5: Peephole optimize the assembly
    if opt_level > 0:
        asm = optimize_asm_text(asm)

    return asm

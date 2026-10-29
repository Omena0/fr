# Compiler Analysis and Optimization

The native pipeline is:

```
source → parse-time evaluation/memoization → bytecode → SSA IR
       → interprocedural analysis → specialization/inlining → lookup tables
       → register allocation → x86-64
```

## Layers of information

1. **Parse time** – literal folding, constant-function evaluation and memo tables.
   Information that is constant here is already reflected in the bytecode.
2. **SSA local passes** – SCCP, algebraic simplification, branch simplification,
   DCE, CSE, LICM, SROA, tail calls, linear block merging.
3. **Whole-program passes** – call graph purity, interprocedural range
   propagation, call-site specialization, pure constant-call folding, dead
   function removal.
4. **Compile-time simulation** – pure scalar functions are interpreted under a
   strict budget and the results become embedded lookup tables.
5. **Code generation** – range facts remove proven-impossible division checks,
   and lookup-table fast paths run before the normal function body. Non-
   allocating leaf functions omit allocation-scope calls; comparisons fused into
   branches avoid setcc/test sequences; `lea` handles integer add/sub copies;
   list length and valid list indexing are inlined; live XMM values are
   preserved across calls; and a final assembly peephole removes redundant
   temporary copies.

## Purity

Purity is computed as a greatest fixed point over the call graph. A function is
pure when all of its instructions are pure and every callee is pure. Memory
reads are conservatively treated as impure so reads are never moved across
stores. Pure calls can be removed when unused and are eligible for CSE and
lookup tables.

## Interprocedural ranges and loop bounds

`ranges.py` performs a conservative abstract interpretation over integer and
boolean SSA values:

* arithmetic, comparisons, min/max, abs and boolean operators;
* natural-loop induction-variable bounds (e.g. `for i < 10` gives body range
  `0..9`);
* call-site argument ranges propagated into callee parameter ranges;
* widening after a configurable number of visits, with visit/value budgets.

The loop-body bounds are used to specialize calls inside loops. They are never
used to fold the loop's own exit branch.

## Call-site specialization

For every call, the optimizer builds a specification from constant arguments
and inferred ranges. A clone is created only when:

* at least one argument has a useful fact;
* the callee has multiple blocks (single-block bodies are simply inlined);
* the body is under `max_specialized_body`;
* the specialization count is under `max_specializations`.

Each clone has its parameters replaced or constrained, then runs SCCP, range
branch folding, unreachable-block removal, linear-block merging and DCE. A
branch containing side effects that is impossible for this call disappears from
the clone. If the clone collapses to one block, the normal inliner merges it
into the caller, so the caller jumps directly past the eliminated checks.

## Pure constant-call folding and LICM

Calls to pure functions whose arguments are all compile-time constants are
evaluated by the budgeted interpreter and replaced with constants. Loop-
invariant arithmetic, loads proven safe from loop-local mutation, and list
length operations are hoisted by LICM. Calls with non-constant arguments still
fall back to the lookup-table fast path.

## Pure-function lookup tables

After specialization, live pure scalar functions are analyzed for call-site
constants and ranges. The IR interpreter in `puresim.py` evaluates candidate
inputs (bounded by step, call and wall-clock budgets). Successful results are
emitted as:

* a contiguous table for dense observed windows, or
* a small compare chain for sparse values.

The generated function checks the table on entry; misses fall through to the
normal body. The optimization is therefore always semantics-preserving.

## Tunable budgets

All speculative work has a budget in `OptimizerConfig` (`src/optimizer/config.py`).
Environment overrides:

| Variable | Meaning |
| --- | --- |
| `FR_OPT_ITERATIONS` | fixed-point iterations |
| `FR_OPT_INLINE_MAX` | normal inlining size limit |
| `FR_OPT_MAX_SPECIALIZATIONS` | maximum clones per module |
| `FR_OPT_MAX_SPECIALIZED_BODY` | maximum clone source size |
| `FR_OPT_MAX_SPECIALIZED_RANGE` | widest range used for a clone |
| `FR_OPT_RANGE_ITERATIONS` | interprocedural range rounds |
| `FR_OPT_RANGE_VISITS` | abstract interpretation worklist budget |
| `FR_OPT_SIM_STEPS` | compile-time simulation instructions |
| `FR_OPT_SIM_CALLS` | compile-time simulation query budget |
| `FR_OPT_SIM_MS` | per-query simulation wall-clock budget |
| `FR_OPT_TABLE_ENTRIES` | maximum lookup-table entries |
| `FR_OPT_TABLE_DOMAIN` | maximum dense table span |
| `FR_OPT_TABLE_MIN` | minimum entries before emitting a table |

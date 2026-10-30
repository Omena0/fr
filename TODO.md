# Roadmap

## Completed

- Native no-libc runtime: **254/254 native tests pass**.
- Python VM: **325/325 tests pass**.
- C VM: **325/325 tests pass**.
- Freestanding native runtime:
  - real mmap-backed allocator with segregated free lists, `free`, `realloc`
  - `printf` implementation (`%d`, `%ld`, `%s`, `%f`, `%g`, `%x`, `%c`)
  - lists/sets/strings/math/file I/O/process/sleep/input
  - `_setjmp`/`longjmp` based exception handling
- Memory model:
  - reference semantics for structs, lists and sets in all three runtimes
  - C VM reference counting for mutable aggregates
  - Python VM garbage collection
  - native SROA + escape analysis + stack allocation for non-escaping structs
- Language-level pointers:
  - `int*`, `*int`, `int**` types and struct pointer fields
  - `&lvalue`, `*p`, `*p = value`, `**pp = value`
  - pointers to locals, globals, struct fields and list elements
  - automatic dereference for `p.field` and chained `p.next.value`
  - global variables and pointers to globals in all runtimes
- Compiler analysis:
  - call-graph side-effect/purity analysis
  - interprocedural integer/boolean range analysis
  - natural-loop induction-variable bounds
  - branch-sensitive per-call-site specialization with constants and ranges
  - dead branch / unreachable block removal
  - linear block merging and dead function elimination
  - purity-aware DCE/CSE
  - compile-time pure-function simulation with embedded lookup tables
  - tunable budgets for every speculative analysis (`OptimizerConfig`)
- Native reference counting:
  - function allocation scopes
  - retain on global/list/field/pointer/return escapes
  - release on overwrite and scope exit
  - safe stack/string pointer handling via object magic/range checks

## Next

- Collect reference-count cycles (managed object cycles are currently leaked,
  like most RC systems).
- Pointer lifetimes beyond a frame could become a compile-time error rather than
  a documented C-style rule.
- Wasm backend needs the new pointer/global opcodes; it is currently not part of
  the validated test matrix.

## Notes

- `int *args` is still varargs; use `int* p` or `*int p` for pointer params.
- Pointers into a list element are invalidated when the list grows.
- Escaping native heap objects live until process exit.

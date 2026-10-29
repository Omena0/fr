# Benchmarks

The benchmarks are ordinary Fr programs and are not part of the test suite.

## N-body

`nbody.fr` is the correctness-sized run (1,000 steps). `nbody_bench.fr` runs
200,000 steps and is the optimization target: it combines nested loops, struct
field traffic, list indexing/set, floating-point math, calls and reference-
counted heap objects.

```sh
python3 src/cli.py compile bench/nbody_bench.fr -o /tmp/nbody.bc
python3 src/cli.py native /tmp/nbody.bc -o /tmp/nbody -O3
time /tmp/nbody
```

The compiler optimizations validated against this target include scope elision,
LICM, compare/branch fusion, LEA instruction selection, inline list length/list
get fast paths, XMM liveness preservation across calls, pure constant-call
folding, and assembly peepholes. The full test suite (which exercises unrelated
integer, string, struct, list, error and HTTP workloads) is run after every
optimization change.

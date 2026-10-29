# Benchmarks

The benchmarks are ordinary Fr programs and are not part of the test suite.

## Vector reductions

`vector_bench.fr` builds 100,000-element integer and float lists and runs
integer sum, float sum, and float sum-of-squares reductions. The native backend
recognizes these loops and emits AVX2 vector loops with a scalar remainder,
while the Python/C VMs run the same source as scalar loops.

```sh
python3 src/cli.py compile bench/vector_bench.fr -o /tmp/vec.bc
python3 src/cli.py native /tmp/vec.bc -o /tmp/vec -O3
time /tmp/vec
```

## N-body

`nbody.fr` is the correctness-sized run (1,000 steps). `nbody_bench.fr` builds
128 bodies and runs 1,000 steps; it combines nested loops, struct field traffic,
list indexing/set, floating-point math, calls and reference-counted heap
objects. `memory_bench.fr` holds 250,000 reference-counted structs in a list and
walks them, giving a reproducible allocation/RSS measurement.

```sh
python3 src/cli.py compile bench/nbody_bench.fr -o /tmp/nbody.bc
python3 src/cli.py native /tmp/nbody.bc -o /tmp/nbody -O3
time /tmp/nbody
/usr/bin/time -f 'rss_kb=%M elapsed=%e' /tmp/nbody
```

Memory benchmark:

```sh
python3 src/cli.py compile bench/memory_bench.fr -o /tmp/mem.bc
python3 src/cli.py native /tmp/mem.bc -o /tmp/mem -O3
/usr/bin/time -f 'rss_kb=%M elapsed=%e' /tmp/mem
```

The compiler optimizations validated against this target include scope elision,
LICM, compare/branch fusion, LEA instruction selection, inline list length/list
get fast paths, XMM liveness preservation across calls, pure constant-call
folding, and assembly peepholes. The full test suite (which exercises unrelated
integer, string, struct, list, error and HTTP workloads) is run after every
optimization change.

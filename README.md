
# Fr

[![Build](https://github.com/Omena0/fr/actions/workflows/publish.yaml/badge.svg)](https://github.com/Omena0/fr/actions/workflows/publish.yaml)
![Tests](https://github.com/Omena0/fr/actions/workflows/test.yaml/badge.svg)
![LoC](https://img.shields.io/badge/Lines%20Of%20Code-64.9K-red?logo=code)
![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-blue)

Simple bytecode compiled C-style compiled language.

## Installation

```zsh
pip install frscript
```

## Features:

- **Command line launcher** (`fr`)
- **Compiled language** - Fast by design
- **File and Socket I/O** - Low-level file operations and sockets.
- **HTTP library** - A working HTTP/1.1 server/client library in `examples/http/http_lib.fr`, running on all three backends.
- **Multiprocessing**. - Easy threading with fork() and wait().
- **Python integration** - You can use any Python libraries with Frscript.
- **Aggressive optimization** - Purity call-graph analysis, interprocedural ranges, call-site specialization, SROA/escape analysis, pure-function lookup tables and SSA/bytecode optimizations.
- **Deterministic memory** - Reference-counted native structs/lists/sets with function-scope cleanup, plus SROA and stack allocation for non-escaping values.
- **Modern memory model** - Reference-semantics structs/lists/sets, scope-based reference counting, automatic stack allocation for non-escaping values, and a free-list native allocator.
- **Opt-in pointers** - `int*`, `&value`, `*p`, pointer fields and pointer parameters, lowered directly to addresses in native code.
- **Stack-based VM** - Fast and memory efficient.
- **Readable bytecode** - Optimize hot code manually
- **WASM Backend** - Run sandboxed code in web browsers.

## Benchmarks:

### Pi_1k

This benchmark computes 1000 digits of pi.

```text
Python: 0.326s
Py VM: DNF
C VM: 64.62s
Native: 0.034s
```

### Fibonacci

This benchmark computes the 1-billionth fibonacci number in mod 1 000 000.

```text
Python: 40.227s
Py VM: DNF
C VM: 31.654s
Native: 4.483s
```

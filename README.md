
# Fr

[![Build](https://github.com/Omena0/fr/actions/workflows/publish.yaml/badge.svg)](https://github.com/Omena0/fr/actions/workflows/publish.yaml)
![Tests](https://github.com/Omena0/fr/actions/workflows/test.yaml/badge.svg)
![LoC](https://img.shields.io/badge/Lines%20Of%20Code-68.3K-red?logo=code)
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
- **Multiprocessing**. - Easy threading with fork() and wait().
- **Python integration** - You can use any Python libraries with Frscript.
- **Aggressive optimization** - Bytecode-level optimizations. Faster than python.
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

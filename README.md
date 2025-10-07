

# Fr

[![Build](https://github.com/Omena0/fr/actions/workflows/publish.yaml/badge.svg)](https://github.com/Omena0/fr/actions/workflows/publish.yaml)
![Tests](https://github.com/Omena0/fr/actions/workflows/test.yaml/badge.svg)
![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-blue)
![AI Code](https://img.shields.io/badge/AI_code-59%25-red?logo=Github%20copilot)

Simple bytecode compiled C-style scripting language.

## Installation

```zsh
pip install frscript
```

Features:
- Launcher (`fr`)
- **Really fast.** High-performance C runtime VM with aggressive optimizations. Parse-time function evaluation, loop unrolling and inlining. Bytecode-level optimizations such as fused operations.
- **Dual Runtime System.** Choose between the fast C VM runtime or the Python runtime for debugging and development.
- Batteries included. Lots of features out-of-the-box. No libraries required.
- **File and Socket I/O**. Low-level file operations and sockets.
- Python integration - You can use any Python libraries with Frscript.


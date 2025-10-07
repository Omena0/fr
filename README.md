

# Fr

[![Build](https://github.com/Omena0/fr/actions/workflows/publish.yaml/badge.svg)](https://github.com/Omena0/fr/actions/workflows/publish.yaml)
![Tests](https://github.com/Omena0/fr/actions/workflows/test.yaml/badge.svg)
![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-blue)
![AI Code](https://img.shields.io/badge/AI_code-59%25-red?logo=Github%20copilot)

Simple bytecode compiled C-style scripting language.

## Installation

### Quick Install (Recommended)

The easiest way to install Frscript globally is using the installation script:

```bash
./install.sh
```

This script will:
- Check if `pipx` is available (recommended for isolated Python app installations)
- Fall back to `pip --user` if pipx is not available
- Install the `fr` command globally for your user
- Provide instructions for adding to PATH if needed

### Manual Installation

#### Using pipx (Recommended)
```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install Frscript
pipx install -e .
```

#### Using pip --user
```bash
pip3 install --user -e .

# Add ~/.local/bin to your PATH if not already there
export PATH="$HOME/.local/bin:$PATH"
```

### Verify Installation

```bash
fr --help
```

Features:
- Launcher (`fr`)
- Really fast. Fast C runtime and parse time function evaluation, loop unrolling and inlining.
Bytecode-level optimizations such as fused operations.
- Batteries included. Lots of features out-of-the-box. No libraries required.
- **File and Socket I/O**. Low-level file operations and sockets..
- Python integration - You can use any Python libraries with Frscript.


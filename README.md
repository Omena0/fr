

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

### C Runtime Build

Frscript includes a high-performance C-based virtual machine that is automatically built during installation. 

**Build Requirements:**
- C compiler (gcc or clang)
- Python development headers (`python3-dev` or `python3-devel`)
- GMP library (`libgmp-dev` or `gmp-devel`)

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python3-dev libgmp-dev
```

**Arch Linux:**
```bash
sudo pacman -S base-devel python gmp
```

If the automatic build fails during installation, you can build the C runtime manually:
```bash
cd runtime
make
```

For detailed build instructions and troubleshooting, see [BUILD_GUIDE.md](BUILD_GUIDE.md).

Features:
- Launcher (`fr`)
- **Really fast.** High-performance C runtime VM with aggressive optimizations. Parse-time function evaluation, loop unrolling and inlining. Bytecode-level optimizations such as fused operations.
- **Dual Runtime System.** Choose between the fast C VM runtime or the Python runtime for debugging and development.
- Batteries included. Lots of features out-of-the-box. No libraries required.
- **File and Socket I/O**. Low-level file operations and sockets.
- Python integration - You can use any Python libraries with Frscript.


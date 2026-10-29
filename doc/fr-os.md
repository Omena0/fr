# Compiling for Fr OS

The native backend can emit a static userspace ELF for
[Fr OS](https://github.com/Omena0/fr-os/).

```sh
python3 src/cli.py compile examples/fr-os/hello.fr -o /tmp/hello.bc
python3 src/cli.py native /tmp/hello.bc -o /tmp/hello.elf --target fr-os
```

The result is:

* `ET_EXEC`, `EM_X86_64`, no `PT_INTERP`;
* linked at the normal userspace base (`0x400000`);
* entered through the global `_start` symbol;
* freestanding (no host libc, no dynamic linker);
* restricted to the Fr OS user ISA profile: SSE2/XMM is allowed, but AVX/AVX2,
  FMA and YMM/ZMM are not emitted. Autovectorization is therefore disabled for
  this target, and the runtime is compiled with `-mno-avx -mno-avx2 -mno-fma`
  plus `-mno-red-zone`.

## Syscall ABI

The target uses the numbers in Fr OS's `src/include/uapi/syscall.h`:

| Operation | Fr OS number |
| --- | --- |
| `read` | 66 |
| `write` | 67 |
| `open` | 64 |
| `close` | 65 |
| `lseek` | 68 |
| `fstat` | 69 |
| `getdents` | 71 |
| `mmap` | 32 |
| `exit` | 2 |
| `fork` | 0 |
| `wait4` | 4 |
| `getpid` | 5 |
| `nanosleep` | 13 |

The current Fr OS tree only assigns `SYS_socket = 160` and
`SYS_shutdown = 206`; the documented bind/connect/listen/accept/send/recv
numbers are not in the current dispatch table yet. The target uses 161–167 for
those goal-ABI calls, so they return `-ENOSYS` on the current kernel.

## Known target limitations

The Fr OS `uapi/syscall.h` currently assigns `fstat = 69` and `getdents = 71`,
while `docs/src/kernel/syscall-abi.md` describes a different numbering
(`stat = 69`, `fstat = 70`, `mkdir = 71`, ...). The new `SYS_shutdown = 206`
also differs from the docs goal's 168. This target follows the uapi
header because that is what the kernel actually dispatches. Path-based
filesystem operations that have no current uapi number (`mkdir`, `rmdir`,
`unlink`, `rename`, `chdir`, `getcwd`) return `-1` in the runtime until the
kernel ABI grows them. `open` is currently a stub in Fr OS and returns
`-ENOENT`, so file tests do not succeed on the current kernel even though the
binary is valid.

Fr OS userland forbids YMM/ZMM because its context switch uses the legacy
FXSAVE/FXRSTOR image. The compiler's AVX2 vectorizer is deliberately disabled
for this target; use `--target linux` for the AVX2 path.

## Fr OS updates observed

The latest Fr OS tree adds termios/TCSETS handling, user signal dispositions and
delivery, `uname`/`sysinfo`, `getrlimit`/`setrlimit`, fd flags with `dup3` and
`fcntl`, keyboard/mouse input state, graphics presentation, and a `shutdown`
syscall at number 206. The target follows the current `uapi/syscall.h` for all
of these (notably `SYS_shutdown = 206`).

`open` is still a stub returning `-ENOENT`, and the current dispatch table only
assigns `SYS_socket = 160`; the documented bind/connect/listen/accept/send/recv
numbers are future ABI. The compiler keeps those calls behind the goal-ABI
numbers so they will start working when the kernel installs them, but they
return `-ENOSYS` today.

## Checking an image

Use Fr OS's own verifier:

```sh
python3 /path/to/fr-os/tools/verify_isa.py --profile user /tmp/hello.elf
```

The generated image should report that it stays inside the 128-bit XMM state.

# Fr OS example

Build a static Fr OS userspace ELF:

```sh
python3 src/cli.py compile examples/fr-os/hello.fr -o /tmp/hello.bc
python3 src/cli.py native /tmp/hello.bc -o /tmp/hello.elf --target fr-os
```

Put `/tmp/hello.elf` into filesystem/bin and build.

See `doc/fr-os.md` for the ABI and target limitations.

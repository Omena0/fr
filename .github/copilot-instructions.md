
# Copilot guide

Make sure you know the language syntax before writing code.

Avoid creating "patches" or "placeholders", prefer full, complete, robust solutions that are easy to maintain and read.

Make sure to create tests for new functionality.
Also update the vscode extension with the new features.

If any tests fail or there are errors, fix it. There were no "existing errors", everything worked before your session. ALL tests must pass after you're done. Not just related ones.

Create a changelog without any formatting or emojis in changes.txt like in the README's "What's new" section,
do not categorize them, just make a big list. Do not edit the actual README, only edit changes.txt.
Do not add useless lines into the changelog, e.g. defining a constant or implementing the same feature
in each file separately does not warrant another line.

If adding a new bytecode instruction, remember to update doc/vm_instructions.md.

Clean up after you're done.

## Workspace-specific details

src/cli.py is installed via alias as `fr` command.
src/run_single_test.py expects code into stdin, not a file argument

The project uses a virtual environment at `.venv`, vscode might not activate it automatically for you.

## How to use the cli

```cli
➜  lang2 git:(main) ✗ fr
Fr - Fast bytecode-compiled language

Usage:
  fr <file.fr> [-c] [-py|--python] [-O|--optimize] - Run the file
                                    -c: Force C runtime
                                    -py: Force Python runtime
  fr parse <file.fr> [--json]       - Parse to AST (binary or JSON)
  fr compile <file.fr|ast.json|ast.bin> [-o out.bc] - Compile to bytecode
  fr native <file.bc> [-o out] [-a|--asm] - Compile bytecode to native binary

Defaults to C runtime unless source has untyped funcs.
```

it will always try to use the C runtime over python.
parse creates `out.bin`
compile creates `out.bc`

!! DO NOT COMMIT EVER !!
(unless you're on a branch other than main)

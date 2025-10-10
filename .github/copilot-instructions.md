Make sure you know the language syntax before writing code.

Avoid creating "patches" or "placeholders", prefer full, complete, robust solutions that are easy to maintain and read.

Make sure to create tests for new functionality.
Also update the vscode extension with the new features.

If any tests fail you have to fix it.

Create a changelog without any formatting or emojis in changes.txt like in the README's "What's new" section,
do not categorize them, just make a big list. Do not edit the actual README, only edit changes.txt.
Do not add useless lines into the changelog, e.g. defining a constant or implementing the same feature
in each file separately does not warrant another line.

If there already is content and it is from a previous commit, overwrite the file.

If adding a new bytecode instruction, remember to update doc/vm_instructions.md.

Clean up after you're done.

"""Minimal peephole optimizer for x86_64 assembly.

Applies simple pattern-based cleanup to the assembly output. Only ~12 patterns
are needed because the SSA IR optimizer + register allocator already produce
clean code. This just catches the few remaining inefficiencies.
"""
from __future__ import annotations
import re


def peephole_optimize(asm_lines: list[str], passes: int = 3) -> list[str]:
    """Run peephole optimization patterns over assembly lines."""
    for _ in range(passes):
        changed = False
        new_lines = []
        i = 0
        while i < len(asm_lines):
            # Try each pattern
            consumed, replacement = _try_patterns(asm_lines, i)
            if consumed > 0:
                new_lines.extend(replacement)
                i += consumed
                changed = True
            else:
                new_lines.append(asm_lines[i])
                i += 1
        asm_lines = new_lines
        if not changed:
            break
    return asm_lines


def _try_patterns(lines: list[str], i: int) -> tuple[int, list[str]]:
    """Try to match and replace patterns starting at index i.
    Returns (number of lines consumed, replacement lines) or (0, [])."""

    line = lines[i].strip()

    # ── Pattern 1: mov rX, rX (self-move) → eliminate ──
    m = re.match(r'mov\s+(\w+),\s*(\w+)', line)
    if m and m.group(1) == m.group(2):
        return (1, [])

    # ── Pattern 2: movsd xmmN, xmmN (self-move) → eliminate ──
    m = re.match(r'movsd\s+(xmm\d+),\s*(xmm\d+)', line)
    if m and m.group(1) == m.group(2):
        return (1, [])

    # ── Pattern 3: mov rX, A ; mov A, rX → mov rX, A ──
    if i + 1 < len(lines):
        line2 = lines[i + 1].strip()
        m1 = re.match(r'mov\s+(\w+),\s*(.+)', line)
        m2 = re.match(r'mov\s+(\w+),\s*(.+)', line2)
        if m1 and m2:
            if m1.group(1) == m2.group(2) and m1.group(2) == m2.group(1):
                return (2, [lines[i]])

    # ── Pattern 4: add rX, 0 → eliminate ──
    m = re.match(r'add\s+(\w+),\s*0$', line)
    if m:
        return (1, [])

    # ── Pattern 5: sub rX, 0 → eliminate ──
    m = re.match(r'sub\s+(\w+),\s*0$', line)
    if m:
        return (1, [])

    # ── Pattern 6: imul rX, 1 → eliminate ──
    m = re.match(r'imul\s+(\w+),\s*1$', line)
    if m:
        return (1, [])

    # ── Pattern 7: mov rX, 0 → xor eX, eX (faster zero) ──
    m = re.match(r'mov\s+(r\w+),\s*0$', line)
    if m:
        reg = m.group(1)
        dword_map = {
            'rax': 'eax', 'rbx': 'ebx', 'rcx': 'ecx', 'rdx': 'edx',
            'rsi': 'esi', 'rdi': 'edi', 'r8': 'r8d', 'r9': 'r9d',
            'r10': 'r10d', 'r11': 'r11d', 'r12': 'r12d', 'r13': 'r13d',
            'r14': 'r14d', 'r15': 'r15d',
        }
        if reg in dword_map:
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            return (1, [f'{indent}xor {dword_map[reg]}, {dword_map[reg]}'])

    # ── Pattern 8: jmp to next label → eliminate ──
    if i + 1 < len(lines):
        m = re.match(r'jmp\s+(\.\w+)', line)
        if m:
            next_line = lines[i + 1].strip()
            if next_line == f'{m.group(1)}:':
                return (1, [])

    # ── Pattern 9: push rX ; pop rX → eliminate ──
    if i + 1 < len(lines):
        m1 = re.match(r'push\s+(\w+)', line)
        line2 = lines[i + 1].strip()
        m2 = re.match(r'pop\s+(\w+)', line2)
        if m1 and m2 and m1.group(1) == m2.group(1):
            return (2, [])

    # ── Pattern 10: push rX ; pop rY → mov rY, rX ──
    if i + 1 < len(lines):
        m1 = re.match(r'push\s+(\w+)', line)
        line2 = lines[i + 1].strip()
        m2 = re.match(r'pop\s+(\w+)', line2)
        if m1 and m2 and m1.group(1) != m2.group(1):
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            return (2, [f'{indent}mov {m2.group(1)}, {m1.group(1)}'])

    # ── Pattern 11: shl rX, 0 → eliminate ──
    m = re.match(r'(shl|shr|sar)\s+(\w+),\s*0$', line)
    if m:
        return (1, [])

    # ── Pattern 12: test rX, rX ; jz L ; jmp L2 ; L: → jnz L2 ; L: ──
    if i + 3 < len(lines):
        m0 = re.match(r'test\s+(\w+),\s*(\w+)', line)
        m1 = re.match(r'jz\s+(\.\w+)', lines[i + 1].strip()) if m0 else None
        m2 = re.match(r'jmp\s+(\.\w+)', lines[i + 2].strip()) if m1 else None
        m3_line = lines[i + 3].strip() if m2 else ''
        if m0 and m1 and m2 and m0.group(1) == m0.group(2) and \
                m3_line == f'{m1.group(1)}:':
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            return (3, [
                lines[i],  # keep the test
                f'{indent}jnz {m2.group(1)}',
            ])

    return (0, [])


def optimize_asm_text(asm_text: str) -> str:
    """Optimize assembly text (convenience wrapper)."""
    lines = asm_text.split('\n')
    optimized = peephole_optimize(lines)
    return '\n'.join(optimized)

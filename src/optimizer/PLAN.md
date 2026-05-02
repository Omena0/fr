# Fr Superoptimizer

A synthesis-driven optimizing compiler backend that uses SMT solving to discover
provably optimal code sequences. Replaces the stack-based native compiler with an
SSA IR pipeline, direct-pointer structs, full register allocation, and a Souper-style
superoptimizer that mathematically proves code transformations correct.

## Design Goal

The fastest possible native code for fr's semantics. Not "competitive with C" — faster
than C on the patterns fr programs use, by exploiting guarantees C compilers can't:

- **No pointer aliasing.** Ever. Two struct references never alias. The optimizer can
  cache, reorder, and eliminate memory accesses that C must keep.
- **Whole-program visibility.** Every function, every call site, every type is known.
  Full inlining, full devirtualization, full interprocedural analysis — by default.
- **Simple semantics.** No undefined behavior, no volatile, no signals, no setjmp.
  Every transformation that's semantically valid is safe to apply.
- **SMT-verified rewrites.** Instead of hand-written peephole patterns, use a solver
  to discover optimal instruction sequences that no human would write.

## Architecture

```
Source (.fr)
    |
    v
[Parser] ── AST ──> [Compiler] ── Bytecode ──> [Python VM / C VM / WASM]
                                      |           (unchanged, bytecode path)
                                      v
                               [IR Builder]
                                      |
                               SSA IR (typed, direct-pointer structs)
                                      |
                     ┌────────────────┼────────────────┐
                     v                v                 v
              [Type Inference]  [Escape Analysis]  [Dominator Tree]
              [Liveness]        [Loop Detection]   [Alias Analysis]
                     |                |                 |
                     └────────────────┼────────────────┘
                                      v
                            [Optimization Passes]
                              1. SCCP (const prop + dead branch)
                              2. Algebraic simplification
                              3. SROA (scalar replacement of aggregates)
                              4. CSE (common subexpression elimination)
                              5. LICM (loop-invariant code motion)
                              6. Strength reduction
                              7. Function inlining
                              8. DCE (dead code elimination)
                              9. Tail call optimization
                                      |
                                      v
                            [Superoptimizer]
                              - Extract instruction windows
                              - Encode as SMT bitvector formulas
                              - Synthesize cheaper equivalents
                              - Verify with Z3: forall inputs, new == old
                              - Cache proven rewrites
                                      |
                                      v
                            [Register Allocator]
                              - Linear scan over all 14 GPRs + 16 XMMs
                              - Spill weight = loop depth * use count
                              - Rematerialization for constants
                              - Calling convention aware
                                      |
                                      v
                            [x86_64 Code Emitter]
                              - Direct register-to-register ops
                              - Inline struct access (pointer + offset)
                              - Minimal stack frame
                              - ABI-correct calls
                                      |
                                      v
                            [Peephole] ── .asm ──> gcc ──> binary
```

## Struct Redesign

### Current (slow)

Structs live in a 64MB BSS block. Each instance gets 256 bytes. References are encoded
as `(instance_id << 16) | struct_id`. Every field access decodes this:

```asm
mov rbx, rax          ; copy reference
shr rbx, 16           ; extract instance_id
cmp rbx, 262144       ; bounds check
jb .ok
and rbx, 0x3FFFF      ; wrap
.ok:
shl rbx, 8            ; * 256 (slot size)
add rbx, FIELD_OFFSET
lea rdx, [rip + struct_data]
mov result, [rdx + rbx]     ; finally load the field
```
= 8-10 instructions per field access. Repeated for every access.

### New (fast)

Structs are contiguous memory at a direct pointer. Field access is one instruction.

**Layout:** Fields packed sequentially, 8 bytes each (uniform for simplicity).
```
struct Ball { int x; int y; float dx; float dy; int radius; }

Memory:  [x:8][y:8][dx:8][dy:8][radius:8] = 40 bytes
Offset:   0    8    16    24    32
```

A struct reference is a raw 64-bit pointer to the first field.

**Field access:**
```asm
mov rax, [struct_ptr + 8]    ; load field at offset 8 (field index 1)
```
= 1 instruction. Always.

**Allocation strategy (3 tiers, chosen by escape analysis):**

**Tier 1 — SROA (zero cost).** If the struct doesn't escape the function and has ≤ 8
fields, replace it with individual SSA values. No memory allocation, no memory access.
Fields live in registers.
```
Point p = Point(3, 4)    →    %px = 3; %py = 4
p.x + p.y               →    %result = ADD_I64 %px, %py
```
This is the common case for local structs.

**Tier 2 — Stack allocation (near-zero cost).** If the struct escapes to callees but
doesn't outlive the function (not returned, not stored in heap structures), allocate it
on the stack frame.
```asm
; In function prologue, struct at [rbp - 48] (5 fields × 8 = 40, aligned to 48)
lea rdi, [rbp - 48]          ; pointer to struct
mov qword ptr [rdi + 0], 3   ; x = 3
mov qword ptr [rdi + 8], 4   ; y = 4
```
Access: `mov rax, [rbp - 40]` — same speed as local variables.

**Tier 3 — Bump allocation (very cheap).** If the struct escapes the function (returned,
stored in a list, assigned to a global), allocate from a bump allocator.
```asm
mov rax, [rip + heap_ptr]    ; current allocation pointer
add qword ptr [rip + heap_ptr], 40   ; advance by struct size
; rax now points to the new struct
```
= 2 instructions to allocate (vs malloc's ~100). No free needed — the bump allocator
arena is reset periodically or at program exit for short-lived programs. For long-running
programs, a simple mark-sweep collector can compact the arena.

**Struct type ID:** When the program needs to know a struct's type at runtime (rare — only
for printing, dynamic dispatch), store a type tag in the first 8 bytes and shift all field
offsets by 8. But for statically-typed code (the common case), the type is known at compile
time and no tag is needed.

### Impact

| Operation | Current | New (Tier 1) | New (Tier 2) | New (Tier 3) |
|---|---|---|---|---|
| Allocate | 4 insns | 0 insns | 1 insn (lea) | 2 insns (bump) |
| Field read | 8-10 insns | 0 insns (register) | 1 insn | 1 insn |
| Field write | 8-10 insns | 0 insns (register) | 1 insn | 1 insn |
| Pass to function | push encoded ref | pass in register | pass pointer in reg | pass pointer in reg |

## Memory Management

**Integers, floats, bools:** Always in registers. Never heap-allocated.

**Strings:** Pointer to null-terminated data in .rodata (literals) or heap (runtime-created).
String operations (concat, slice, format) allocate via the bump allocator. Immutable — concat
creates a new string, doesn't modify either input.

**Lists:** Heap-allocated header + contiguous element array. Typed: `list[int]` stores raw
int64s (8 bytes each), `list[str]` stores pointers. No boxing.

**Bump allocator design:**
```
Arena: [=========allocated=========|----free----|]
       ^                           ^             ^
    arena_base                  heap_ptr      arena_end
```
Allocation is `heap_ptr += size; return old heap_ptr`. Two instructions.
When arena is full, allocate a new arena (double size) and chain them.
For long-running programs, a simple collector walks live references and compacts.
For short-lived programs (benchmarks, scripts), just let the OS reclaim on exit.

## SSA IR

Every value is assigned exactly once. No mutable variables — instead, new versions
and phi nodes at control flow merge points.

### Types

```python
class IRType:
    INT64    # 64-bit signed integer
    FLOAT64  # 64-bit IEEE double
    BOOL     # 1-bit boolean (stored as 64-bit in registers)
    STRING   # pointer to null-terminated string
    STRUCT   # pointer to struct instance (with struct_name metadata)
    LIST     # pointer to list header (with element type metadata)
    VOID     # no value
```

### Instructions

Every instruction produces at most one value and consumes zero or more values.

```
# Constants
%0 = CONST_INT 42
%1 = CONST_FLOAT 3.14
%2 = CONST_STR "hello"
%3 = CONST_BOOL true

# Arithmetic (int)
%4 = ADD %a, %b          # int64 + int64 → int64
%5 = SUB %a, %b
%6 = MUL %a, %b
%7 = DIV %a, %b          # checked division (trap on zero)
%8 = MOD %a, %b
%9 = NEG %a

# Arithmetic (float)
%10 = FADD %a, %b        # float64 + float64 → float64
%11 = FSUB %a, %b
%12 = FMUL %a, %b
%13 = FDIV %a, %b
%14 = FNEG %a

# Comparison (works for both int and float)
%15 = LT %a, %b          # → bool
%16 = GT %a, %b
%17 = LE %a, %b
%18 = GE %a, %b
%19 = EQ %a, %b
%20 = NE %a, %b

# Logic
%21 = AND %a, %b
%22 = OR %a, %b
%23 = NOT %a

# Bitwise
%24 = SHL %a, %b         # shift left
%25 = SHR %a, %b         # arithmetic shift right
%26 = BIT_AND %a, %b
%27 = BIT_OR %a, %b
%28 = BIT_XOR %a, %b

# Struct operations (with new direct-pointer model)
%30 = ALLOC_STRUCT <type_name>    # returns pointer (tier chosen by escape analysis)
      STORE_FIELD %ptr, <idx>, %val   # ptr[idx] = val (void)
%31 = LOAD_FIELD %ptr, <idx>         # val = ptr[idx]

# List operations
%32 = ALLOC_LIST <elem_type>
%33 = LIST_GET %list, %index
      LIST_SET %list, %index, %val
      LIST_APPEND %list, %val
%34 = LIST_LEN %list

# String operations
%35 = STR_CONCAT %a, %b
%36 = STR_LEN %a

# Type conversion
%37 = INT_TO_FLOAT %a
%38 = FLOAT_TO_INT %a
%39 = TO_STR %a           # any → string
%40 = STR_TO_INT %a

# Function calls
%41 = CALL <func_name> (%arg0, %arg1, ...)
%42 = CALL_EXTERN <func_name> (%arg0, %arg1, ...)   # C FFI
%43 = CALL_BUILTIN <name> (%arg0, ...)               # print, len, etc.

# Control flow (block terminators only)
      BRANCH %cond, label_true, label_false
      JUMP label
      RETURN %val
      RETURN_VOID

# SSA
%44 = PHI (%val_from_block_A, block_A), (%val_from_block_B, block_B)
```

### Basic Blocks and CFG

```
function updateBall(ball: struct Ball) -> void:
  entry:
    %dt = CALL_EXTERN GetFrameTime ()
    %x = LOAD_FIELD %ball, 0            # ball.x
    %dx = LOAD_FIELD %ball, 2           # ball.dx
    %new_x_f = FMUL %dx, %dt
    %new_x_i = FLOAT_TO_INT %new_x_f
    %x2 = ADD %x, %new_x_i
    STORE_FIELD %ball, 0, %x2           # ball.x = x2
    %cmp = LT %x2, 0
    BRANCH %cmp, bounce, done

  bounce:
    %neg_dx = FNEG %dx
    STORE_FIELD %ball, 2, %neg_dx       # ball.dx = -dx
    JUMP done

  done:
    RETURN_VOID
```

## Superoptimizer (Synthesis Engine)

### What It Is

A Souper-style superoptimizer that uses an SMT solver (Z3) to discover provably optimal
rewrites for instruction sequences. Instead of pattern-matching known optimizations, it
*searches* for them mathematically.

### How It Works

**Step 1: Harvest instruction windows.**

Walk the optimized IR. For each instruction that computes a value, extract its "cone of
influence" — the minimal set of instructions needed to compute it, up to a configurable
depth (default: 6 instructions, max: 10).

Example:
```
%0 = CONST_INT 1
%1 = SHL %x, %0       # x << 1
%2 = ADD %x, %1       # x + (x << 1) = x * 3
```
This is a 3-instruction window computing `%2` from input `%x`.

**Step 2: Encode as SMT formula.**

Express the computation as Z3 bitvector operations:
```python
x = BitVec('x', 64)
v0 = BitVecVal(1, 64)
v1 = x << v0            # SHL
v2 = x + v1             # ADD
# v2 represents the output
```

**Step 3: Enumerate candidate replacements by cost.**

Generate candidate expressions, cheapest first:
- Cost 0: just `x` (identity), or a constant
- Cost 1: `x + x`, `x * 2`, `x << 1`, `x - 0`, ...
- Cost 2: `x * 3`, `x * C` for small C, `(x << 1) + x`, ...
- Cost 3: more complex expressions

For each candidate, ask Z3:
```python
solver.add(ForAll([x], v2 == candidate))
if solver.check() == sat:
    # candidate is equivalent — use it!
```

For the example above, Z3 would prove that `x * 3` is equivalent to `x + (x << 1)`.
The cost of `MUL x, 3` is 1 instruction (which maps to `lea rax, [rax + rax*2]` on x86).
The original was 2 instructions. We save one instruction.

**Step 4: Cache the rewrite.**

Store the proven rewrite: `(SHL x, 1) + x → MUL x, 3`. Next time this pattern appears
(in any program), apply it instantly without calling Z3.

The cache is a dictionary mapping normalized instruction patterns to their optimal
replacements. It persists across compilations (saved to disk) and grows over time.

### What It Finds That Traditional Passes Miss

1. **Multi-instruction algebraic identities:**
   `(x & 0xFF) | ((y & 0xFF) << 8)` → `PACK_BYTES x, y` (if we have such an op) or
   optimal shift/mask sequence.

2. **Bit manipulation tricks:**
   `x / 2` where x is known non-negative → `SHR x, 1` (the division pass might not
   know about the non-negativity, but the SMT solver sees it from the constraints).

3. **Redundant computation across branches:**
   If both branches of an if-else compute parts of the same expression, the superoptimizer
   can find the common subexpression even when CSE can't (because CSE only looks within
   dominator trees).

4. **Strength reduction compositions:**
   `x * 7` → `(x << 3) - x` (3 instructions with naive mul, 2 with composition).
   Traditional strength reduction knows `x * 8 = x << 3` but not always the subtraction trick.
   The SMT solver discovers it automatically.

5. **Conditional simplification:**
   `if (x > 0) { y = x } else { y = -x }` → `y = abs(x)` → on x86:
   `mov rbx, rax; sar rbx, 63; xor rax, rbx; sub rax, rbx` (branchless, 4 insns).
   No traditional pass converts branching code to branchless — the solver can.

### Practical Limits

- **Window size:** Max 10 instructions. Larger windows make Z3 slow.
- **Timeout:** 100ms per query. Skip if Z3 can't solve in time.
- **When to run:** Only at -O3. -O1/-O2 skip synthesis entirely.
- **Candidate generation:** Smart enumeration, not brute force. Start with cheapest
  expressions, stop when we find one cheaper than the original.
- **Cache hit rate:** After compiling a few programs, most common patterns are cached.
  Compilation speed approaches normal after warmup.

### Rewrite Cache Format

```python
# Key: canonical pattern (op, operand_pattern, ...)
# Value: replacement pattern + cost savings
{
    ('ADD', ('SHL', 'x', 1), 'x'): ('MUL', 'x', 3),           # cost 2 → 1
    ('SUB', 'x', 'x'): ('CONST_INT', 0),                       # cost 1 → 0
    ('MUL', 'x', ('CONST_INT', 2)): ('SHL', 'x', 1),           # cost 1 → 1 (but SHL is faster)
    ('DIV', 'x', ('CONST_INT', 4)): ('SHR', 'x', 2),           # cost 1 → 1 (DIV is 20+ cycles)
}
```

The cache lives at `~/.cache/fr/synthesis_cache.json` and is loaded at startup.

## Register Allocation

### Available Registers

```
General purpose (14):
  Caller-saved: rax, rcx, rdx, rsi, rdi, r8, r9, r10, r11
  Callee-saved: rbx, r12, r13, r14, r15

Floating point (16):
  xmm0 - xmm15 (all caller-saved)

Reserved:
  rsp (stack pointer), rbp (frame pointer)
```

The current compiler uses only r12-r15 (4 registers). We use all 14 GPRs + 16 XMMs.

### Algorithm: Linear Scan

1. **Compute liveness intervals:** For each SSA value, determine the range of instruction
   indices where it's live (from definition to last use). Values used in loops have their
   interval extended to cover the entire loop body.

2. **Sort by start point.**

3. **Scan forward,** maintaining an "active" set of currently-allocated intervals:
   - Expire intervals that ended before the current point → free their registers
   - Try to allocate a register for the current interval:
     - Prefer callee-saved registers for values live across CALL instructions
     - Prefer caller-saved registers for short-lived scratch values
     - If no register available, spill the value with the highest cost
       (cost = spill_weight / remaining_interval_length)

4. **Insert spill/reload code:**
   - Spill: `mov [rbp - offset], reg` at point of spill
   - Reload: `mov reg, [rbp - offset]` at point of use
   - For constants: rematerialize (`mov reg, imm`) instead of memory load

5. **Resolve phi nodes:**
   - For each phi: if all incoming values are in the same register, no code needed
   - If different registers: insert `mov` at the end of predecessor blocks
   - Use parallel copy decomposition to handle cycles

### Calling Convention (System V AMD64)

**Arguments:** First 6 integer/pointer args in rdi, rsi, rdx, rcx, r8, r9.
First 8 float args in xmm0-xmm7. Remaining on stack.

**Return:** Integer/pointer in rax. Float in xmm0.

**Preservation:** rbx, r12-r15, rbp, rsp are callee-saved.

**The allocator plans around calls:**
- Before CALL: live values in caller-saved registers are saved to stack (or moved to
  callee-saved registers if available — this avoids the save/restore entirely)
- Function arguments are placed in the correct ABI registers directly from their
  allocated registers (if arg is already in rdi, no mov needed)
- Return value is placed in rax; if the target register is rax, no mov needed

## Code Emitter

### Instruction Mapping

Each IR instruction maps to 1-3 x86_64 instructions. Because values are in registers,
there's no stack traffic.

```
IR                          x86_64
─────────────────────────────────────────────────
%c = ADD %a, %b             mov Rc, Ra          (if Rc != Ra)
                            add Rc, Rb

%c = ADD %a, %b             add Ra, Rb          (if Rc == Ra, destructive)

%c = MUL %a, 3              lea Rc, [Ra + Ra*2] (strength-reduced)

%c = LOAD_FIELD %p, 2       mov Rc, [Rp + 16]   (ONE instruction)

%c = LT %a, %b              cmp Ra, Rb
                            setl Rc_byte
                            movzx Rc, Rc_byte

BRANCH %cond, T, F          test Rcond, Rcond
                            jnz .T
                            jmp .F

CALL foo (%a, %b)           mov rdi, Ra         (if Ra != rdi)
                            mov rsi, Rb         (if Rb != rsi)
                            call foo

ALLOC_STRUCT Ball           mov Rc, [rip + heap_ptr]
                            add qword ptr [rip + heap_ptr], 40
```

### Function Prologue

```asm
func_name:
    push rbp
    mov rbp, rsp
    sub rsp, FRAME_SIZE        ; only what's actually needed (spill slots)
    ; save only callee-saved registers that are used
    mov [rbp - 8], rbx         ; only if rbx is allocated
    mov [rbp - 16], r12        ; only if r12 is allocated
    ; ... etc
```

FRAME_SIZE is computed from: number of spill slots × 8, aligned to 16 bytes.
Leaf functions (no calls) can omit `push rbp / mov rbp, rsp` entirely and use
rsp-relative addressing.

### vs. Current Output

```
Current updatePaddle (40+ lines just for 2 struct accesses):
    push r12         ; LOAD struct
    pop rax
    mov rbx, rax
    shr rbx, 16      ; decode instance_id
    cmp rbx, 262144  ; bounds check
    jb .ok
    and rbx, 0x3FFFF
    .ok:
    mov rax, rbx
    shl rax, 8       ; * 256
    add rax, 8       ; + field offset
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    ... (repeat for every field access)

New updatePaddle:
    mov rax, [rdi + 8]    ; paddle.y — done
    mov rbx, [rdi + 32]   ; paddle.speed — done
```

## Modules

```
src/optimizer/
├── __init__.py          # Pipeline entry point: optimize_native(bytecode, struct_defs)
├── PLAN.md              # This document
├── ir.py                # SSA IR data structures (Module, Function, Block, Instruction)
├── ir_builder.py        # Bytecode → SSA IR (stack simulation + SSA construction)
├── types.py             # Type system and lattice-based type inference
├── analysis.py          # Dominator tree, liveness, loops, escape analysis, alias analysis
├── passes.py            # SCCP, DCE, CSE, LICM, SROA, strength reduction, inlining, TCO
├── synthesis.py         # SMT superoptimizer (Z3-based instruction synthesis)
├── regalloc.py          # Linear scan register allocator (14 GPR + 16 XMM)
├── codegen.py           # x86_64 assembly emitter (from register-allocated IR)
├── peephole.py          # Minimal assembly cleanup (~12 patterns)
└── bytecode_opt.py      # Existing bytecode optimizer (moved from src/optimizer.py)
```

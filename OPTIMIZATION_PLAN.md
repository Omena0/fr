# VM.C Optimization Implementation Plan

## Overview
This document outlines the comprehensive optimization strategy for vm.c, ordered by impact and risk level.

---

## Phase 1: Dispatch Table Optimization ⚡ HIGH IMPACT
**Status:** ✅ Partially Complete (Alignment added)
**Risk:** LOW
**Expected Performance Gain:** 1-2% (alignment only - full optimization not possible with computed goto)

### Steps:
1. ✅ Analyze current dispatch table in vm_run() (line ~2691)
2. ✅ Add `__attribute__((aligned(64)))` for cache line optimization
3. ✅ Test all opcodes dispatch correctly
4. ⬜ Benchmark performance improvement

### Implementation Details:
- Current: Dispatch table recreated on every vm_run() call
- Target: Added alignment for better cache performance
- Note: Cannot move to global scope due to computed goto labels
- Alignment: 64-byte alignment for cache line optimization

---

## Phase 2: LOAD Instruction Optimization ⚡ HIGH IMPACT
**Status:** ✅ Complete
**Risk:** LOW
**Expected Performance Gain:** 5-10% in variable-heavy code

### Steps:
1. ✅ Identify immutable types: VAL_INT, VAL_F64, VAL_BOOL, VAL_VOID
2. ✅ Add fast path for immutable types in LOAD instruction
3. ✅ Keep deep copy for mutable types: VAL_STR, VAL_LIST, VAL_STRUCT, VAL_PYOBJECT, VAL_BIGINT
4. ✅ Add inline type check with likely() hint
5. ✅ Test with comprehensive test suite
6. ⬜ Benchmark performance improvement

### Implementation Details:
```c
// Fast path for immutable types (direct copy)
if (likely(v.type == VAL_INT || v.type == VAL_F64 || 
           v.type == VAL_BOOL || v.type == VAL_VOID)) {
    vm_push(vm, v);
} else {
    // Slow path for mutable types (deep copy)
    vm_push(vm, value_copy(v));
}
```

---

## Phase 3: Call Frame Caching ⚡ MEDIUM IMPACT
**Status:** ✅ Complete
**Risk:** LOW
**Expected Performance Gain:** 3-7% in function-heavy code

### Steps:
1. ✅ Add `register CallFrame *current_frame` in vm_run()
2. ✅ Initialize on function entry
3. ✅ Update on CALL instruction
4. ✅ Update on RETURN instruction
5. ✅ Replace all `&vm->call_stack[vm->call_stack_top - 1]` references
6. ✅ Test function calls and returns
7. ⬜ Benchmark performance improvement

### Implementation Details:
- Cache current frame in register variable
- Update only on CALL/RETURN
- Reduces pointer arithmetic overhead
- Updated all instructions: LOAD, STORE, INC_LOCAL, DEC_LOCAL, COPY_LOCAL, etc.

---

## Phase 4: Compiler Hints & Optimizations ⚡ MEDIUM IMPACT
**Status:** ✅ Complete
**Risk:** LOW
**Expected Performance Gain:** 3-8% overall

### Steps:
1. ✅ Add alignment to dispatch table (__attribute__((aligned(64))))
2. ✅ Add `__attribute__((always_inline))` to vm_push and vm_pop
3. ✅ Add `#ifndef NDEBUG` guards for bounds checking
4. ✅ Add `__attribute__((hot))` to vm_run function
5. ✅ Test with -O3 optimization
6. ⬜ Add `__builtin_prefetch()` for predictable memory access (future)
7. ⬜ Benchmark performance improvement

### Implementation Details:
- Dispatch table aligned to 64 bytes for cache line optimization
- Stack operations marked always_inline for aggressive inlining
- Bounds checks removed in release builds (NDEBUG defined)
- Hot function attribute for aggressive optimization of vm_run
- Compiled with -O3, -march=native, -flto, -ffast-math, -funroll-loops

---

## Phase 5: String Length Caching ⚡ MEDIUM IMPACT
**Status:** Planning
**Risk:** MEDIUM
**Expected Performance Gain:** 10-15% in string-heavy code

### Steps:
1. ⬜ Define new FrString structure with length field
2. ⬜ Update value_make_str() to store length
3. ⬜ Update all string operations to use cached length
4. ⬜ Replace strlen() calls with length field access
5. ⬜ Update value_print and string consumers
6. ⬜ Test comprehensive string operations
7. ⬜ Ensure backward compatibility
8. ⬜ Benchmark performance improvement

### Implementation Details:
```c
typedef struct {
    char *data;
    size_t length;
    size_t capacity;  // For future growth optimization
} FrString;
```

---

## Phase 6: Memory Pool for Strings ⚡ MEDIUM-HIGH IMPACT
**Status:** Planning
**Risk:** MEDIUM
**Expected Performance Gain:** 15-25% reduction in allocation overhead

### Steps:
1. ⬜ Design simple string pool structure
2. ⬜ Implement pool_alloc_string(size_t len)
3. ⬜ Implement pool_free_string(FrString *str)
4. ⬜ Add pool to VM structure
5. ⬜ Update string creation to use pool
6. ⬜ Add pool cleanup in vm_free()
7. ⬜ Test memory usage and leaks
8. ⬜ Benchmark performance improvement

### Implementation Details:
- Fixed-size block allocator for common string sizes
- Free list for quick reuse
- Fall back to malloc for large strings

---

## Phase 7: GMP Temporary Object Pool ⚡ LOW-MEDIUM IMPACT
**Status:** Planning
**Risk:** MEDIUM
**Expected Performance Gain:** 5-10% in bigint-heavy code

### Steps:
1. ⬜ Create pool of pre-initialized mpz_t objects
2. ⬜ Implement acquire_temp_bigint()
3. ⬜ Implement release_temp_bigint()
4. ⬜ Add pool to VM structure
5. ⬜ Update bigint operations to use pool
6. ⬜ Ensure proper cleanup
7. ⬜ Test bigint operations
8. ⬜ Benchmark performance improvement

### Implementation Details:
- Pool of 16-32 pre-initialized mpz_t objects
- LIFO free list for cache locality
- Thread-safe if needed later

---

## Phase 8: Value Object Pooling ⚡ MEDIUM IMPACT
**Status:** Planning
**Risk:** MEDIUM
**Expected Performance Gain:** 10-15% in arithmetic-heavy code

### Steps:
1. ⬜ Design value pool structure
2. ⬜ Implement acquire_value()
3. ⬜ Implement release_value()
4. ⬜ Add pool to VM structure
5. ⬜ Modify arithmetic operations to reuse values
6. ⬜ Track value lifetimes carefully
7. ⬜ Test for memory leaks
8. ⬜ Benchmark performance improvement

### Implementation Details:
- Pool of Value objects for temporary computations
- Reuse instead of malloc/free in hot loops
- Careful lifetime management

---

## Phase 9: Bytecode Parser Optimization ⚡ LOW IMPACT
**Status:** Planning
**Risk:** LOW
**Expected Performance Gain:** One-time 20-30% faster loading

### Steps:
1. ⬜ Implement custom tokenizer
2. ⬜ Replace strtok in vm_load_bytecode
3. ⬜ Use pointer arithmetic for parsing
4. ⬜ Reduce allocations during parsing
5. ⬜ Test bytecode loading
6. ⬜ Benchmark load time improvement

### Implementation Details:
- Direct pointer manipulation
- Single-pass parsing where possible
- Reduce memory allocations

---

## Testing Strategy

### Per-Phase Testing:
1. Run full test suite after each phase
2. Memory leak detection with valgrind
3. Performance benchmarking with representative workloads
4. Stress testing with edge cases

### Benchmark Suite:
- Arithmetic-heavy loops
- String manipulation
- Function calls
- List operations
- Mixed workload

### Success Criteria:
- All tests pass
- No memory leaks
- Measurable performance improvement
- No regression in any test case

---

## Expected Overall Performance Gain
**Conservative Estimate:** 30-50% improvement
**Optimistic Estimate:** 50-80% improvement
**Target Workload:** Mixed computational tasks with loops, functions, and data structures

---

## Implementation Order Rationale
1. Quick wins first (Phases 1-4): Low risk, immediate gains
2. Structural changes (Phase 5): Medium risk, significant gains
3. Advanced optimizations (Phases 6-8): Higher risk, major gains
4. Cleanup (Phase 9): Low priority, one-time benefit

---

## Notes
- Maintain backward compatibility
- Document all changes
- Add comments for non-obvious optimizations
- Consider future parallelization opportunities


# TODO: Native no-libc runtime - Remaining Work

## Current State

- Native tests passing: 141/247
- Hello world binary: 222 bytes (no libc)
- Index error tests pass with ?line,0:message format
- Basic arithmetic, function calls, list bounds checking work

## Remaining Test Failures (106 tests)

### 1. Assertion Failures (2 tests)

- `assertions/assert_fail.fr` - Output "" != expected "Assertion failed"
- `assertions/assert_output.fr` - Output "" != expected "hello"
- **Fix**: runtime_assert in fr_rt.c outputs empty instead of message. Need to fix fr_fputs usage.

### 2. Control Flow - Loops (8 tests)

- `control_flow/for_in_list.fr` - Output "" != expected "1\n2\n3"
- `control_flow/for_in_string.fr` - in function `_fr_main_fall_1`
- `control_flow/for_in_empty_string.fr` - in function `_fr_main_fall_1`
- `control_flow/for_range.fr` - Output "" != expected "0\n1\n2\n3\n4"
- `control_flow/for_range_start.fr` - Output "" != expected "2\n3\n4"
- `control_flow/for_range_step.fr` - Output "" != expected "0\n2\n4\n6\n8"
- `control_flow/for_range_step_negative.fr` - Output "" != expected "10\n7\n4\n1"
- `control_flow/for_range_step_odd.fr` - Output "" != expected "1\n3\n5\n7\n9"
- `control_flow/break_for.fr` - Output "" != expected "0\n1\n2\n3\n4"
- `control_flow/continue_for.fr` - Output "" != expected "0\n1\n3\n4"
- `control_flow/break_while.fr` - Output "" != expected "0\n1\n2"
- **Fix**: Loop iteration over lists/strings/ranges may be missing runtime support or codegen has issues with loop constructors.

### 3. Struct Allocation (12 tests)

- `data_structures/struct_basic.fr` - undefined reference to `_fr_heap_ptr`
- `data_structures/struct_field_assign.fr`
- `data_structures/struct_field_cache.fr`
- `data_structures/struct_get_local.fr`
- `data_structures/struct_mixed_types.fr`
- `data_structures/struct_multi_field_read.fr`
- `data_structures/struct_nested.fr`
- `data_structures/struct_return.fr`
- `data_structures/struct_string_field.fr`
- `data_structures/struct_in_list.fr`
- `data_structures/struct_as_param.fr`
- **Fix**: Codegen emits `_fr_heap_ptr` global but fr_rt.c uses mmap-based heap with `heap_base`/`heap_ptr` locals. Need to either:
  - Add `_fr_heap_ptr` global to fr_rt.c and update init_heap, OR
  - Change codegen to call `runtime_alloc_struct(size)` instead of direct heap access

### 4. List Operations (8 tests)

- `data_types/list_append.fr` - Output "[list]" != expected "[1, 2, 3, 4]"
- `data_types/list_empty.fr` - Output "[list]" != expected "[]"
- `data_types/list_assignment.fr` - Output "" != expected "10"
- `data_types/list_indexing.fr` - Output "" != expected "1"
- `data_types/list_literal.fr` - Output "[list]" != expected "[1, 2, 3]"
- `data_types/list_len.fr` - Output "" != expected "3"
- `data_types/list_method_syntax.fr` - Output "" != expected "5"
- `data_types/list_pop.fr` - in function `_fr_main_main_entry`
- `data_types/list_pop_last.fr` - in function `_fr_main_main_entry`
- `data_types/list_pop_remaining.fr` - in function `_fr_main_main_entry`
- **Fix**: runtime_list_to_str returns "[list]" stub. Need proper list formatting. Also need to verify list append/set operations work.

### 5. Set Operations (3 tests)

- `data_types/set_add_duplicate.fr` - Output "{set}" != expected "{1, 2, 3}"
- `data_types/set_empty.fr` - Output "{set}" != expected "{}"
- `data_types/set_string.fr` - Output "{set}" != expected "{hello, world}"
- **Fix**: runtime_set_to_str returns "{set}" stub. Need proper set formatting with sorted elements.

### 6. String Operations (1 test)

- `control_flow/switch_string.fr` - in function `_fr_main_main_entry`
- **Fix**: Missing runtime_str_to_lower or similar string case conversion for switch matching.

### 7. Float Formatting (3 tests - already fixed, need verification)

- `data_types/float_multiplication.fr` - Output "7.50" != expected "7.5"
- `data_types/float_division.fr` - Output "3.50" != expected "3.5"
- `data_types/float_negative.fr` - Output "-3.50" != expected "-3.5"
- `data_types/float_addition.fr` - Output "3.50" != expected "3.5"
- **Fix**: Already modified runtime_float_to_str to strip trailing zeros. Need to re-test.

### 8. Misc (1 test)

- `misc/wait_basic.fr` - in function `_fr_main_main_entry`
- **Fix**: Missing fork/wait syscalls or runtime support.

### 9. Input Function

- Need to implement runtime_input_str or similar if any tests use input()

## Implementation Order

1. Fix struct allocation (_fr_heap_ptr issue) - unblocks 12 tests
2. Fix list_to_str - unblocks 8 tests
3. Fix set_to_str - unblocks 3 tests
4. Fix assert output - unblocks 2 tests
5. Fix loop iteration - unblocks 10 tests
6. Fix float formatting verify - 3-4 tests
7. Fix switch_string - 1 test
8. Fix wait_basic - 1 test
9. Fix any remaining individual tests

## Files to Modify

- `runtime/fr_rt.c` - Add missing runtime functions
- `src/optimizer/codegen.py` - Fix struct alloc to use runtime call or add _fr_heap_ptr
- `src/run_single_test.py` - Already updated, may need minor fixes
- `src/cli.py` - Already updated

## Notes

- Wasm backend has 208 failures but is not the current focus
- C VM has 11 failures (separate from native)
- Python VM has 2 failures (separate from native)

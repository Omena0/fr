# Memory Model and Pointers

Fr uses **reference semantics for mutable aggregates** (`struct`, `list`, `set`).
Assigning one to another aliases the same object; the compiler/runtime chooses
where that object lives.

## Pointer syntax

Pointers are opt-in. Existing code that does not use `*`/`&` keeps its current
value/reference behaviour.

```fr
struct Node {
    int value
    Node* next
}

void bump(int* p) {
    *p = *p + 1
}

void main() {
    int x = 5
    int* p = &x          // address of a local
    *p = 9
    println(x)           // 9

    int** pp = &p        // pointer to a pointer
    **pp = 10

    int y = 1
    p = &y               // re-point at another variable
    bump(p)              // y == 2

    list xs = [1, 2, 3]
    int* e = &xs[1]      // pointer to a list element
    *e = 99
}
```

Accepted spellings:

| Spelling | Meaning |
| --- | --- |
| `int* p` | pointer to `int` |
| `*int p` | pointer to `int` |
| `int** p` / `**int p` | pointer to pointer |
| `Point* p` | pointer to a struct |
| `*Point p` | pointer to a struct |

`int *p` (with a space before the star) remains the varargs declaration
`int *args`; use `int* p` or `*int p` for pointers.

Operations:

* `&lvalue` – address of a variable, struct field, or list element.
* `*p` – load through a pointer.
* `*p = value` – store through a pointer (also `**pp = value`).
* `p.field` automatically dereferences a pointer variable, so `p.x` and
  `(*p).x` are equivalent.
* Chained access works: `p.next.value`, `p.next.value = 7`.

Pointers are raw addresses in the native backend and pointers to `Value` cells
in the C VM. The Python VM uses a `Pointer` object that closes over the target
cell, so `*p = ...` is visible to every alias.

## Lifetime rules

* Do not return or store a pointer to a local variable that outlives its frame.
  This is the same rule as C. The escape analysis keeps address-taken locals
  safe within the function but cannot make a dangling pointer valid.
* Growing a list may reallocate its element buffer, invalidating pointers
  previously obtained from `&list[i]`.
* Heap-allocated objects in the native runtime live for the duration of the
  process. They are allocated from a segregated free-list allocator (not a
  fixed slot table) and can be reused by `realloc`/`free` operations performed
  by the runtime.

## Automatic memory decisions

The SSA optimizer runs these memory-related passes:

1. **SROA (scalar replacement of aggregates)** – non-escaping structs whose
   fields are only read/written directly are replaced by SSA values. No memory
   allocation remains.
2. **Escape analysis** – classifies each allocation as `NO_ESCAPE`,
   `ARG_ESCAPE` (only passed to callees) or `FULL_ESCAPE` (returned, stored in
   another object, stored to a global, or address-taken).
3. **Stack allocation** – `ARG_ESCAPE` allocations are placed in fixed slots in
   the function frame, so passing a struct to a helper does not allocate.
4. **Runtime allocation** – remaining structs are allocated by
   `runtime_struct_new`, lists grow with `realloc`, and the C VM reference-counts
   structs/lists/sets so aliases share one object.

Because structs already have reference semantics, passing a struct to a
function is always a pointer pass; no copy is emitted. Scalar arguments are SSA
values and are not copied either.

## C VM and Python VM

* **Python VM** – mutable objects are ordinary Python objects and are managed by
  the Python garbage collector.
* **C VM** – `Struct`, `List`, and `Set` carry a reference count. Copies of a
  `Value` retain the object; scope/variable cleanup releases it. Cycles are not
  collected, matching the usual reference-counting trade-off.
* **Native** – direct pointers, SROA/stack placement where possible, and a
  free-list heap for escaping objects.

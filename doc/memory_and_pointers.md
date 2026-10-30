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
* Native heap objects are reference counted with function-scope cleanup. Every
  function enters an allocation scope, and every allocation made in that scope
  is released when the function returns. Stores into globals, lists and
  reference-typed struct fields, as well as returns, retain the value; when the
  owning scope exits its reference is dropped and the object is freed if no
  other owner remains. Overwriting a field/global releases the old value.
* Cycles between managed objects are not collected, just as with any reference
  counting scheme. Explicit pointer fields are borrowed by design; do not build
  a cycle through raw pointers unless you manage its lifetime yourself.

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
4. **Runtime allocation and cleanup** – remaining structs are allocated by
   `runtime_struct_new`, lists grow with `realloc`, and both the C VM and the
   native runtime reference-count structs/lists/sets so aliases share one
   object. Native functions push/pop an allocation scope; escaping values are
   retained and the rest are freed at scope exit.

Because structs already have reference semantics, passing a struct to a
function is always a pointer pass; no copy is emitted. Scalar arguments are SSA
values and are not copied either.

## C VM and Python VM

* **Python VM** – mutable objects are ordinary Python objects and are managed by
  the Python garbage collector.
* **C VM** – `Struct`, `List`, and `Set` carry a reference count. Copies of a
  `Value` retain the object; scope/variable cleanup releases it. Cycles are not
  collected, matching the usual reference-counting trade-off.
* **Native** – direct pointers, SROA/stack placement where possible, a
  segregated free-list heap, and scope-based reference counting for escaping
  structs/lists/sets. Values are retained when they escape into a global, list,
  reference-typed field, pointer cell, or return value, and released when the
  owning function scope ends or an owner is overwritten.

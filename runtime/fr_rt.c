/*
 * Minimal freestanding fr runtime for native binaries.
 *
 * Linked with: gcc ... runtime/fr_rt.c runtime/syscall.S -nostdlib -static
 *
 * This file intentionally does not use libc. It provides the small subset of
 * the C runtime that the native backend needs: syscalls, a real (free-list
 * based) allocator, string/list/set operations, math helpers, file I/O and
 * exception unwinding via _setjmp/longjmp.
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef __builtin_va_list fr_va_list;

/* Forward declarations for functions used before their definitions. */
typedef struct {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type; /* -1 unknown, 0 int, 1 string, 2 float, 3 bool */
} RuntimeList;

void* malloc(size_t size);
void free(void* ptr);
void* realloc(void* ptr, size_t size);
void* calloc(size_t count, size_t size);
void runtime_error_at(const char* message, int line);
void runtime_list_append_int(RuntimeList* list, int64_t value);
static void fr_int64_to_buf(int64_t value, char* buffer);
void runtime_retain(void* ptr);
void runtime_release(void* ptr);
void runtime_scope_push(void);
void runtime_scope_pop(void);
void runtime_scope_unwind(int64_t depth);

/* ------------------------------------------------------------------------- */
/* Syscalls (implemented in syscall.S)                                        */
/* ------------------------------------------------------------------------- */

extern int64_t syscall1(int64_t num, int64_t arg1);
extern int64_t syscall3(int64_t num, int64_t arg1, int64_t arg2, int64_t arg3);
extern int64_t syscall6(int64_t num, int64_t arg1, int64_t arg2, int64_t arg3,
                        int64_t arg4, int64_t arg5, int64_t arg6);

extern int _setjmp(void* buffer);
extern void longjmp(void* buffer, int value) __attribute__((noreturn));

#define SYS_READ       0
#define SYS_WRITE      1
#define SYS_CLOSE      3
#define SYS_LSEEK      8
#define SYS_MMAP       9
#define SYS_NANOSLEEP  35
#define SYS_FORK       57
#define SYS_EXIT       60
#define SYS_WAIT4      61
#define SYS_OPENAT     257

#define AT_FDCWD       (-100)
#define O_RDONLY       0
#define O_WRONLY       1
#define O_RDWR         2
#define O_CREAT        64
#define O_TRUNC        512
#define O_APPEND       1024

#define SEEK_SET       0
#define SEEK_CUR       1
#define SEEK_END       2

/* ------------------------------------------------------------------------- */
/* String / memory primitives                                                 */
/* ------------------------------------------------------------------------- */

int64_t strlen(const char* s) {
    const char* p = s;
    if (!p) return 0;
    while (*p) p++;
    return (int64_t)(p - s);
}

void* memcpy(void* dest, const void* src, size_t n) {
    unsigned char* d = (unsigned char*)dest;
    const unsigned char* s = (const unsigned char*)src;
    for (size_t i = 0; i < n; i++) d[i] = s[i];
    return dest;
}

void* memmove(void* dest, const void* src, size_t n) {
    unsigned char* d = (unsigned char*)dest;
    const unsigned char* s = (const unsigned char*)src;
    if (d < s) {
        for (size_t i = 0; i < n; i++) d[i] = s[i];
    } else if (d > s) {
        for (size_t i = n; i > 0; i--) d[i - 1] = s[i - 1];
    }
    return dest;
}

void* memset(void* dest, int c, size_t n) {
    unsigned char* d = (unsigned char*)dest;
    for (size_t i = 0; i < n; i++) d[i] = (unsigned char)c;
    return dest;
}

int memcmp(const void* a, const void* b, size_t n) {
    const unsigned char* pa = (const unsigned char*)a;
    const unsigned char* pb = (const unsigned char*)b;
    for (size_t i = 0; i < n; i++) {
        if (pa[i] != pb[i]) return (int)pa[i] - (int)pb[i];
    }
    return 0;
}

int strcmp(const char* a, const char* b) {
    while (*a && *a == *b) { a++; b++; }
    return (unsigned char)*a - (unsigned char)*b;
}

int strncmp(const char* a, const char* b, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (a[i] != b[i]) return (unsigned char)a[i] - (unsigned char)b[i];
        if (!a[i]) return 0;
    }
    return 0;
}

char* strcpy(char* dest, const char* src) {
    char* d = dest;
    while ((*d++ = *src++)) {}
    return dest;
}

char* strncpy(char* dest, const char* src, size_t n) {
    size_t i = 0;
    for (; i < n && src[i]; i++) dest[i] = src[i];
    for (; i < n; i++) dest[i] = '\0';
    return dest;
}

char* strcat(char* dest, const char* src) {
    char* d = dest + strlen(dest);
    while ((*d++ = *src++)) {}
    return dest;
}

const char* strchr(const char* s, int c) {
    while (s && *s) {
        if ((unsigned char)*s == (unsigned char)c) return s;
        s++;
    }
    return NULL;
}

const char* strstr(const char* haystack, const char* needle) {
    if (!haystack || !needle) return NULL;
    if (!*needle) return haystack;
    for (; *haystack; haystack++) {
        const char* h = haystack;
        const char* n = needle;
        while (*h && *n && *h == *n) { h++; n++; }
        if (!*n) return haystack;
    }
    return NULL;
}

/* ------------------------------------------------------------------------- */
/* Output                                                                     */
/* ------------------------------------------------------------------------- */

static void fr_write(int fd, const char* data, size_t len) {
    size_t off = 0;
    while (off < len) {
        int64_t n = syscall3(SYS_WRITE, fd, (int64_t)(data + off),
                             (int64_t)(len - off));
        if (n <= 0) break;
        off += (size_t)n;
    }
}

void fr_putchar(char c) {
    fr_write(1, &c, 1);
}

void fr_puts(const char* s) {
    if (!s) return;
    fr_write(1, s, (size_t)strlen(s));
    fr_putchar('\n');
}

void fr_fputs(const char* s, int fd) {
    if (!s) return;
    fr_write(fd, s, (size_t)strlen(s));
}

void fr_fflush(int fd) { (void)fd; }

void fr_exit(int status) {
    syscall1(SYS_EXIT, status);
    while (1) {}
}

/* libc-compatible aliases used by emitted assembly */
void puts(const char* s) { fr_puts(s); }
void fputs(const char* s, int fd) { fr_fputs(s, fd); }
void fflush(int fd) { fr_fflush(fd); }
void exit(int status) { fr_exit(status); }

static void fr_write_int(int64_t value, bool newline) {
    char buf[32];
    char* p = buf + sizeof(buf);
    *--p = '\0';
    uint64_t n = value < 0 ? (uint64_t)(-(value + 1)) + 1 : (uint64_t)value;
    if (n == 0) {
        *--p = '0';
    } else {
        while (n) {
            *--p = (char)('0' + (n % 10));
            n /= 10;
        }
        if (value < 0) *--p = '-';
    }
    fr_write(1, p, (size_t)(buf + sizeof(buf) - 1 - p));
    if (newline) fr_putchar('\n');
}

char* runtime_int_to_str(int64_t value) {
    char* result = (char*)malloc(32);
    if (!result) return NULL;
    char* p = result + 31;
    *p = '\0';
    uint64_t n = value < 0 ? (uint64_t)(-(value + 1)) + 1 : (uint64_t)value;
    if (n == 0) {
        *--p = '0';
    } else {
        while (n) {
            *--p = (char)('0' + (n % 10));
            n /= 10;
        }
        if (value < 0) *--p = '-';
    }
    size_t len = (size_t)(result + 31 - p);
    memmove(result, p, len + 1);
    return result;
}

char* runtime_float_to_str(double value) {
    char* result = (char*)malloc(64);
    if (!result) return NULL;

    if (!(value == value)) {  /* NaN */
        strcpy(result, "nan");
        return result;
    }
    if (value > 1.7976931348623157e308) {
        strcpy(result, "inf");
        return result;
    }
    if (value < -1.7976931348623157e308) {
        strcpy(result, "-inf");
        return result;
    }

    char* out = result;
    if (value < 0) {
        *out++ = '-';
        value = -value;
    }

    /* Split into integer and fractional parts. */
    uint64_t ipart = (uint64_t)value;
    double frac = value - (double)ipart;

    char tmp[32];
    char* t = tmp + sizeof(tmp);
    *--t = '\0';
    if (ipart == 0) {
        *--t = '0';
    } else {
        while (ipart) {
            *--t = (char)('0' + (ipart % 10));
            ipart /= 10;
        }
    }
    while (*t) *out++ = *t++;

    *out++ = '.';
    if (frac < 1e-12) {
        *out++ = '0';
    } else {
        /* Produce six fractional digits, then round the final digit. */
        char digits[6];
        for (int i = 0; i < 6; i++) {
            frac *= 10.0;
            int digit = (int)frac;
            digits[i] = (char)('0' + digit);
            frac -= (double)digit;
        }
        if (frac >= 0.5) {
            int i = 5;
            while (i >= 0 && digits[i] == '9') {
                digits[i] = '0';
                i--;
            }
            if (i >= 0) {
                digits[i]++;
            } else {
                /* Carry into the integer part: re-render it. */
                char* ip = out;
                while (ip > result && ip[-1] != '.' && ip[-1] != '-') ip--;
                /* Find the start of the integer text. */
                char* int_start = result;
                if (*int_start == '-') int_start++;
                char* p2 = out - 1; /* points at '.' */
                while (p2 > int_start) {
                    p2--;
                    if (*p2 == '9') {
                        *p2 = '0';
                    } else {
                        (*p2)++;
                        break;
                    }
                }
                if (p2 == int_start) {
                    /* All nines: prepend a 1. */
                    memmove(int_start + 1, int_start, (size_t)(out - int_start));
                    *int_start = '1';
                    out++;
                }
            }
        }
        int last = 5;
        while (last >= 0 && digits[last] == '0') last--;
        for (int i = 0; i <= last; i++) *out++ = digits[i];
        if (last < 0) *out++ = '0';
    }
    *out = '\0';
    return result;
}

char* runtime_bool_to_str(int64_t value) {
    return (char*)(value ? "true" : "false");
}

/* Minimal printf: %s %c %d %i %u %ld %lu %f %g %x %% */
int printf(const char* fmt, ...) {
    fr_va_list ap;
    __builtin_va_start(ap, fmt);

    for (const char* p = fmt; *p; p++) {
        if (*p != '%') {
            fr_putchar(*p);
            continue;
        }
        p++;
        if (*p == '%') {
            fr_putchar('%');
            continue;
        }
        bool is_long = false;
        while (*p == 'l' || *p == 'z') {
            is_long = true;
            p++;
        }
        switch (*p) {
            case 'd':
            case 'i': {
                int64_t v = is_long ? __builtin_va_arg(ap, int64_t)
                                    : (int64_t)__builtin_va_arg(ap, int);
                fr_write_int(v, false);
                break;
            }
            case 'u': {
                uint64_t v = is_long ? __builtin_va_arg(ap, uint64_t)
                                     : (uint64_t)__builtin_va_arg(ap, unsigned int);
                fr_write_int((int64_t)v, false);
                break;
            }
            case 'x': {
                uint64_t v = is_long ? __builtin_va_arg(ap, uint64_t)
                                     : (uint64_t)__builtin_va_arg(ap, unsigned int);
                char buf[24];
                char* q = buf + sizeof(buf);
                *--q = '\0';
                if (!v) *--q = '0';
                while (v) {
                    unsigned d = (unsigned)(v & 15u);
                    *--q = (char)(d < 10 ? '0' + d : 'a' + d - 10);
                    v >>= 4;
                }
                fr_write(1, q, (size_t)(buf + sizeof(buf) - 1 - q));
                break;
            }
            case 's': {
                const char* s = __builtin_va_arg(ap, const char*);
                if (!s) s = "(null)";
                fr_write(1, s, (size_t)strlen(s));
                break;
            }
            case 'c':
                fr_putchar((char)__builtin_va_arg(ap, int));
                break;
            case 'f':
            case 'g': {
                double d = __builtin_va_arg(ap, double);
                char* s = runtime_float_to_str(d);
                if (s) {
                    fr_write(1, s, (size_t)strlen(s));
                    free(s);
                }
                break;
            }
            default:
                fr_putchar('%');
                if (*p) fr_putchar(*p);
                break;
        }
    }
    __builtin_va_end(ap);
    return 0;
}

void fr_printf(const char* fmt, ...) { (void)fmt; }

/* ------------------------------------------------------------------------- */
/* Allocator: mmap arena + segregated free lists.                             */
/* ------------------------------------------------------------------------- */

#define HEAP_SIZE ((size_t)64 * 1024 * 1024)
#define HEAP_MAGIC 0x4652484541503031ULL /* "FRHEAP01" */
#define MIN_BLOCK 16
#define NUM_BINS 32

typedef struct BlockHeader {
    uint64_t magic;
    size_t size; /* payload size */
    size_t bin;
} BlockHeader;

typedef struct FreeBlock {
    struct FreeBlock* next;
} FreeBlock;

static unsigned char* heap_base;
static unsigned char* heap_cur;
static unsigned char* heap_end;
static FreeBlock* free_lists[NUM_BINS];

static int bin_index(size_t size) {
    size_t block = size + sizeof(BlockHeader);
    int bin = 4; /* 16-byte minimum */
    size_t cap = (size_t)1 << bin;
    while (cap < block && bin < NUM_BINS - 1) {
        bin++;
        cap <<= 1;
    }
    return bin;
}

static size_t bin_size(int bin) {
    return (size_t)1 << bin;
}

void init_heap(void) {
    if (heap_base) return;
    int64_t result = syscall6(SYS_MMAP, 0, (int64_t)HEAP_SIZE,
                              3 /* PROT_READ|PROT_WRITE */,
                              0x22 /* MAP_PRIVATE|MAP_ANONYMOUS */, -1, 0);
    if (result < 0) {
        fr_fputs("Runtime error: out of memory\n", 2);
        fr_exit(1);
    }
    heap_base = (unsigned char*)result;
    heap_cur = heap_base;
    heap_end = heap_base + HEAP_SIZE;
    for (int i = 0; i < NUM_BINS; i++) free_lists[i] = NULL;
}

void* malloc(size_t size) {
    if (!heap_base) init_heap();
    if (size == 0) size = 8;
    int bin = bin_index(size);
    if (bin >= NUM_BINS) {
        fr_fputs("Runtime error: allocation too large\n", 2);
        fr_exit(1);
    }

    BlockHeader* header;
    if (free_lists[bin]) {
        FreeBlock* block = free_lists[bin];
        free_lists[bin] = block->next;
        header = (BlockHeader*)block;
    } else {
        size_t total = bin_size(bin);
        if (heap_cur + total > heap_end) {
            /* Try a larger bin before giving up. */
            int alt = bin + 1;
            while (alt < NUM_BINS && !free_lists[alt]) alt++;
            if (alt < NUM_BINS) {
                FreeBlock* block = free_lists[alt];
                free_lists[alt] = block->next;
                header = (BlockHeader*)block;
                /* A larger block is fine; free() records its actual bin. */
                header->magic = HEAP_MAGIC;
                header->size = bin_size(alt) - sizeof(BlockHeader);
                header->bin = (size_t)alt;
                return (void*)(header + 1);
            }
            fr_fputs("Runtime error: out of memory\n", 2);
            fr_exit(1);
        }
        header = (BlockHeader*)heap_cur;
        heap_cur += total;
    }

    header->magic = HEAP_MAGIC;
    header->size = bin_size(bin) - sizeof(BlockHeader);
    header->bin = (size_t)bin;
    return (void*)(header + 1);
}

void free(void* ptr) {
    if (!ptr) return;
    BlockHeader* header = ((BlockHeader*)ptr) - 1;
    if (header->magic != HEAP_MAGIC) {
        fr_fputs("Runtime error: invalid free\n", 2);
        fr_exit(1);
    }
    size_t bin = header->bin;
    if (bin >= NUM_BINS) return;
    header->magic = 0;
    FreeBlock* block = (FreeBlock*)header;
    block->next = free_lists[bin];
    free_lists[bin] = block;
}

void* realloc(void* ptr, size_t size) {
    if (!ptr) return malloc(size);
    if (size == 0) {
        free(ptr);
        return NULL;
    }
    BlockHeader* header = ((BlockHeader*)ptr) - 1;
    if (header->magic != HEAP_MAGIC) return malloc(size);
    if (header->size >= size) return ptr;

    void* next = malloc(size);
    if (!next) return NULL;
    memcpy(next, ptr, header->size);
    free(ptr);
    return next;
}

void* calloc(size_t count, size_t size) {
    size_t total = count * size;
    void* ptr = malloc(total);
    if (ptr) memset(ptr, 0, total);
    return ptr;
}

/*
 * Managed objects
 * ---------------
 * Structs and lists carry a header so the runtime can use reference counting
 * with deterministic, scope-based cleanup. Every allocation is registered in
 * the current function's allocation scope. Escaping values are retained by the
 * operation that makes them escape (field/global/list store or return); when
 * the owning function exits its scope drops one reference from every object it
 * created. Objects still referenced elsewhere survive, unreferenced ones are
 * freed immediately.
 */
#define FR_OBJ_MAGIC 0x46524F424A303031ULL /* "FROBJ001" */
#define FR_OBJ_STRUCT 1
#define FR_OBJ_LIST 2
#define FR_OBJ_SET 3
#define FR_OBJ_RAW 4
#define FR_OBJ_DICT 5

typedef struct FrObjHeader {
    uint64_t magic;
    int64_t refcount;
    int64_t kind;
    int64_t aux;             /* struct: managed-field mask */
    struct FrObjHeader* next_scope;
    struct FrObjHeader* prev_scope;
    int64_t scope_id;
    uint64_t reserved;
} FrObjHeader;

#define FR_MAX_SCOPES 1024
FrObjHeader* fr_scope_heads[FR_MAX_SCOPES];
int64_t fr_scope_depth = 0;

static bool fr_obj_valid(void* ptr) {
    if (!ptr || !heap_base) return false;
    unsigned char* p = (unsigned char*)ptr;
    if (p < heap_base + sizeof(FrObjHeader) || p >= heap_cur) return false;
    FrObjHeader* header = ((FrObjHeader*)p) - 1;
    return header->magic == FR_OBJ_MAGIC;
}

static void* fr_obj_alloc(size_t size, int kind, int64_t aux) {
    FrObjHeader* header = (FrObjHeader*)malloc(sizeof(FrObjHeader) + size);
    if (!header) return NULL;
    memset(header, 0, sizeof(FrObjHeader));
    header->magic = FR_OBJ_MAGIC;
    header->refcount = 1;
    header->kind = kind;
    header->aux = aux;
    header->next_scope = NULL;
    header->prev_scope = NULL;
    header->scope_id = -1;
    if (fr_scope_depth > 0) {
        int depth = fr_scope_depth - 1;
        header->scope_id = depth;
        header->next_scope = fr_scope_heads[depth];
        if (fr_scope_heads[depth]) fr_scope_heads[depth]->prev_scope = header;
        fr_scope_heads[depth] = header;
    }
    return (void*)(header + 1);
}

void runtime_retain(void* ptr) {
    if (!fr_obj_valid(ptr)) return;
    FrObjHeader* header = ((FrObjHeader*)ptr) - 1;
    header->refcount++;
}

/* Remove an object from the current scope without freeing it. Used when a
 * store/return transfers the current scope's reference to a new owner. */
static void runtime_scope_forget(void* ptr) {
    if (!fr_obj_valid(ptr) || fr_scope_depth <= 0) return;
    FrObjHeader* header = ((FrObjHeader*)ptr) - 1;
    int depth = fr_scope_depth - 1;
    if (header->scope_id != depth) return;

    if (header->prev_scope) {
        header->prev_scope->next_scope = header->next_scope;
    } else if (fr_scope_heads[depth] == header) {
        fr_scope_heads[depth] = header->next_scope;
    }
    if (header->next_scope) {
        header->next_scope->prev_scope = header->prev_scope;
    }
    header->next_scope = NULL;
    header->prev_scope = NULL;
    header->scope_id = -1;
    runtime_release(ptr);
}

void runtime_retain_transfer(void* ptr) {
    runtime_retain(ptr);
    runtime_scope_forget(ptr);
}

void runtime_scope_pop(void) {
    if (fr_scope_depth <= 0) return;
    int depth = --fr_scope_depth;
    FrObjHeader* header = fr_scope_heads[depth];
    fr_scope_heads[depth] = NULL;
    while (header) {
        FrObjHeader* next = header->next_scope;
        header->next_scope = NULL;
        runtime_release((void*)(header + 1));
        header = next;
    }
}

void runtime_scope_unwind(int64_t depth) {
    if (depth < 0) depth = 0;
    while (fr_scope_depth > depth) runtime_scope_pop();
}

void* runtime_alloc(int64_t size) {
    if (size <= 0) size = 8;
    return fr_obj_alloc((size_t)size, FR_OBJ_RAW, 0);
}

void runtime_free(void* ptr) { runtime_release(ptr); }
void* runtime_realloc(void* ptr, int64_t size) { return realloc(ptr, (size_t)size); }

void* runtime_struct_new(int64_t size, int64_t count, int64_t* fields,
                         int64_t managed_mask) {
    char* memory = (char*)fr_obj_alloc((size_t)size, FR_OBJ_STRUCT, managed_mask);
    if (!memory) return NULL;
    if (fields && count > 0) {
        memcpy(memory, fields, (size_t)count * sizeof(int64_t));
    }
    for (int i = 0; i < 64; i++) {
        if (managed_mask & ((int64_t)1 << i)) {
            runtime_retain(((void**)memory)[i]);
            runtime_scope_forget(((void**)memory)[i]);
        }
    }
    return memory;
}

void runtime_store_field(void* struct_ptr, int64_t value, int64_t field_index,
                         int64_t managed) {
    if (!struct_ptr) return;
    int64_t* fields = (int64_t*)struct_ptr;
    if (managed) {
        if (fields[field_index] == value) return;
        runtime_retain((void*)value);
        if (fr_obj_valid(struct_ptr)) {
            FrObjHeader* header = ((FrObjHeader*)struct_ptr) - 1;
            if (header->kind == FR_OBJ_STRUCT) runtime_scope_forget((void*)value);
        }
        runtime_release((void*)fields[field_index]);
    }
    fields[field_index] = value;
}

void runtime_store_global(int64_t* slot, int64_t value, int64_t managed) {
    if (!slot) return;
    if (managed) {
        if (*slot == value) return;
        runtime_retain((void*)value);
        runtime_scope_forget((void*)value);
        runtime_release((void*)*slot);
    }
    *slot = value;
}

void runtime_ptr_store(int64_t* slot, int64_t value, int64_t managed) {
    runtime_store_global(slot, value, managed);
}

/* ------------------------------------------------------------------------- */
/* Math                                                                       */
/* ------------------------------------------------------------------------- */

double fabs(double x) { return x < 0 ? -x : x; }

double sqrt(double x) {
    if (x <= 0.0) return 0.0;
    double result;
    __asm__ __volatile__("sqrtsd %1, %0" : "=x"(result) : "x"(x));
    return result;
}

double floor(double x) {
    int64_t i = (int64_t)x;
    if ((double)i > x) i--;
    return (double)i;
}

double ceil(double x) {
    int64_t i = (int64_t)x;
    if ((double)i < x) i++;
    return (double)i;
}

double round(double x) {
    return x >= 0.0 ? floor(x + 0.5) : ceil(x - 0.5);
}

double runtime_floor(double x) { return floor(x); }
double runtime_ceil(double x) { return ceil(x); }
double runtime_round(double x) { return round(x); }

double runtime_sin(double x) {
    double r;
    __asm__ __volatile__("fsin" : "=t"(r) : "0"(x));
    return r;
}

double runtime_cos(double x) {
    double r;
    __asm__ __volatile__("fcos" : "=t"(r) : "0"(x));
    return r;
}

double runtime_tan(double x) {
    double r;
    __asm__ __volatile__("fptan" : "=t"(r) : "0"(x) : "st(1)");
    return r;
}

double sin(double x) { return runtime_sin(x); }
double cos(double x) { return runtime_cos(x); }
double tan(double x) { return runtime_tan(x); }

double pow(double base, double exp) {
    if (exp == 0.0) return 1.0;
    if (exp == 1.0) return base;
    if (base == 0.0) return 0.0;

    bool neg = exp < 0.0;
    double e = neg ? -exp : exp;
    int64_t whole = (int64_t)e;
    double fraction = e - (double)whole;

    double result = 1.0;
    double b = base;
    int64_t n = whole;
    while (n > 0) {
        if (n & 1) result *= b;
        b *= b;
        n >>= 1;
    }
    /* Fractional exponent: use exp(log(x)) via x87. */
    if (fraction > 0.0) {
        double lx;
        __asm__ __volatile__("fyl2x"
                             : "=t"(lx)
                             : "0"(base), "u"(fraction)
                             : "st(1)");
        double ex;
        __asm__ __volatile__("fldl2e; fmulp; fld %%st(0); frndint; "
                             "fxch %%st(1); fsub %%st(1), %%st; f2xm1; "
                             "fld1; faddp; fscale; fstp %%st(1)"
                             : "=t"(ex)
                             : "0"(lx)
                             : "st(1)");
        result *= ex;
    }
    return neg ? 1.0 / result : result;
}

double runtime_pow(double base, double exp) { return pow(base, exp); }

int64_t runtime_abs_int(int64_t value) { return value < 0 ? -value : value; }
int64_t runtime_min_int(int64_t a, int64_t b) { return a < b ? a : b; }
int64_t runtime_max_int(int64_t a, int64_t b) { return a > b ? a : b; }

/* ------------------------------------------------------------------------- */
/* String operations                                                          */
/* ------------------------------------------------------------------------- */

static char* fr_strdup(const char* s) {
    if (!s) s = "";
    size_t len = (size_t)strlen(s);
    char* out = (char*)malloc(len + 1);
    if (!out) return NULL;
    memcpy(out, s, len + 1);
    return out;
}

char* runtime_str_concat(const char* a, const char* b) {
    if (!a) a = "";
    if (!b) b = "";
    size_t la = (size_t)strlen(a);
    size_t lb = (size_t)strlen(b);
    char* result = (char*)malloc(la + lb + 1);
    if (!result) return NULL;
    memcpy(result, a, la);
    memcpy(result + la, b, lb + 1);
    return result;
}

int64_t runtime_str_len(const char* str) { return strlen(str); }

int64_t runtime_str_contains(const char* haystack, const char* needle) {
    return strstr(haystack, needle) != NULL ? 1 : 0;
}

int64_t runtime_str_eq(const char* a, const char* b) {
    if (!a || !b) return a == b;
    return strcmp(a, b) == 0;
}

char* runtime_str_get_char(const char* str, int64_t index) {
    int64_t len = strlen(str);
    if (index < 0) index += len;
    if (index < 0 || index >= len) return fr_strdup("");
    char* result = (char*)malloc(2);
    if (!result) return NULL;
    result[0] = str[index];
    result[1] = '\0';
    return result;
}

char* runtime_str_upper(const char* str) {
    size_t len = (size_t)strlen(str);
    char* result = (char*)malloc(len + 1);
    if (!result) return NULL;
    for (size_t i = 0; i < len; i++) {
        char c = str[i];
        result[i] = (c >= 'a' && c <= 'z') ? (char)(c - 'a' + 'A') : c;
    }
    result[len] = '\0';
    return result;
}

char* runtime_str_lower(const char* str) {
    size_t len = (size_t)strlen(str);
    char* result = (char*)malloc(len + 1);
    if (!result) return NULL;
    for (size_t i = 0; i < len; i++) {
        char c = str[i];
        result[i] = (c >= 'A' && c <= 'Z') ? (char)(c - 'A' + 'a') : c;
    }
    result[len] = '\0';
    return result;
}

static bool fr_isspace(char c) {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f';
}

char* runtime_str_strip(const char* str) {
    const char* start = str;
    while (*start && fr_isspace(*start)) start++;
    const char* end = start + strlen(start);
    while (end > start && fr_isspace(end[-1])) end--;
    size_t len = (size_t)(end - start);
    char* result = (char*)malloc(len + 1);
    if (!result) return NULL;
    memcpy(result, start, len);
    result[len] = '\0';
    return result;
}

RuntimeList* runtime_list_new(void); /* forward */

char* runtime_str_join(RuntimeList* list, const char* delim) {
    if (!list || list->length == 0) return fr_strdup("");
    if (!delim) delim = "";
    size_t delim_len = (size_t)strlen(delim);
    size_t total = 0;
    for (int64_t i = 0; i < list->length; i++) {
        const char* s = (const char*)list->items[i];
        total += (size_t)strlen(s);
        if (i + 1 < list->length) total += delim_len;
    }
    char* result = (char*)malloc(total + 1);
    if (!result) return NULL;
    char* out = result;
    for (int64_t i = 0; i < list->length; i++) {
        const char* s = (const char*)list->items[i];
        size_t len = (size_t)strlen(s);
        memcpy(out, s, len);
        out += len;
        if (i + 1 < list->length) {
            memcpy(out, delim, delim_len);
            out += delim_len;
        }
    }
    *out = '\0';
    return result;
}

char* runtime_str_replace(const char* str, const char* old, const char* repl) {
    if (!old || !repl || !*old) return fr_strdup(str);
    size_t old_len = (size_t)strlen(old);
    size_t repl_len = (size_t)strlen(repl);
    size_t count = 0;
    const char* p = str;
    while ((p = strstr(p, old)) != NULL) { count++; p += old_len; }
    if (count == 0) return fr_strdup(str);

    size_t src_len = (size_t)strlen(str);
    size_t out_len = src_len + count * (repl_len - old_len);
    char* result = (char*)malloc(out_len + 1);
    if (!result) return NULL;
    char* out = result;
    const char* src = str;
    while ((p = strstr(src, old)) != NULL) {
        size_t chunk = (size_t)(p - src);
        memcpy(out, src, chunk);
        out += chunk;
        memcpy(out, repl, repl_len);
        out += repl_len;
        src = p + old_len;
    }
    strcpy(out, src);
    return result;
}

RuntimeList* runtime_str_split(const char* str, const char* delim) {
    RuntimeList* list = runtime_list_new();
    list->elem_type = 1;
    if (!delim || !*delim) {
        runtime_list_append_int(list, (int64_t)fr_strdup(str));
        return list;
    }
    size_t delim_len = (size_t)strlen(delim);
    const char* start = str;
    const char* p = str;
    while (*p) {
        if (strncmp(p, delim, delim_len) == 0) {
            size_t len = (size_t)(p - start);
            char* token = (char*)malloc(len + 1);
            if (token) {
                memcpy(token, start, len);
                token[len] = '\0';
                runtime_list_append_int(list, (int64_t)token);
            }
            p += delim_len;
            start = p;
        } else {
            p++;
        }
    }
    runtime_list_append_int(list, (int64_t)fr_strdup(start));
    return list;
}

char* runtime_str_repeat(const char* str, int64_t count) {
    if (count <= 0) return fr_strdup("");
    size_t len = (size_t)strlen(str);
    char* result = (char*)malloc(len * (size_t)count + 1);
    if (!result) return NULL;
    char* out = result;
    for (int64_t i = 0; i < count; i++) {
        memcpy(out, str, len);
        out += len;
    }
    *out = '\0';
    return result;
}

char* runtime_str_encode(const char* str) { return fr_strdup(str); }
char* runtime_str_decode(const char* bytes) { return fr_strdup(bytes); }

int64_t runtime_str_to_int(const char* str) {
    if (!str) return 0;
    int64_t sign = 1;
    if (*str == '-') { sign = -1; str++; }
    else if (*str == '+') str++;
    int64_t value = 0;
    bool any = false;
    while (*str >= '0' && *str <= '9') {
        any = true;
        value = value * 10 + (*str - '0');
        str++;
    }
    return any ? value * sign : 0;
}

double runtime_str_to_float(const char* str) {
    if (!str) return 0.0;
    double sign = 1.0;
    if (*str == '-') { sign = -1.0; str++; }
    else if (*str == '+') str++;
    double value = 0.0;
    bool any = false;
    while (*str >= '0' && *str <= '9') {
        any = true;
        value = value * 10.0 + (double)(*str - '0');
        str++;
    }
    if (*str == '.') {
        str++;
        double place = 0.1;
        while (*str >= '0' && *str <= '9') {
            any = true;
            value += (double)(*str - '0') * place;
            place *= 0.1;
            str++;
        }
    }
    return any ? value * sign : 0.0;
}

/* ------------------------------------------------------------------------- */
/* List operations                                                            */
/* ------------------------------------------------------------------------- */

RuntimeList* runtime_list_new(void) {
    RuntimeList* list = (RuntimeList*)fr_obj_alloc(sizeof(RuntimeList), FR_OBJ_LIST, 0);
    if (!list) return NULL;
    list->capacity = 8;
    list->length = 0;
    list->elem_type = -1;
    list->items = (int64_t*)malloc((size_t)list->capacity * sizeof(int64_t));
    if (!list->items) {
        free(list);
        return NULL;
    }
    return list;
}

RuntimeList* runtime_list_new_typed(int64_t elem_type) {
    RuntimeList* list = runtime_list_new();
    if (list) list->elem_type = (int)elem_type;
    return list;
}

static void fr_list_append_raw(RuntimeList* list, int64_t value, bool retain) {
    if (!list) return;
    if (retain) {
        runtime_retain((void*)value);
        runtime_scope_forget((void*)value);
    }
    if (list->length >= list->capacity) {
        int64_t new_cap = list->capacity ? list->capacity * 2 : 8;
        int64_t* items = (int64_t*)realloc(
            list->items, (size_t)new_cap * sizeof(int64_t));
        if (!items) return;
        list->items = items;
        list->capacity = new_cap;
    }
    list->items[list->length++] = value;
}

void runtime_list_append_int(RuntimeList* list, int64_t value) {
    fr_list_append_raw(list, value, list && list->elem_type == 4);
}

void runtime_list_append_managed(RuntimeList* list, int64_t value) {
    if (!list) return;
    if (list->elem_type < 0 || list->elem_type == 0) list->elem_type = 4;
    fr_list_append_raw(list, value, true);
}

int64_t runtime_list_get_int(RuntimeList* list, int64_t index) {
    if (!list) return 0;
    if (index < 0) index += list->length;
    if (index < 0 || index >= list->length) return 0;
    return list->items[index];
}

void runtime_list_set_int(RuntimeList* list, int64_t index, int64_t value) {
    if (!list) return;
    if (index < 0) index += list->length;
    if (index < 0 || index >= list->length) return;
    if (list->elem_type == 4) {
        if (list->items[index] == value) return;
        runtime_retain((void*)value);
        runtime_scope_forget((void*)value);
        runtime_release((void*)list->items[index]);
    }
    list->items[index] = value;
}

void runtime_list_set_managed(RuntimeList* list, int64_t index, int64_t value) {
    if (!list) return;
    if (list->elem_type < 0 || list->elem_type == 0) list->elem_type = 4;
    runtime_list_set_int(list, index, value);
}

int64_t runtime_list_len(RuntimeList* list) { return list ? list->length : 0; }

void* runtime_list_elem_addr(RuntimeList* list, int64_t index) {
    if (!list) runtime_error_at("Index error: null list pointer", 0);
    int64_t original = index;
    if (index < 0) index += list->length;
    if (index < 0 || index >= list->length) {
        char msg[256];
        char index_str[32];
        char length_str[32];
        fr_int64_to_buf(original, index_str);
        fr_int64_to_buf(list->length, length_str);
        strcpy(msg, "Index error: list index out of range: ");
        strcat(msg, index_str);
        strcat(msg, " (length: ");
        strcat(msg, length_str);
        strcat(msg, ")");
        runtime_error_at(msg, 0);
    }
    return (void*)&list->items[index];
}

int64_t runtime_list_pop(RuntimeList* list) {
    if (!list || list->length == 0) return 0;
    return list->items[--list->length];
}

static void fr_int64_to_buf(int64_t value, char* buffer) {
    char* p = buffer + 31;
    *p = '\0';
    uint64_t n = value < 0 ? (uint64_t)(-(value + 1)) + 1 : (uint64_t)value;
    if (!n) {
        *--p = '0';
    } else {
        while (n) { *--p = (char)('0' + (n % 10)); n /= 10; }
        if (value < 0) *--p = '-';
    }
    while (*p) *buffer++ = *p++;
    *buffer = '\0';
}

int64_t runtime_list_get_int_at(RuntimeList* list, int64_t index, int line) {
    if (!list) {
        runtime_error_at("Index error: null list pointer", line);
    }
    int64_t original = index;
    if (index < 0) index += list->length;
    if (index < 0 || index >= list->length) {
        char msg[256];
        char index_str[32];
        char length_str[32];
        fr_int64_to_buf(original, index_str);
        fr_int64_to_buf(list->length, length_str);
        strcpy(msg, "Index error: list index out of range: ");
        strcat(msg, index_str);
        strcat(msg, " (length: ");
        strcat(msg, length_str);
        strcat(msg, ")");
        runtime_error_at(msg, line);
    }
    return list->items[index];
}

void runtime_list_set_int_at(RuntimeList* list, int64_t index, int64_t value,
                             int line) {
    int64_t original = index;
    if (index < 0) index += list->length;
    if (index < 0 || index >= list->length) {
        char msg[256];
        char index_str[32];
        char length_str[32];
        fr_int64_to_buf(original, index_str);
        fr_int64_to_buf(list->length, length_str);
        strcpy(msg, "Index error: list index out of range: ");
        strcat(msg, index_str);
        strcat(msg, " (length: ");
        strcat(msg, length_str);
        strcat(msg, ")");
        runtime_error_at(msg, line);
    }
    list->items[index] = value;
}

void runtime_list_set_managed_at(RuntimeList* list, int64_t index, int64_t value,
                                 int line) {
    if (!list) return;
    if (list->elem_type < 0 || list->elem_type == 0) list->elem_type = 4;
    runtime_list_set_int_at(list, index, value, line);
}

RuntimeList* runtime_list_from_array(int64_t* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    if (!list) return NULL;
    list->capacity = count > 0 ? count : 8;
    list->length = count;
    list->items = (int64_t*)malloc((size_t)list->capacity * sizeof(int64_t));
    if (!list->items) return NULL;
    if (count > 0) memcpy(list->items, values, (size_t)count * sizeof(int64_t));
    return list;
}

RuntimeList* runtime_list_from_array_typed(int64_t* values, int64_t count,
                                            int64_t elem_type) {
    RuntimeList* list = runtime_list_from_array(values, count);
    if (list) {
        list->elem_type = (int)elem_type;
        if (elem_type == 4) {
            for (int64_t i = 0; i < count; i++) {
                runtime_retain((void*)values[i]);
                runtime_scope_forget((void*)values[i]);
            }
        }
    }
    return list;
}

static bool runtime_list_contains_value(RuntimeList* list, int64_t value) {
    if (!list) return false;
    for (int64_t i = 0; i < list->length; i++) {
        if (list->elem_type == 1) {
            if (strcmp((const char*)list->items[i], (const char*)value) == 0)
                return true;
        } else if (list->items[i] == value) {
            return true;
        }
    }
    return false;
}

int64_t runtime_contains(RuntimeList* list, int64_t value) {
    return runtime_list_contains_value(list, value) ? 1 : 0;
}

void runtime_list_free(RuntimeList* list) {
    if (!list) return;
    free(list->items);
    free(list);
}

char* runtime_list_to_str(RuntimeList* list) {
    if (!list) return fr_strdup("[]");
    size_t capacity = 256;
    for (int64_t i = 0; i < list->length; i++) {
        if (list->elem_type == 1) capacity += (size_t)strlen((const char*)list->items[i]) + 2;
        else capacity += 32;
    }
    char* result = (char*)malloc(capacity);
    if (!result) return NULL;
    char* out = result;
    *out++ = '[';
    for (int64_t i = 0; i < list->length; i++) {
        if (i) { *out++ = ','; *out++ = ' '; }
        if (list->elem_type == 1) {
            const char* s = (const char*)list->items[i];
            size_t len = (size_t)strlen(s);
            memcpy(out, s, len);
            out += len;
        } else if (list->elem_type == 2) {
            union { int64_t i; double d; } pun;
            pun.i = list->items[i];
            char* s = runtime_float_to_str(pun.d);
            if (s) {
                size_t len = (size_t)strlen(s);
                memcpy(out, s, len);
                out += len;
                free(s);
            }
        } else if (list->elem_type == 3) {
            const char* s = list->items[i] ? "true" : "false";
            size_t len = (size_t)strlen(s);
            memcpy(out, s, len);
            out += len;
        } else {
            char buf[32];
            fr_int64_to_buf(list->items[i], buf);
            size_t len = (size_t)strlen(buf);
            memcpy(out, buf, len);
            out += len;
        }
    }
    *out++ = ']';
    *out = '\0';
    return result;
}

/* ------------------------------------------------------------------------- */
/* Set operations                                                             */
/* ------------------------------------------------------------------------- */

typedef struct {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type;
} RuntimeSet;

typedef struct {
    int64_t* keys;
    int64_t* values;
    int64_t length;
    int64_t capacity;
    int key_type; /* -1 unknown, 0 int, 1 string */
} RuntimeDict;

RuntimeDict* runtime_dict_new(void) {
    RuntimeDict* dict = (RuntimeDict*)fr_obj_alloc(sizeof(RuntimeDict), FR_OBJ_DICT, 0);
    if (!dict) return NULL;
    dict->capacity = 8;
    dict->length = 0;
    dict->key_type = -1;
    dict->keys = (int64_t*)malloc((size_t)dict->capacity * sizeof(int64_t));
    dict->values = (int64_t*)malloc((size_t)dict->capacity * sizeof(int64_t));
    if (!dict->keys || !dict->values) return NULL;
    return dict;
}

static bool runtime_dict_key_eq(RuntimeDict* dict, int64_t a, int64_t b) {
    if (dict->key_type == 1) return strcmp((const char*)a, (const char*)b) == 0;
    return a == b;
}

void runtime_dict_set(RuntimeDict* dict, int64_t key, int64_t value) {
    if (!dict) return;
    if (dict->key_type == -1) dict->key_type = key > 0x100000 ? 1 : 0;
    for (int64_t i = 0; i < dict->length; i++) {
        if (runtime_dict_key_eq(dict, dict->keys[i], key)) {
            dict->values[i] = value;
            return;
        }
    }
    if (dict->length >= dict->capacity) {
        int64_t cap = dict->capacity * 2;
        int64_t* keys = (int64_t*)realloc(dict->keys, (size_t)cap * sizeof(int64_t));
        int64_t* values = (int64_t*)realloc(dict->values, (size_t)cap * sizeof(int64_t));
        if (!keys || !values) return;
        dict->keys = keys;
        dict->values = values;
        dict->capacity = cap;
    }
    dict->keys[dict->length] = key;
    dict->values[dict->length] = value;
    dict->length++;
}

int64_t runtime_dict_get(RuntimeDict* dict, int64_t key) {
    if (!dict) return 0;
    for (int64_t i = 0; i < dict->length; i++) {
        if (runtime_dict_key_eq(dict, dict->keys[i], key)) return dict->values[i];
    }
    return 0;
}

int64_t runtime_dict_contains(RuntimeDict* dict, int64_t key) {
    if (!dict) return 0;
    for (int64_t i = 0; i < dict->length; i++) {
        if (runtime_dict_key_eq(dict, dict->keys[i], key)) return 1;
    }
    return 0;
}

int64_t runtime_dict_len(RuntimeDict* dict) { return dict ? dict->length : 0; }

RuntimeSet* runtime_set_new(void) {
    RuntimeSet* set = (RuntimeSet*)fr_obj_alloc(sizeof(RuntimeSet), FR_OBJ_SET, 0);
    if (!set) return NULL;
    set->capacity = 16;
    set->length = 0;
    set->elem_type = -1;
    set->items = (int64_t*)malloc((size_t)set->capacity * sizeof(int64_t));
    if (!set->items) return NULL;
    return set;
}

static bool runtime_set_equal(RuntimeSet* set, int64_t a, int64_t b) {
    if (set->elem_type == 1) return strcmp((const char*)a, (const char*)b) == 0;
    return a == b;
}

void runtime_set_add(RuntimeSet* set, int64_t value) {
    if (!set) return;
    if (set->elem_type == -1) set->elem_type = value > 0x100000 ? 1 : 0;
    for (int64_t i = 0; i < set->length; i++) {
        if (runtime_set_equal(set, set->items[i], value)) return;
    }
    if (set->elem_type == 4) {
        runtime_retain((void*)value);
        runtime_scope_forget((void*)value);
    }
    if (set->length >= set->capacity) {
        int64_t new_cap = set->capacity * 2;
        int64_t* items = (int64_t*)realloc(
            set->items, (size_t)new_cap * sizeof(int64_t));
        if (!items) return;
        set->items = items;
        set->capacity = new_cap;
    }
    set->items[set->length++] = value;
}

void runtime_set_add_typed(RuntimeSet* set, int64_t value, int elem_type) {
    if (set && set->elem_type == -1) set->elem_type = elem_type;
    runtime_set_add(set, value);
}

void runtime_set_remove(RuntimeSet* set, int64_t value) {
    if (!set) return;
    for (int64_t i = 0; i < set->length; i++) {
        if (runtime_set_equal(set, set->items[i], value)) {
            if (set->elem_type == 4) runtime_release((void*)set->items[i]);
            for (int64_t j = i; j + 1 < set->length; j++)
                set->items[j] = set->items[j + 1];
            set->length--;
            return;
        }
    }
}

int64_t runtime_set_contains(RuntimeSet* set, int64_t value) {
    if (!set) return 0;
    for (int64_t i = 0; i < set->length; i++) {
        if (runtime_set_equal(set, set->items[i], value)) return 1;
    }
    return 0;
}

int64_t runtime_set_len(RuntimeSet* set) { return set ? set->length : 0; }

void runtime_set_free(RuntimeSet* set) {
    if (!set) return;
    free(set->items);
    free(set);
}

char* runtime_set_to_str(RuntimeSet* set) {
    if (!set) return fr_strdup("{}");
    size_t capacity = 256;
    for (int64_t i = 0; i < set->length; i++) capacity += 40;
    char* result = (char*)malloc(capacity);
    if (!result) return NULL;
    char* out = result;
    *out++ = '{';
    for (int64_t i = 0; i < set->length; i++) {
        if (i) { *out++ = ','; *out++ = ' '; }
        if (set->elem_type == 1) {
            const char* s = (const char*)set->items[i];
            size_t len = (size_t)strlen(s);
            memcpy(out, s, len);
            out += len;
        } else {
            char buf[32];
            fr_int64_to_buf(set->items[i], buf);
            size_t len = (size_t)strlen(buf);
            memcpy(out, buf, len);
            out += len;
        }
    }
    *out++ = '}';
    *out = '\0';
    return result;
}

/* ------------------------------------------------------------------------- */
/* Error handling / exceptions                                                */
/* ------------------------------------------------------------------------- */

void int64_to_str(int64_t value, char* buffer);

#define MAX_EXCEPTION_HANDLERS 256
typedef struct {
    char* exc_type;
    uint64_t jump_buffer[8];
    int64_t scope_depth;
} RuntimeExceptionHandler;

static RuntimeExceptionHandler exception_handlers[MAX_EXCEPTION_HANDLERS];
static int exception_handler_count = 0;

void runtime_error_at(const char* message, int line) {
    const char* exc_type = "RuntimeError";
    if (strstr(message, "division by zero")) exc_type = "ZeroDivisionError";
    else if (strstr(message, "Index error")) exc_type = "IndexError";

    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];
        if (handler->exc_type[0] == '\0' ||
            strcmp(handler->exc_type, exc_type) == 0) {
            runtime_scope_unwind(handler->scope_depth);
            longjmp(handler->jump_buffer, 1);
        }
    }

    char full[1024];
    char line_str[32];
    fr_int64_to_buf(line, line_str);
    strcpy(full, "?");
    strcat(full, line_str);
    strcat(full, ",0:");
    strcat(full, message);
    strcat(full, "\n");
    fr_fputs(full, 2);
    fr_exit(1);
}

void runtime_exception_init(void) { exception_handler_count = 0; }

void* runtime_exception_push(const char* exc_type) {
    if (exception_handler_count >= MAX_EXCEPTION_HANDLERS) {
        fr_fputs("Runtime error: exception handler depth exceeded\n", 2);
        fr_exit(1);
    }
    RuntimeExceptionHandler* handler = &exception_handlers[exception_handler_count];
    handler->exc_type = (char*)(exc_type ? exc_type : "");
    handler->scope_depth = fr_scope_depth;
    return (void*)(int64_t)exception_handler_count++;
}

void* runtime_exception_get_jump_buffer(void) {
    if (exception_handler_count == 0) return NULL;
    return &exception_handlers[exception_handler_count - 1].jump_buffer;
}

void runtime_exception_pop(void) {
    if (exception_handler_count > 0) exception_handler_count--;
}

__attribute__((noinline, optimize("no-omit-frame-pointer")))
void runtime_exception_raise(const char* exc_type, const char* message) {
    if (!exc_type) exc_type = "";
    if (!message) message = "";
    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];
        if (handler->exc_type[0] == '\0' ||
            strcmp(handler->exc_type, exc_type) == 0) {
            runtime_scope_unwind(handler->scope_depth);
            longjmp(handler->jump_buffer, 1);
        }
    }
    char full[1024];
    strcpy(full, "[");
    strcat(full, exc_type);
    strcat(full, "] ");
    strcat(full, message);
    strcat(full, "\n");
    fr_fputs(full, 2);
    fr_exit(1);
}

__attribute__((noinline, optimize("no-omit-frame-pointer")))
void runtime_exception_raise_at(const char* exc_type, const char* message,
                                int line) {
    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];
        if (handler->exc_type[0] == '\0' ||
            strcmp(handler->exc_type, exc_type) == 0) {
            runtime_scope_unwind(handler->scope_depth);
            longjmp(handler->jump_buffer, 1);
        }
    }
    char full[1024];
    char line_str[32];
    fr_int64_to_buf(line, line_str);
    strcpy(full, "?");
    strcat(full, line_str);
    strcat(full, ",0:[");
    strcat(full, exc_type);
    strcat(full, "] ");
    strcat(full, message);
    strcat(full, "\n");
    fr_fputs(full, 2);
    fr_exit(1);
}

void runtime_check_div_zero_i64_at(int64_t divisor, int line) {
    if (divisor == 0) runtime_error_at("integer division by zero", line);
}

void runtime_check_div_zero_f64_at(double divisor, int line) {
    if (divisor == 0.0) runtime_error_at("float division by zero", line);
}

void runtime_check_div_zero_i64(int64_t divisor) {
    if (divisor == 0) runtime_exception_raise("ZeroDivisionError",
                                              "integer division by zero");
}

void runtime_check_div_zero_f64(double divisor) {
    if (divisor == 0.0) runtime_exception_raise("ZeroDivisionError",
                                                "float division by zero");
}

void runtime_assert(bool condition, const char* message) {
    if (!condition) {
        if (message && message[0] != '\0') {
            fr_fputs(message, 1);
            fr_putchar('\n');
        } else {
            fr_fputs("Assertion failed\n", 1);
        }
        fr_exit(1);
    }
}

/* ------------------------------------------------------------------------- */
/* Process / time                                                             */
/* ------------------------------------------------------------------------- */

int64_t runtime_fork(void) {
    int64_t pid = syscall1(SYS_FORK, 0);
    return pid;
}

int64_t runtime_wait(int64_t pid) {
    int status = 0;
    int64_t result = syscall6(SYS_WAIT4, pid, (int64_t)&status, 0, 0, 0, 0);
    if (result < 0) return -1;
    return (status & 0x7f) == 0 ? ((status >> 8) & 0xff) : status;
}

void runtime_sleep(double seconds) {
    if (seconds <= 0.0) return;
    int64_t sec = (int64_t)seconds;
    int64_t nsec = (int64_t)((seconds - (double)sec) * 1000000000.0);
    int64_t ts[2] = {sec, nsec};
    syscall3(SYS_NANOSLEEP, (int64_t)ts, 0, 0);
}

void runtime_exit(int64_t status) { fr_exit((int)status); }

/* ------------------------------------------------------------------------- */
/* File I/O                                                                   */
/* ------------------------------------------------------------------------- */

static int fr_open_flags(const char* mode) {
    bool plus = false;
    if (!mode) return O_RDONLY;
    for (const char* p = mode; *p; p++) if (*p == '+') plus = true;
    switch (mode[0]) {
        case 'w':
            return O_CREAT | O_TRUNC | (plus ? O_RDWR : O_WRONLY);
        case 'a':
            return O_CREAT | O_APPEND | (plus ? O_RDWR : O_WRONLY);
        case 'r':
        default:
            return plus ? O_RDWR : O_RDONLY;
    }
}

int64_t runtime_fopen(const char* path, const char* mode) {
    int flags = fr_open_flags(mode);
    int64_t fd = syscall6(SYS_OPENAT, AT_FDCWD, (int64_t)path, flags, 0666, 0, 0);
    return fd;
}

int64_t runtime_fwrite(int64_t fd, const char* data) {
    if (fd < 0 || !data) return 0;
    size_t len = (size_t)strlen(data);
    size_t off = 0;
    while (off < len) {
        int64_t n = syscall3(SYS_WRITE, fd, (int64_t)(data + off),
                             (int64_t)(len - off));
        if (n <= 0) break;
        off += (size_t)n;
    }
    return (int64_t)off;
}

char* runtime_fread(int64_t fd, int64_t size) {
    if (fd < 0) return fr_strdup("");
    if (size < 0) {
        int64_t cur = syscall3(SYS_LSEEK, fd, 0, SEEK_CUR);
        int64_t end = syscall3(SYS_LSEEK, fd, 0, SEEK_END);
        syscall3(SYS_LSEEK, fd, cur, SEEK_SET);
        if (end < cur) return fr_strdup("");
        size = end - cur;
    }
    char* buffer = (char*)malloc((size_t)size + 1);
    if (!buffer) return NULL;
    size_t got = 0;
    while (got < (size_t)size) {
        int64_t n = syscall3(SYS_READ, fd, (int64_t)(buffer + got),
                             (int64_t)((size_t)size - got));
        if (n <= 0) break;
        got += (size_t)n;
    }
    buffer[got] = '\0';
    return buffer;
}

void runtime_fclose(int64_t fd) {
    if (fd >= 0) syscall1(SYS_CLOSE, fd);
}

/* ------------------------------------------------------------------------- */
/* Input                                                                      */
/* ------------------------------------------------------------------------- */

char* runtime_input(void) {
    size_t capacity = 128;
    size_t length = 0;
    char* buffer = (char*)malloc(capacity);
    if (!buffer) return NULL;
    while (1) {
        char c;
        int64_t n = syscall3(SYS_READ, 0, (int64_t)&c, 1);
        if (n <= 0) break;
        if (c == '\n') break;
        if (c == '\r') continue;
        if (length + 1 >= capacity) {
            capacity *= 2;
            char* grown = (char*)realloc(buffer, capacity);
            if (!grown) break;
            buffer = grown;
        }
        buffer[length++] = c;
    }
    buffer[length] = '\0';
    return buffer;
}

/* ------------------------------------------------------------------------- */
/* Sockets (Linux syscalls)                                                   */
/* ------------------------------------------------------------------------- */

#define SYS_SOCKET     41
#define SYS_CONNECT    42
#define SYS_ACCEPT     43
#define SYS_SENDTO     44
#define SYS_RECVFROM   45
#define SYS_SHUTDOWN   48
#define SYS_BIND       49
#define SYS_LISTEN     50
#define SYS_SETSOCKOPT 54

#define AF_INET_       2
#define SOCK_STREAM_   1
#define SOCK_DGRAM_    2
#define SOL_SOCKET_    1
#define SO_REUSEADDR_  2
#define SO_KEEPALIVE_  9
#define SO_BROADCAST_  6
#define SO_RCVBUF_     8
#define SO_SNDBUF_     7
#define IPPROTO_TCP_   6
#define IPPROTO_IP_    0
#define MSG_NOSIGNAL_  0x4000

typedef struct {
    uint16_t family;
    uint16_t port;   /* network byte order */
    uint32_t addr;   /* network byte order */
    uint8_t zero[8];
} FrSockaddrIn;

static bool fr_streq_ci(const char* a, const char* b) {
    if (!a || !b) return false;
    while (*a && *b) {
        char ca = *a, cb = *b;
        if (ca >= 'A' && ca <= 'Z') ca = (char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (char)(cb - 'A' + 'a');
        if (ca != cb) return false;
        a++; b++;
    }
    return *a == *b;
}

static uint16_t fr_htons(uint16_t v) {
    return (uint16_t)((v << 8) | (v >> 8));
}

static int fr_parse_ipv4(const char* host, uint32_t* out) {
    if (!host || !*host) { *out = 0; return 0; }
    if (fr_streq_ci(host, "localhost")) {
        *out = fr_htons((uint16_t)(127 | (0 << 8))); /* 127.0.0.1 bytes */
        *out = ((uint32_t)127) | ((uint32_t)0 << 8) | ((uint32_t)0 << 16) | ((uint32_t)1 << 24);
        return 0;
    }
    uint32_t parts[4] = {0, 0, 0, 0};
    int part = 0;
    for (const char* p = host; *p; p++) {
        if (*p == '.') {
            part++;
            if (part > 3) return -1;
        } else if (*p >= '0' && *p <= '9') {
            parts[part] = parts[part] * 10 + (uint32_t)(*p - '0');
            if (parts[part] > 255) return -1;
        } else {
            return -1;
        }
    }
    if (part != 3) return -1;
    *out = parts[0] | (parts[1] << 8) | (parts[2] << 16) | (parts[3] << 24);
    return 0;
}

int64_t runtime_socket_create(const char* family, const char* type) {
    int fam = AF_INET_;
    if (family && fr_streq_ci(family, "inet6")) fam = 10;
    else if (family && fr_streq_ci(family, "unix")) fam = 1;
    int typ = SOCK_STREAM_;
    if (type && fr_streq_ci(type, "dgram")) typ = SOCK_DGRAM_;
    else if (type && fr_streq_ci(type, "raw")) typ = 3;

    int64_t fd = syscall3(SYS_SOCKET, fam, typ, 0);
    if (fd >= 0) {
        int one = 1;
        syscall6(SYS_SETSOCKOPT, fd, SOL_SOCKET_, SO_REUSEADDR_,
                 (int64_t)&one, sizeof(one), 0);
    }
    return fd;
}

int64_t runtime_socket_connect(int64_t fd, const char* host, int64_t port) {
    FrSockaddrIn addr;
    memset(&addr, 0, sizeof(addr));
    addr.family = AF_INET_;
    addr.port = fr_htons((uint16_t)port);
    if (fr_parse_ipv4(host, &addr.addr) != 0) return -1;
    return syscall3(SYS_CONNECT, fd, (int64_t)&addr, sizeof(addr));
}

int64_t runtime_socket_bind(int64_t fd, const char* host, int64_t port) {
    FrSockaddrIn addr;
    memset(&addr, 0, sizeof(addr));
    addr.family = AF_INET_;
    addr.port = fr_htons((uint16_t)port);
    if (fr_parse_ipv4(host, &addr.addr) != 0) return -1;
    return syscall3(SYS_BIND, fd, (int64_t)&addr, sizeof(addr));
}

int64_t runtime_socket_listen(int64_t fd, int64_t backlog) {
    return syscall3(SYS_LISTEN, fd, backlog, 0);
}

int64_t runtime_socket_accept(int64_t fd) {
    return syscall3(SYS_ACCEPT, fd, 0, 0);
}

int64_t runtime_socket_send(int64_t fd, const char* data) {
    if (!data) return 0;
    size_t len = (size_t)strlen(data);
    size_t sent = 0;
    while (sent < len) {
        int64_t n = syscall6(SYS_SENDTO, fd, (int64_t)(data + sent),
                             (int64_t)(len - sent), MSG_NOSIGNAL_, 0, 0);
        if (n <= 0) break;
        sent += (size_t)n;
    }
    return (int64_t)sent;
}

int64_t runtime_socket_sendall(int64_t fd, const char* data) {
    return runtime_socket_send(fd, data);
}

char* runtime_socket_recv(int64_t fd, int64_t size) {
    if (fd < 0) return fr_strdup("");
    if (size <= 0) size = 4096;
    char* buffer = (char*)malloc((size_t)size + 1);
    if (!buffer) return fr_strdup("");
    int64_t n = syscall6(SYS_RECVFROM, fd, (int64_t)buffer, size, 0, 0, 0);
    if (n < 0) n = 0;
    buffer[n] = '\0';
    return buffer;
}

int64_t runtime_socket_close(int64_t fd) {
    if (fd < 0) return -1;
    return syscall1(SYS_CLOSE, fd);
}

int64_t runtime_socket_setsockopt(int64_t fd, const char* level,
                                  const char* option, int64_t value) {
    int lev = SOL_SOCKET_;
    if (level && fr_streq_ci(level, "IPPROTO_TCP")) lev = IPPROTO_TCP_;
    else if (level && fr_streq_ci(level, "IPPROTO_IP")) lev = IPPROTO_IP_;

    int opt = SO_REUSEADDR_;
    if (option && fr_streq_ci(option, "SO_KEEPALIVE")) opt = SO_KEEPALIVE_;
    else if (option && fr_streq_ci(option, "SO_BROADCAST")) opt = SO_BROADCAST_;
    else if (option && fr_streq_ci(option, "SO_RCVBUF")) opt = SO_RCVBUF_;
    else if (option && fr_streq_ci(option, "SO_SNDBUF")) opt = SO_SNDBUF_;

    int val = (int)value;
    return syscall6(SYS_SETSOCKOPT, fd, lev, opt, (int64_t)&val,
                    sizeof(val), 0);
}

int64_t runtime_socket_shutdown(int64_t fd, int64_t how) {
    return syscall3(SYS_SHUTDOWN, fd, how, 0);
}

/* ------------------------------------------------------------------------- */
/* Init / globals                                                             */
/* ------------------------------------------------------------------------- */

void int64_to_str(int64_t value, char* buffer) {
    fr_int64_to_buf(value, buffer);
}

static void fr_release_fields(char* memory, int64_t mask) {
    for (int i = 0; i < 64; i++) {
        if (mask & ((int64_t)1 << i)) {
            runtime_release(((void**)memory)[i]);
        }
    }
}

void runtime_release(void* ptr) {
    if (!fr_obj_valid(ptr)) return;
    FrObjHeader* header = ((FrObjHeader*)ptr) - 1;
    if (--header->refcount > 0) return;
    header->magic = 0;

    if (header->kind == FR_OBJ_STRUCT) {
        fr_release_fields((char*)(header + 1), header->aux);
    } else if (header->kind == FR_OBJ_LIST) {
        RuntimeList* list = (RuntimeList*)(header + 1);
        if (list->elem_type == 4) {
            for (int64_t i = 0; i < list->length; i++) {
                runtime_release((void*)list->items[i]);
            }
        }
        free(list->items);
    } else if (header->kind == FR_OBJ_SET) {
        RuntimeSet* set = (RuntimeSet*)(header + 1);
        if (set->elem_type == 4) {
            for (int64_t i = 0; i < set->length; i++) {
                runtime_release((void*)set->items[i]);
            }
        }
        free(set->items);
    } else if (header->kind == FR_OBJ_DICT) {
        RuntimeDict* dict = (RuntimeDict*)(header + 1);
        free(dict->keys);
        free(dict->values);
    }
    free(header);
}

void runtime_init(void) {
    init_heap();
    runtime_exception_init();
    fr_scope_depth = 0;
}

int64_t _fr_global_vars[256] = {0};
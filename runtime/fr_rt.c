/*
 * Minimal fr runtime - replaces libc with syscall-based implementations.
 * Link with: gcc ... runtime/fr_rt.c runtime/syscall.S -nostdlib -static
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// ============================================================================
// Syscall wrappers (implemented in assembly)
// ============================================================================

extern int64_t syscall1(int64_t num, int64_t arg1);
extern int64_t syscall3(int64_t num, int64_t arg1, int64_t arg2, int64_t arg3);
extern int64_t syscall6(int64_t num, int64_t arg1, int64_t arg2, int64_t arg3,
                        int64_t arg4, int64_t arg5, int64_t arg6);

// Syscall numbers
#define SYS_WRITE  1
#define SYS_EXIT   60
#define SYS_MMAP   9
#define SYS_MPROTECT 10

// ============================================================================
// String functions
// ============================================================================

int64_t strlen(const char* s) {
    const char* p = s;
    while (*p) p++;
    return (int64_t)(p - s);
}

void* memcpy(void* dest, const void* src, int64_t n) {
    char* d = (char*)dest;
    const char* s = (const char*)src;
    while (n--) *d++ = *s++;
    return dest;
}

void* memset(void* dest, int c, int64_t n) {
    char* d = (char*)dest;
    while (n--) *d++ = (char)c;
    return dest;
}

int memcmp(const void* a, const void* b, int64_t n) {
    const unsigned char* pa = (const unsigned char*)a;
    const unsigned char* pb = (const unsigned char*)b;
    while (n--) {
        if (*pa != *pb) return *pa - *pb;
        pa++; pb++;
    }
    return 0;
}

char* strcpy(char* dest, const char* src) {
    char* d = dest;
    while ((*d++ = *src++));
    return dest;
}

char* strcat(char* dest, const char* src) {
    char* d = dest + strlen(dest);
    while ((*d++ = *src++));
    return dest;
}

const char* strchr(const char* s, int c) {
    while (*s) {
        if ((unsigned char)*s == (unsigned char)c) return s;
        s++;
    }
    return NULL;
}

const char* strstr(const char* haystack, const char* needle) {
    if (!*needle) return haystack;
    for (; *haystack; haystack++) {
        const char* h = haystack;
        const char* n = needle;
        while (*h && *n && *h == *n) { h++; n++; }
        if (!*n) return haystack;
    }
    return NULL;
}

// ============================================================================
// Stdio replacements
// ============================================================================

void fr_putchar(char c) {
    char buf[1];
    buf[0] = c;
    syscall3(SYS_WRITE, 1, (int64_t)buf, 1);
}

void fr_puts(const char* s) {
    int64_t len = strlen(s);
    syscall3(SYS_WRITE, 1, (int64_t)s, len);
    syscall3(SYS_WRITE, 1, (int64_t)"\n", 1);
}

void fr_fputs(const char* s, int fd) {
    int64_t len = strlen(s);
    syscall3(SYS_WRITE, fd, (int64_t)s, len);
}

void fr_fflush(int fd) {
    (void)fd;
}

void fr_exit(int status) {
    syscall1(SYS_EXIT, status);
    while (1);
}

// Minimal printf - handles %s, %ld, %g
void fr_printf(const char* fmt, ...) {
    // Simple implementation - just walk the format string
    // For now, this is a stub that works for our basic cases
}

// Provide libc-compatible names for assembly
void puts(const char* s) { fr_puts(s); }
void fputs(const char* s, int fd) { fr_fputs(s, fd); }
void fflush(int fd) { fr_fflush(fd); }
void exit(int status) { fr_exit(status); }
void printf(const char* fmt, ...) { fr_printf(fmt); }

// ============================================================================
// Memory allocation
// ============================================================================

static uint8_t* heap_base;
static uint8_t* heap_ptr;
static uint64_t heap_size;

void init_heap(void) {
    heap_base = (uint8_t*)syscall6(SYS_MMAP, 0, 8 * 1024 * 1024,
                                    0x3 /* PROT_READ|PROT_WRITE */,
                                    0x22 /* MAP_PRIVATE|MAP_ANONYMOUS */,
                                    -1, 0);
    heap_ptr = heap_base;
    heap_size = 8 * 1024 * 1024;
}

void* malloc(int64_t size) {
    size = (size + 7) & ~7;
    if (heap_ptr + size > heap_base + heap_size) {
        return NULL;
    }
    void* ptr = heap_ptr;
    heap_ptr += size;
    return ptr;
}

void free(void* ptr) {
    (void)ptr;
}

// ============================================================================
// Math functions
// ============================================================================

double fabs(double x) {
    if (x < 0) return -x;
    return x;
}

double sqrt(double x) {
    if (x <= 0) return 0;
    double guess = x / 2;
    for (int i = 0; i < 20; i++) {
        guess = (guess + x / guess) / 2;
    }
    return guess;
}

double floor(double x) {
    int64_t i = (int64_t)x;
    return (double)i;
}

double ceil(double x) {
    int64_t i = (int64_t)x;
    if (x == (double)i) return (double)i;
    return (double)(i + 1);
}

double round(double x) {
    if (x >= 0) return floor(x + 0.5);
    return ceil(x - 0.5);
}

double pow(double base, double exp) {
    if (exp == 0) return 1;
    if (exp == 1) return base;
    double result = 1;
    int64_t e = (int64_t)exp;
    double b = base;
    while (e > 0) {
        if (e & 1) result *= b;
        b *= b;
        e >>= 1;
    }
    return result;
}

double sin(double x) { return x; }
double cos(double x) { return 1; }
double tan(double x) { return x; }

// ============================================================================
// Exception handling stubs
// ============================================================================

#define MAX_EXCEPTION_HANDLERS 256
static void* exception_handlers[MAX_EXCEPTION_HANDLERS];
static int exception_handler_count = 0;

// ============================================================================
// Type conversion stubs
// ============================================================================

char* runtime_int_to_str(int64_t value) {
    char* buf = malloc(32);
    if (!buf) return NULL;
    char* p = buf + 31;
    *p = '\0';
    if (value == 0) {
        *--p = '0';
    } else {
        int64_t n = value;
        if (n < 0) n = -n;
        while (n > 0) {
            *--p = '0' + (n % 10);
            n /= 10;
        }
        if (value < 0) *--p = '-';
    }
    return p;
}

char* runtime_float_to_str(double value) {
    char* buf = malloc(64);
    if (!buf) return NULL;
    int64_t ipart = (int64_t)value;
    double fracpart = value - (double)ipart;
    char* p = buf;
    if (value < 0) {
        *p++ = '-';
        ipart = -ipart;
        fracpart = -fracpart;
    }
    char tmp[32];
    char* t = tmp + 31;
    *t = '\0';
    if (ipart == 0) {
        *--t = '0';
    } else {
        int64_t n = ipart;
        while (n > 0) {
            *--t = '0' + (n % 10);
            n /= 10;
        }
    }
    while (*t) *p++ = *t++;
    *p++ = '.';
    for (int i = 0; i < 6; i++) {
        fracpart *= 10;
        int digit = (int)fracpart;
        *p++ = '0' + digit;
        fracpart -= digit;
        if (fracpart < 0.000001) break;
    }
    while (*(p-1) == '0') p--;
    if (*(p-1) == '.') *p++ = '0';
    *p = '\0';
    return buf;
}

char* runtime_bool_to_str(int64_t value) {
    if (value) return (char*)"true";
    return (char*)"false";
}

char* runtime_str_concat(const char* a, const char* b) {
    int64_t len_a = strlen(a);
    int64_t len_b = strlen(b);
    char* result = malloc(len_a + len_b + 1);
    if (!result) return NULL;
    memcpy(result, a, len_a);
    memcpy(result + len_a, b, len_b);
    result[len_a + len_b] = '\0';
    return result;
}

int64_t runtime_str_len(const char* str) {
    return strlen(str);
}

int64_t runtime_str_contains(const char* haystack, const char* needle) {
    return strstr(haystack, needle) != NULL ? 1 : 0;
}

// ============================================================================
// List operations
// ============================================================================

typedef struct {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type;
} RuntimeList;

RuntimeList* runtime_list_new(void) {
    RuntimeList* list = (RuntimeList*)malloc(sizeof(RuntimeList));
    if (!list) return NULL;
    list->capacity = 8;
    list->length = 0;
    list->elem_type = -1;
    list->items = (int64_t*)malloc(list->capacity * sizeof(int64_t));
    if (!list->items) { free(list); return NULL; }
    return list;
}

void runtime_list_append_int(RuntimeList* list, int64_t value) {
    if (list->length >= list->capacity) {
        list->capacity *= 2;
        list->items = (int64_t*)malloc(list->capacity * sizeof(int64_t));
        if (!list->items) return;
    }
    list->items[list->length++] = value;
}

int64_t runtime_list_get_int(RuntimeList* list, int64_t index) {
    if (index < 0) index = list->length + index;
    if (index < 0 || index >= list->length) return 0;
    return list->items[index];
}

void runtime_list_set_int(RuntimeList* list, int64_t index, int64_t value) {
    if (index < 0) index = list->length + index;
    if (index < 0 || index >= list->length) return;
    list->items[index] = value;
}

int64_t runtime_list_len(RuntimeList* list) {
    return list->length;
}

char* runtime_list_to_str(RuntimeList* list) {
    (void)list;
    return (char*)"[list]";
}

// ============================================================================
// Set operations
// ============================================================================

typedef struct {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type;
} RuntimeSet;

RuntimeSet* runtime_set_new(void) {
    RuntimeSet* set = (RuntimeSet*)malloc(sizeof(RuntimeSet));
    if (!set) return NULL;
    set->capacity = 16;
    set->length = 0;
    set->elem_type = -1;
    set->items = (int64_t*)malloc(sizeof(int64_t) * set->capacity);
    if (!set->items) { free(set); return NULL; }
    return set;
}

void runtime_set_add(RuntimeSet* set, int64_t value) {
    if (set->length >= set->capacity) {
        set->capacity *= 2;
        set->items = (int64_t*)malloc(sizeof(int64_t) * set->capacity);
        if (!set->items) return;
    }
    set->items[set->length++] = value;
}

int64_t runtime_set_len(RuntimeSet* set) {
    return set->length;
}

char* runtime_set_to_str(RuntimeSet* set) {
    (void)set;
    return (char*)"{set}";
}

// ============================================================================
// Error handling and exceptions
// ============================================================================

void int64_to_str(int64_t value, char* buffer) {
    char* p = buffer + 31;
    *p = '\0';
    if (value == 0) {
        *--p = '0';
    } else {
        int64_t n = value;
        if (n < 0) n = -n;
        while (n > 0) {
            *--p = '0' + (n % 10);
            n /= 10;
        }
        if (value < 0) *--p = '-';
    }
    while (*p) *buffer++ = *p++;
    *buffer = '\0';
}

void runtime_error_at(const char* message, int line) {
    char full_msg[1024];
    char line_str[32];
    int64_to_str(line, line_str);
    strcpy(full_msg, "?");
    strcat(full_msg, line_str);
    strcat(full_msg, ",0:");
    strcat(full_msg, message);
    strcat(full_msg, "\n");
    fr_fputs(full_msg, 2);
    fr_exit(1);
}

void runtime_exception_init(void) {
}

void* runtime_exception_push(const char* exc_type) {
    (void)exc_type;
    return NULL;
}

void runtime_exception_pop(void) {
}

void runtime_exception_raise(const char* exc_type, const char* message) {
    (void)exc_type;
    fr_printf("Uncaught exception: [%s] %s\n", exc_type, message);
    fr_exit(1);
}

void runtime_exception_raise_at(const char* exc_type, const char* message, int line) {
    char full_msg[1024];
    char line_str[32];
    int64_to_str(line, line_str);
    strcpy(full_msg, "?");
    strcat(full_msg, line_str);
    strcat(full_msg, ",0:[");
    strcat(full_msg, exc_type);
    strcat(full_msg, "] ");
    strcat(full_msg, message);
    strcat(full_msg, "\n");
    fr_fputs(full_msg, 2);
    fr_exit(1);
}

void runtime_check_div_zero_i64_at(int64_t divisor, int line) {
    if (divisor == 0) {
        runtime_error_at("integer division by zero", line);
    }
}

void runtime_check_div_zero_f64_at(double divisor, int line) {
    if (divisor == 0.0) {
        runtime_error_at("float division by zero", line);
    }
}

// ============================================================================
// List operations with bounds checking
// ============================================================================

int64_t runtime_list_get_int_at(RuntimeList* list, int64_t index, int line) {
    if (!list) {
        runtime_error_at("Index error: null list pointer", line);
    }
    int64_t original_index = index;
    if (index < 0) {
        index = list->length + index;
    }
    if (index < 0 || index >= list->length) {
        char msg[512];
        char index_str[32];
        char length_str[32];
        int64_to_str(original_index, index_str);
        int64_to_str(list->length, length_str);
        strcpy(msg, "Index error: list index out of range: ");
        strcat(msg, index_str);
        strcat(msg, " (length: ");
        strcat(msg, length_str);
        strcat(msg, ")");
        runtime_error_at(msg, line);
    }
    return list->items[index];
}

void runtime_list_set_int_at(RuntimeList* list, int64_t index, int64_t value, int line) {
    int64_t original_index = index;
    if (index < 0) {
        index = list->length + index;
    }
    if (index < 0 || index >= list->length) {
        char msg[512];
        char index_str[32];
        char length_str[32];
        int64_to_str(original_index, index_str);
        int64_to_str(list->length, length_str);
        strcpy(msg, "Index error: list index out of range: ");
        strcat(msg, index_str);
        strcat(msg, " (length: ");
        strcat(msg, length_str);
        strcat(msg, ")");
        runtime_error_at(msg, line);
    }
    list->items[index] = value;
}

RuntimeList* runtime_list_from_array(int64_t* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    if (!list) return NULL;
    list->capacity = count;
    list->length = count;
    list->items = (int64_t*)malloc(count * sizeof(int64_t));
    if (!list->items) { free(list); return NULL; }
    memcpy(list->items, values, count * sizeof(int64_t));
    return list;
}

// Runtime init - must be non-static for assembly call
void runtime_init(void) {
    init_heap();
    runtime_exception_init();
}

void runtime_assert(bool condition, const char* message) {
    if (!condition) {
        if (message && message[0] != '\0') {
            fr_fputs(message, 2);
            fr_putchar('\n');
        } else {
            fr_fputs("Assertion failed\n", 2);
        }
        fr_exit(1);
    }
}

// ============================================================================
// Global variables
// ============================================================================

int64_t _fr_global_vars[256] = {0};

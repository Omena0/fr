/*
 * Runtime Library Implementation for fr x86_64 Compiled Code
 */

#include "runtime_lib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/wait.h>

// Global state for error formatting
static int runtime_test_mode = -1;  // -1 = uninitialized, 0 = user mode, 1 = test mode
static const char* runtime_source_file = NULL;
static const char** runtime_source_lines = NULL;
static int runtime_source_line_count = 0;

// Check if we're in test mode (returns 1 for test mode, 0 for user mode)
static int is_test_mode() {
    if (runtime_test_mode == -1) {
        // Check environment variable on first call
        const char* env = getenv("FR_TEST_MODE");
        runtime_test_mode = (env && strcmp(env, "1") == 0) ? 1 : 0;
    }
    return runtime_test_mode;
}

// Set source file information for error reporting
void runtime_set_source_info(const char* filename, const char* source) {
    runtime_source_file = filename;

    // Count lines
    runtime_source_line_count = 1;
    for (const char* p = source; *p; p++) {
        if (*p == '\n') runtime_source_line_count++;
    }

    // Split source into lines
    runtime_source_lines = (const char**)malloc(runtime_source_line_count * sizeof(char*));
    int line_idx = 0;
    const char* line_start = source;

    for (const char* p = source; *p; p++) {
        if (*p == '\n') {
            size_t len = p - line_start;
            char* line = (char*)malloc(len + 1);
            memcpy(line, line_start, len);
            line[len] = '\0';
            runtime_source_lines[line_idx++] = line;
            line_start = p + 1;
        }
    }

    // Last line (if doesn't end with newline)
    if (line_start[0] != '\0') {
        runtime_source_lines[line_idx] = strdup(line_start);
    }
}

// ============================================================================
// Basic I/O
// ============================================================================

void runtime_print_int(int64_t value) {
    printf("%ld", value);
    fflush(stdout);
}

void runtime_println_int(int64_t value) {
    printf("%ld\n", value);
}

void runtime_print_float(double value) {
    printf("%f", value);
    fflush(stdout);
}

void runtime_println_float(double value) {
    // Format float to match Python's str() behavior: show at least 1 decimal place
    // If value is whole number, show .0; otherwise show up to 6 significant digits
    if (value == (long long)value && value >= -1e15 && value < 1e15) {
        // Whole number
        printf("%.1f\n", value);
    } else {
        // Use %g for compact representation of decimals
        printf("%g\n", value);
    }
}

void runtime_print_str(const char* str) {
    printf("%s", str);
    fflush(stdout);
}

void runtime_println_str(const char* str) {
    printf("%s\n", str);
}

void runtime_print(int64_t value) {
    // Smart print that handles multiple types
    // Check if value looks like a pointer (is in a valid memory range)
    if (value > 0x100000) {
        // Likely a pointer to a string
        runtime_print_str((const char*)value);
    } else {
        // Likely a regular integer
        runtime_print_int(value);
    }
}

void runtime_println(int64_t value) {
    // Smart println that handles multiple types
    // Check if value looks like a pointer (is in a valid memory range)
    if (value > 0x100000) {
        // Likely a pointer to a string
        runtime_println_str((const char*)value);
    } else {
        // Likely a regular integer
        runtime_println_int(value);
    }
}

// ============================================================================
// String Operations
// ============================================================================

char* runtime_str_concat(const char* a, const char* b) {
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    char* result = malloc(len_a + len_b + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    strcpy(result, a);
    strcat(result, b);
    return result;
}

// Checked wrapper that validates pointers before calling runtime_str_concat.
char* runtime_str_concat_checked(const char* a, const char* b) {
    if (!a || !b) {
        fprintf(stderr, "runtime_str_concat_checked: invalid args a=%p b=%p\n", (void*)a, (void*)b);
        // Provide more debugging context, then abort to surface the issue
        exit(1);
    }
    return runtime_str_concat(a, b);
}

int64_t runtime_str_len(const char* str) {
    return (int64_t)strlen(str);
}

char* runtime_str_get_char(const char* str, int64_t index) {
    int64_t len = (int64_t)strlen(str);

    // Handle negative indices
    if (index < 0) {
        index = len + index;
    }

    if (index < 0 || index >= len) {
        fprintf(stderr, "Runtime error: string index out of bounds\n");
        exit(1);
    }

    char* result = malloc(2);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    result[0] = str[index];
    result[1] = '\0';
    return result;
}

char* runtime_str_upper(const char* str) {
    size_t len = strlen(str);
    char* result = malloc(len + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    for (size_t i = 0; i < len; i++) {
        result[i] = toupper(str[i]);
    }
    result[len] = '\0';
    return result;
}

char* runtime_str_lower(const char* str) {
    size_t len = strlen(str);
    char* result = malloc(len + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    for (size_t i = 0; i < len; i++) {
        result[i] = tolower(str[i]);
    }
    result[len] = '\0';
    return result;
}

char* runtime_int_to_str(int64_t value) {
    char* result = malloc(32);  // Enough for any int64
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }

    // Manual int to string conversion
    if (value == 0) {
        result[0] = '0';
        result[1] = '\0';
    } else {
        // Handle negative numbers
        int is_negative = value < 0;
        if (is_negative) value = -value;

        // Extract digits in reverse order
        int len = 0;
        int64_t temp = value;
        while (temp > 0) {
            result[len++] = '0' + (temp % 10);
            temp /= 10;
        }

        // Add negative sign if needed
        if (is_negative) {
            result[len++] = '-';
        }

        // Reverse the string
        for (int i = 0; i < len / 2; i++) {
            char tmp = result[i];
            result[i] = result[len - 1 - i];
            result[len - 1 - i] = tmp;
        }

        result[len] = '\0';
    }

    return result;
}

char* runtime_float_to_str(double value) {
    char* result = malloc(64);  // Enough for most floats
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    // For whole numbers, ensure .0 is included
    // Check if value is a whole number
    if (value == (double)(long long)value && value >= -1e15 && value <= 1e15) {
        // It's a whole number, format with .0
        snprintf(result, 64, "%.1f", value);
    } else {
        // Use %g for non-whole numbers
        snprintf(result, 64, "%g", value);
    }
    return result;
}

char* runtime_bool_to_str(int64_t value) {
    // Convert boolean to "true" or "false"
    // Any non-zero value is true, zero is false
    char* result = malloc(6);  // Enough for "true" or "false"
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    if (value != 0) {
        strcpy(result, "true");
    } else {
        strcpy(result, "false");
    }
    return result;
}

int64_t runtime_str_contains(const char* haystack, const char* needle) {
    // Check if haystack contains needle substring
    // Returns 1 (true) if found, 0 (false) otherwise
    if (!haystack || !needle) return 0;
    return strstr(haystack, needle) != NULL ? 1 : 0;
}

char* runtime_str_strip(const char* str) {
    // Find start (skip leading whitespace)
    while (*str && isspace(*str)) str++;
    if (*str == '\0') {
        return strdup("");
    }

    // Find end (skip trailing whitespace)
    const char* end = str + strlen(str) - 1;
    while (end > str && isspace(*end)) end--;

    // Copy the stripped string
    size_t len = end - str + 1;
    char* result = malloc(len + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    memcpy(result, str, len);
    result[len] = '\0';
    return result;
}

RuntimeList* runtime_str_split(const char* str, const char* delim) {
    RuntimeList* list = runtime_list_new();
    char* str_copy = strdup(str);
    char* token = strtok(str_copy, delim);

    while (token != NULL) {
        // For now, store the pointer as an int64_t
        // In a full implementation, we'd have a proper list of strings
        runtime_list_append_int(list, (int64_t)strdup(token));
        token = strtok(NULL, delim);
    }

    free(str_copy);
    return list;
}

char* runtime_str_join(RuntimeList* list, const char* delim) {
    if (list->length == 0) {
        return strdup("");
    }

    // Calculate total length
    size_t total_len = 0;
    size_t delim_len = strlen(delim);
    for (int64_t i = 0; i < list->length; i++) {
        char* str = (char*)list->items[i];
        total_len += strlen(str);
        if (i < list->length - 1) {
            total_len += delim_len;
        }
    }

    // Build result string
    char* result = malloc(total_len + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }

    result[0] = '\0';
    for (int64_t i = 0; i < list->length; i++) {
        char* str = (char*)list->items[i];
        strcat(result, str);
        if (i < list->length - 1) {
            strcat(result, delim);
        }
    }

    return result;
}

char* runtime_str_replace(const char* str, const char* old, const char* new) {
    if (!old || !new || strlen(old) == 0) {
        return strdup(str);
    }

    // Count occurrences
    int count = 0;
    const char* p = str;
    size_t old_len = strlen(old);
    while ((p = strstr(p, old)) != NULL) {
        count++;
        p += old_len;
    }

    if (count == 0) {
        return strdup(str);
    }

    // Allocate result
    size_t new_len = strlen(new);
    size_t result_len = strlen(str) + count * (new_len - old_len);
    char* result = malloc(result_len + 1);
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }

    // Build result
    char* dst = result;
    const char* src = str;
    while ((p = strstr(src, old)) != NULL) {
        size_t len = p - src;
        memcpy(dst, src, len);
        dst += len;
        memcpy(dst, new, new_len);
        dst += new_len;
        src = p + old_len;
    }
    strcpy(dst, src);

    return result;
}

char* runtime_str_encode(const char* str) {
    // For now, just duplicate the string (UTF-8 is default)
    return strdup(str);
}

char* runtime_str_decode(const char* bytes) {
    // For now, just duplicate the string (UTF-8 is default)
    return strdup(bytes);
}

int64_t runtime_str_to_int(const char* str) {
    // Convert string to integer
    char* endptr;
    long long value = strtoll(str, &endptr, 10);

    // Check if conversion was successful (optional: could handle errors differently)
    if (str == endptr) {
        // Conversion failed - return 0
        return 0;
    }

    return (int64_t)value;
}

double runtime_str_to_float(const char* str) {
    // Convert string to float
    char* endptr;
    double value = strtod(str, &endptr);

    // Check if conversion was successful (optional: could handle errors differently)
    if (str == endptr) {
        // Conversion failed - return 0.0
        return 0.0;
    }

    return value;
}

// ============================================================================
// List Operations
// ============================================================================

RuntimeList* runtime_list_new() {
    RuntimeList* list = malloc(sizeof(RuntimeList));
    if (!list) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    list->capacity = 8;
    list->length = 0;
    list->elem_type = -1; // Unknown type initially
    list->items = malloc(list->capacity * sizeof(int64_t));
    if (!list->items) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    return list;
}

void runtime_list_append_int(RuntimeList* list, int64_t value) {
    if (list->length >= list->capacity) {
        list->capacity *= 2;
        list->items = realloc(list->items, list->capacity * sizeof(int64_t));
        if (!list->items) {
            fprintf(stderr, "Runtime error: out of memory\n");
            exit(1);
        }
    }
    list->items[list->length++] = value;
}

int64_t runtime_list_get_int(RuntimeList* list, int64_t index) {
    // Handle negative indices (Python-style)
    if (index < 0) {
        index = list->length + index;
    }

    if (index < 0 || index >= list->length) {
        fprintf(stderr, "Runtime error: list index out of bounds\n");
        exit(1);
    }
    return list->items[index];
}

// Helper function to convert int64 to string (simple implementation)
static void int64_to_str(int64_t value, char* buffer) {
    if (value == 0) {
        buffer[0] = '0';
        buffer[1] = '\0';
        return;
    }

    int is_negative = 0;
    if (value < 0) {
        is_negative = 1;
        value = -value;
    }

    char temp[32];
    int i = 0;
    while (value > 0) {
        temp[i++] = '0' + (value % 10);
        value /= 10;
    }

    int j = 0;
    if (is_negative) {
        buffer[j++] = '-';
    }
    while (i > 0) {
        buffer[j++] = temp[--i];
    }
    buffer[j] = '\0';
}

int64_t runtime_list_get_int_at(RuntimeList* list, int64_t index, int line) {
    // Validate list pointer
    if (!list) {
        runtime_error_at("Index error: null list pointer", line);
    }

    // Handle negative indices (Python-style)
    int64_t original_index = index;
    if (index < 0) {
        index = list->length + index;
    }

    if (index < 0 || index >= list->length) {
        // Manually construct error message without sprintf
        static char msg[512];
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

void runtime_list_set_int(RuntimeList* list, int64_t index, int64_t value) {
    // Handle negative indices (Python-style)
    if (index < 0) {
        index = list->length + index;
    }

    if (index < 0 || index >= list->length) {
        fprintf(stderr, "Runtime error: list index out of bounds\n");
        exit(1);
    }
    list->items[index] = value;
}

void runtime_list_set_int_at(RuntimeList* list, int64_t index, int64_t value, int line) {
    // Handle negative indices (Python-style)
    int64_t original_index = index;
    if (index < 0) {
        index = list->length + index;
    }

    if (index < 0 || index >= list->length) {
        // Manually construct error message without sprintf
        static char msg[512];
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

int64_t runtime_list_len(RuntimeList* list) {
    return list->length;
}

int64_t runtime_list_pop(RuntimeList* list) {
    if (list->length == 0) {
        fprintf(stderr, "Runtime error: pop from empty list\n");
        exit(1);
    }
    return list->items[--list->length];
}

RuntimeList* runtime_list_new_i64(int64_t* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    list->elem_type = 0; // Integer type
    for (int64_t i = 0; i < count; i++) {
        runtime_list_append_int(list, values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_f64(double* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    list->elem_type = 2; // Float type
    for (int64_t i = 0; i < count; i++) {
        // Store as int64_t (cast pointer)
        runtime_list_append_int(list, *(int64_t*)&values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_str(char** values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    list->elem_type = 1; // String type
    for (int64_t i = 0; i < count; i++) {
        runtime_list_append_int(list, (int64_t)values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_bool(bool* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    list->elem_type = 3; // Bool type
    for (int64_t i = 0; i < count; i++) {
        runtime_list_append_int(list, values[i] ? 1 : 0);
    }
    return list;
}

bool runtime_contains(RuntimeList* list, int64_t value) {
    for (int64_t i = 0; i < list->length; i++) {
        if (list->items[i] == value) {
            return true;
        }
    }
    return false;
}

void runtime_list_free(RuntimeList* list) {
    if (list) {
        free(list->items);
        free(list);
    }
}

// ============================================================================
// Set Operations
// ============================================================================

RuntimeSet* runtime_set_new() {
    RuntimeSet* set = malloc(sizeof(RuntimeSet));
    if (!set) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    set->capacity = 16;
    set->length = 0;
    set->elem_type = -1; // Unknown type initially
    set->items = malloc(sizeof(int64_t) * set->capacity);
    if (!set->items) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    return set;
}

void runtime_set_add(RuntimeSet* set, int64_t value) {
    // Detect type on first add
    if (set->elem_type == -1) {
        if (value > 0x100000) {
            set->elem_type = 1; // String type
        } else {
            set->elem_type = 0; // Integer type
        }
    }

    // Check if already exists
    for (int64_t i = 0; i < set->length; i++) {
        if (set->items[i] == value) {
            return;  // Already in set
        }
    }

    // Resize if needed
    if (set->length >= set->capacity) {
        set->capacity *= 2;
        set->items = realloc(set->items, sizeof(int64_t) * set->capacity);
        if (!set->items) {
            fprintf(stderr, "Runtime error: out of memory\n");
            exit(1);
        }
    }

    set->items[set->length++] = value;
}

void runtime_set_add_typed(RuntimeSet* set, int64_t value, int elem_type) {
    // Set the element type if not already set
    if (set->elem_type == -1) {
        set->elem_type = elem_type;
    }

    // Check if already exists
    for (int64_t i = 0; i < set->length; i++) {
        if (set->items[i] == value) {
            return;  // Already in set
        }
    }

    // Resize if needed
    if (set->length >= set->capacity) {
        set->capacity *= 2;
        set->items = realloc(set->items, sizeof(int64_t) * set->capacity);
        if (!set->items) {
            fprintf(stderr, "Runtime error: out of memory\n");
            exit(1);
        }
    }

    set->items[set->length++] = value;
}

void runtime_set_remove(RuntimeSet* set, int64_t value) {
    for (int64_t i = 0; i < set->length; i++) {
        if (set->items[i] == value) {
            // Shift remaining elements
            for (int64_t j = i; j < set->length - 1; j++) {
                set->items[j] = set->items[j + 1];
            }
            set->length--;
            return;
        }
    }
}

bool runtime_set_contains(RuntimeSet* set, int64_t value) {
    for (int64_t i = 0; i < set->length; i++) {
        if (set->items[i] == value) {
            return true;
        }
    }
    return false;
}

int64_t runtime_set_len(RuntimeSet* set) {
    return set->length;
}

void runtime_set_free(RuntimeSet* set) {
    if (set) {
        free(set->items);
        free(set);
    }
}

// ============================================================================
// Math Operations
// ============================================================================

int64_t runtime_abs_int(int64_t value) {
    return value < 0 ? -value : value;
}

double runtime_abs_float(double value) {
    return fabs(value);
}

double runtime_pow(double base, double exp) {
    return pow(base, exp);
}

double runtime_sqrt(double value) {
    return sqrt(value);
}

double runtime_floor(double value) {
    return floor(value);
}

double runtime_ceil(double value) {
    return ceil(value);
}

// ============================================================================
// Python Interop (Stubs for now)
// ============================================================================

struct RuntimePyObject {
    void* ptr;  // Placeholder
};

RuntimePyObject* runtime_py_import(const char* module_name) {
    fprintf(stderr, "Runtime error: Python interop not yet implemented\n");
    exit(1);
    return NULL;
}

int64_t runtime_py_call_int(RuntimePyObject* module, const char* func_name,
                             int argc, int64_t* args) {
    fprintf(stderr, "Runtime error: Python interop not yet implemented\n");
    exit(1);
    return 0;
}

RuntimePyObject* runtime_py_getattr(RuntimePyObject* obj, const char* attr_name) {
    fprintf(stderr, "Runtime error: Python interop not yet implemented\n");
    exit(1);
    return NULL;
}

// ============================================================================
// Additional Math Operations
// ============================================================================

int64_t runtime_min_int(int64_t a, int64_t b) {
    return (a < b) ? a : b;
}

int64_t runtime_max_int(int64_t a, int64_t b) {
    return (a > b) ? a : b;
}

double runtime_min_float(double a, double b) {
    return (a < b) ? a : b;
}

double runtime_max_float(double a, double b) {
    return (a > b) ? a : b;
}

double runtime_sin(double x) {
    return sin(x);
}

double runtime_cos(double x) {
    return cos(x);
}

double runtime_tan(double x) {
    return tan(x);
}

double runtime_round(double x) {
    return round(x);
}

// ============================================================================
// Builtin Functions
// ============================================================================

void runtime_exit(int64_t status) {
    exit((int)status);
}

void runtime_sleep(double seconds) {
    // Use nanosleep for sub-second precision
    #ifdef _WIN32
        Sleep((DWORD)(seconds * 1000));
    #else
        #include <unistd.h>
        #include <time.h>
        struct timespec ts;
        ts.tv_sec = (time_t)seconds;
        ts.tv_nsec = (long)((seconds - ts.tv_sec) * 1e9);
        nanosleep(&ts, NULL);
    #endif
}

void runtime_assert(bool condition, const char* message) {
    if (!condition) {
        if (message && message[0] != '\0') {
            // If message is provided, just print it
            printf("%s\n", message);
        } else {
            // If no message, print default message to stderr
            fprintf(stderr, "Assertion failed\n");
        }
        exit(1);
    }
}

// ============================================================================
// Exception Handling
// ============================================================================

#define MAX_EXCEPTION_HANDLERS 256

static RuntimeExceptionHandler exception_handlers[MAX_EXCEPTION_HANDLERS];
static int exception_handler_count = 0;

void runtime_exception_init() {
    exception_handler_count = 0;
}

int runtime_exception_push(const char* exc_type) {
    if (exception_handler_count >= MAX_EXCEPTION_HANDLERS) {
        fprintf(stderr, "Error: Maximum exception handler depth exceeded\n");
        exit(1);
    }

    RuntimeExceptionHandler* handler = &exception_handlers[exception_handler_count];
    handler->exc_type = exc_type;

    return exception_handler_count++;
}

jmp_buf* runtime_exception_get_jump_buffer() {
    if (exception_handler_count == 0) {
        return NULL;
    }
    return &exception_handlers[exception_handler_count - 1].jump_buffer;
}

void runtime_exception_pop() {
    if (exception_handler_count > 0) {
        exception_handler_count--;
    }
}

// Functions that call longjmp must be compiled with reduced optimizations
// to prevent issues with register allocation and variable caching.
// We use -fno-omit-frame-pointer and disable inline optimizations.
__attribute__((optimize("no-omit-frame-pointer")))
__attribute__((noinline))
void runtime_exception_raise(const char* exc_type, const char* message) {
    // Search for matching exception handler (from most recent to oldest)
    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];

        // Check if handler matches exception type (empty string matches all)
        if (strcmp(handler->exc_type, "") == 0 || strcmp(handler->exc_type, exc_type) == 0) {
            // Perform non-local jump to handler
            // The longjmp will return to the setjmp location with value 1
            // The handler's TRY_END will pop this handler from the stack
            longjmp(handler->jump_buffer, 1);
        }
    }

    // No handler found - print error and exit
    fprintf(stderr, "Uncaught exception: [%s] %s\n", exc_type, message);
    exit(1);
}

__attribute__((optimize("no-omit-frame-pointer")))
__attribute__((noinline))
void runtime_exception_raise_at(const char* exc_type, const char* message, int line) {
    // Search for matching exception handler (from most recent to oldest)
    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];

        // Check if handler matches exception type (empty string matches all)
        if (strcmp(handler->exc_type, "") == 0 || strcmp(handler->exc_type, exc_type) == 0) {
            // Perform non-local jump to handler
            longjmp(handler->jump_buffer, 1);
        }
    }

    // No handler found - print error with dual format support
    if (is_test_mode()) {
        // Test mode: concise format ?line,column:[Type] message
        fprintf(stderr, "?%d,0:[%s] %s\n", line, exc_type, message);
    } else {
        // User mode: detailed format similar to Python runtime
        fprintf(stderr, "Exception: %s\n", exc_type);

        if (runtime_source_file && runtime_source_lines && line > 0 && line <= runtime_source_line_count) {
            // Print file location and source line (no caret for raise statements)
            const char* source_line = runtime_source_lines[line - 1];

            fprintf(stderr, "  File \"%s\" line %d in main\n", runtime_source_file, line);
            fprintf(stderr, "      %s\n", source_line);
            fprintf(stderr, "\n");  // Blank line instead of caret
            fprintf(stderr, "    %s:%d: %s\n", runtime_source_file, line, message);
        } else {
            // No source info available - still show proper format
            fprintf(stderr, "  File \"<unknown>\" line %d in main\n", line);
            fprintf(stderr, "    <unknown>:%d: %s\n", line, message);
        }
    }

    exit(1);
}

__attribute__((optimize("no-omit-frame-pointer")))
__attribute__((noinline))
void runtime_error_at(const char* message, int line) {
    // Search for matching exception handler using "RuntimeError" as type
    for (int i = exception_handler_count - 1; i >= 0; i--) {
        RuntimeExceptionHandler* handler = &exception_handlers[i];

        // Extract exception type from message if present (e.g., "ZeroDivisionError")
        // For runtime errors, we need to match against handler's expected type
        // Default to RuntimeError if no type in message
        const char* exc_type = "RuntimeError";

        // Check if message contains exception type (for division by zero, etc.)
        if (strstr(message, "division by zero")) {
            exc_type = "ZeroDivisionError";
        }

        if (strcmp(handler->exc_type, "") == 0 || strcmp(handler->exc_type, exc_type) == 0) {
            longjmp(handler->jump_buffer, 1);
        }
    }

    // No handler found - print error and exit
    if (is_test_mode()) {
        // Test mode: concise format ?line,column:message
        fprintf(stderr, "?%d,0:%s\n", line, message);
    } else {
        // User mode: detailed format similar to Python runtime
        fprintf(stderr, "Exception: Runtime Error\n");

        if (runtime_source_file && runtime_source_lines && line > 0 && line <= runtime_source_line_count) {
            // Print file location and source line
            const char* source_line = runtime_source_lines[line - 1];

            // Try to find a reasonable column position based on the error message
            int col = 0;

            // For index errors, try to find the '[' bracket and point to the index value
            if (strstr(message, "Index error")) {
                const char* bracket = strchr(source_line, '[');
                if (bracket) {
                    // Find the closing bracket
                    const char* close_bracket = strchr(bracket, ']');
                    if (close_bracket) {
                        // Point just before the closing bracket (at the last character of the index)
                        col = close_bracket - source_line - 1;
                    } else {
                        // No closing bracket, point at the opening bracket
                        col = bracket - source_line;
                    }
                } else {
                    // Fallback to end of line
                    col = strlen(source_line);
                }
            } else {
                // For other errors, position at end of line
                col = strlen(source_line);
            }

            fprintf(stderr, "  File \"%s\" line %d in main\n", runtime_source_file, line);
            fprintf(stderr, "      %s\n", source_line);
            fprintf(stderr, "      %*s^\n", col, "");  // Print spaces then ^
            fprintf(stderr, "    %s:%d:%d: %s\n", runtime_source_file, line, col, message);
        } else {
            // No source info available - still show proper format
            // Use "unknown" as filename and "0" as column
            fprintf(stderr, "  File \"<unknown>\" line %d in main\n", line);
            fprintf(stderr, "    <unknown>:%d:0: %s\n", line, message);
        }
    }

    exit(1);
}

void runtime_check_div_zero_i64(int64_t divisor) {
    if (divisor == 0) {
        runtime_exception_raise("ZeroDivisionError", "integer division by zero");
    }
}

void runtime_check_div_zero_i64_at(int64_t divisor, int line) {
    if (divisor == 0) {
        runtime_error_at("integer division by zero", line);
    }
}

void runtime_check_div_zero_f64(double divisor) {
    if (divisor == 0.0) {
        runtime_exception_raise("ZeroDivisionError", "float division by zero");
    }
}

void runtime_check_div_zero_f64_at(double divisor, int line) {
    if (divisor == 0.0) {
        runtime_error_at("float division by zero", line);
    }
}

// ============================================================================
// Memory Management
// ============================================================================

void runtime_init() {
    // Initialize any global state here
    runtime_exception_init();
}

void runtime_cleanup() {
    // Cleanup any global state here
}

// ============================================================================
// String Conversion for Complex Types
// ============================================================================

char* runtime_list_to_str(RuntimeList* list) {
    return runtime_list_repr(list);
}

char* runtime_set_to_str(RuntimeSet* set) {
    return runtime_set_repr(set);
}

// ============================================================================
// List and Set String Representations
// ============================================================================

char* runtime_list_repr(RuntimeList* list) {
    if (!list) return strdup("[]");

    // Add compiler barrier to prevent aggressive optimization of list pointer
    __asm__ __volatile__("" : : "r"(list) : "memory");

    // Validate list structure before accessing
    if (!list->items && list->length > 0) {
        fprintf(stderr, "Runtime error: corrupted list structure (items=NULL, length=%ld)\n", list->length);
        return strdup("[corrupted]");
    }

    char* result = malloc(4096);
    if (!result) return NULL;

    strcpy(result, "[");
    for (int64_t i = 0; i < list->length; i++) {
        if (i > 0) strcat(result, ", ");

        // Use type information to format correctly
        if (list->elem_type == 1) {
            // String type
            const char* str = (const char*)list->items[i];
            strcat(result, str);
        } else if (list->elem_type == 2) {
            // Float type - use union for type-safe punning
            union { int64_t i; double d; } pun;
            pun.i = list->items[i];
            char tmp[32];
            snprintf(tmp, 32, "%g", pun.d);
            strcat(result, tmp);
        } else {
            // Integer type (or unknown)
            char tmp[32];
            snprintf(tmp, 32, "%ld", list->items[i]);
            strcat(result, tmp);
        }
    }
    strcat(result, "]");
    return result;
}

char* runtime_set_repr(RuntimeSet* set) {
    char* result = malloc(4096);
    if (!result) return NULL;

    strcpy(result, "{");
    for (int64_t i = 0; i < set->length; i++) {
        if (i > 0) strcat(result, ", ");

        // Use type information to format correctly
        if (set->elem_type == 1) {
            // String type
            const char* str = (const char*)set->items[i];
            strcat(result, str);
        } else {
            // Integer type (or unknown)
            char tmp[32];
            snprintf(tmp, 32, "%ld", set->items[i]);
            strcat(result, tmp);
        }
    }
    strcat(result, "}");
    return result;
}

// ============================================================================
// Process Management
// ============================================================================

int64_t runtime_fork() {
    pid_t pid = fork();
    if (pid == -1) {
        fprintf(stderr, "Runtime error: fork failed\n");
        exit(1);
    }
    return (int64_t)pid;
}

int64_t runtime_wait(int64_t pid) {
    int status;
    pid_t result = waitpid((pid_t)pid, &status, 0);
    if (result == -1) {
        fprintf(stderr, "Runtime error: waitpid failed\n");
        exit(1);
    }
    // Return the exit status
    // Extract the actual exit code (bits 8-15)
    if (WIFEXITED(status)) {
        return (int64_t)WEXITSTATUS(status);
    }
    return status;
}

// ============================================================================
// File I/O Operations
// ============================================================================

// File descriptor mapping - store FILE* pointers as int64_t "handles"
// Using a simple hash table approach with 256 slots
#define MAX_FDS 256
static FILE* fd_table[MAX_FDS] = {0};
static int fd_counter = 0;

int64_t runtime_fopen(const char* path, const char* mode) {
    if (fd_counter >= MAX_FDS) {
        fprintf(stderr, "Runtime error: too many open files\n");
        return -1;
    }
    FILE* fp = fopen(path, mode);
    if (!fp) {
        fprintf(stderr, "Runtime error: failed to open file %s\n", path);
        return -1;
    }
    int64_t handle = (int64_t)fp;
    fd_table[fd_counter++] = fp;
    return handle;
}

int64_t runtime_fwrite(int64_t fd, const char* data) {
    FILE* fp = (FILE*)fd;
    if (!fp) {
        fprintf(stderr, "Runtime error: invalid file descriptor\n");
        return 0;
    }
    size_t len = strlen(data);
    size_t written = fwrite(data, 1, len, fp);
    fflush(fp);
    return (int64_t)written;
}

char* runtime_fread(int64_t fd, int64_t size) {
    FILE* fp = (FILE*)fd;
    if (!fp) {
        fprintf(stderr, "Runtime error: invalid file descriptor\n");
        return "";
    }

    // If size is -1, read entire file
    if (size == -1) {
        // Get file size
        long current_pos = ftell(fp);
        fseek(fp, 0, SEEK_END);
        long file_size = ftell(fp);
        fseek(fp, current_pos, SEEK_SET);

        // Allocate buffer for entire file
        char* buffer = malloc(file_size + 1);
        if (!buffer) {
            fprintf(stderr, "Runtime error: out of memory\n");
            return "";
        }

        size_t read = fread(buffer, 1, file_size, fp);
        buffer[read] = '\0';
        return buffer;
    }

    char* buffer = malloc(size + 1);
    if (!buffer) {
        fprintf(stderr, "Runtime error: out of memory\n");
        return "";
    }
    size_t read = fread(buffer, 1, size, fp);
    buffer[read] = '\0';
    return buffer;
}

void runtime_fclose(int64_t fd) {
    FILE* fp = (FILE*)fd;
    if (fp) {
        fclose(fp);
        // Remove from fd_table (simple linear search)
        for (int i = 0; i < fd_counter; i++) {
            if (fd_table[i] == fp) {
                fd_table[i] = NULL;
                break;
            }
        }
    }
}


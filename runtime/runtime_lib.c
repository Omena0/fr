/*
 * Runtime Library Implementation for fr x86_64 Compiled Code
 */

#include "runtime_lib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

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
    snprintf(result, 32, "%ld", value);
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
    if (index < 0 || index >= list->length) {
        fprintf(stderr, "Runtime error: list index out of bounds\n");
        exit(1);
    }
    return list->items[index];
}

void runtime_list_set_int(RuntimeList* list, int64_t index, int64_t value) {
    if (index < 0 || index >= list->length) {
        fprintf(stderr, "Runtime error: list index out of bounds\n");
        exit(1);
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
    for (int64_t i = 0; i < count; i++) {
        runtime_list_append_int(list, values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_f64(double* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    for (int64_t i = 0; i < count; i++) {
        // Store as int64_t (cast pointer)
        runtime_list_append_int(list, *(int64_t*)&values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_str(char** values, int64_t count) {
    RuntimeList* list = runtime_list_new();
    for (int64_t i = 0; i < count; i++) {
        runtime_list_append_int(list, (int64_t)values[i]);
    }
    return list;
}

RuntimeList* runtime_list_new_bool(bool* values, int64_t count) {
    RuntimeList* list = runtime_list_new();
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
    set->items = malloc(sizeof(int64_t) * set->capacity);
    if (!set->items) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    return set;
}

void runtime_set_add(RuntimeSet* set, int64_t value) {
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
// Memory Management
// ============================================================================

void runtime_init() {
    // Initialize any global state here
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
    char* result = malloc(4096);
    if (!result) return NULL;
    
    strcpy(result, "[");
    for (int64_t i = 0; i < list->length; i++) {
        if (i > 0) strcat(result, ", ");
        char tmp[32];
        snprintf(tmp, 32, "%ld", list->items[i]);
        strcat(result, tmp);
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
        char tmp[32];
        snprintf(tmp, 32, "%ld", set->items[i]);
        strcat(result, tmp);
    }
    strcat(result, "}");
    return result;
}

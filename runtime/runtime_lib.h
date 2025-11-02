/*
 * Runtime Library for fr x86_64 Compiled Code
 * 
 * Provides C functions for complex operations that are difficult to implement
 * directly in assembly (lists, strings, Python interop, file I/O, etc.)
 */

#ifndef FR_RUNTIME_LIB_H
#define FR_RUNTIME_LIB_H

#include <stdint.h>
#include <stdbool.h>

// Forward declarations
typedef struct RuntimePyObject RuntimePyObject;

// Data structure definitions
struct RuntimeList {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type; // 0=int, 1=string, 2=other
};
typedef struct RuntimeList RuntimeList;

struct RuntimeSet {
    int64_t* items;
    int64_t length;
    int64_t capacity;
    int elem_type; // 0=int, 1=string, 2=other
};
typedef struct RuntimeSet RuntimeSet;

// ============================================================================
// Basic I/O
// ============================================================================

/**
 * Print an integer value to stdout (no newline)
 */
void runtime_print_int(int64_t value);

/**
 * Print an integer value to stdout with newline
 */
void runtime_println_int(int64_t value);

/**
 * Print a float value to stdout (no newline)
 */
void runtime_print_float(double value);

/**
 * Print a float value to stdout with newline
 */
void runtime_println_float(double value);

/**
 * Print a string to stdout (no newline)
 */
void runtime_print_str(const char* str);

/**
 * Print a string to stdout with newline
 */
void runtime_println_str(const char* str);

/**
 * Generic print function (for now, just prints int)
 */
void runtime_print(int64_t value);

/**
 * Generic println function (for now, just prints int)
 */
void runtime_println(int64_t value);

// ============================================================================
// String Operations
// ============================================================================

/**
 * Concatenate two strings
 * Returns newly allocated string (caller must free)
 */
char* runtime_str_concat(const char* a, const char* b);

/**
 * Get string length
 */
int64_t runtime_str_len(const char* str);

/**
 * Get character at index as a string
 * Returns newly allocated string
 */
char* runtime_str_get_char(const char* str, int64_t index);

/**
 * Convert string to uppercase
 * Returns newly allocated string
 */
char* runtime_str_upper(const char* str);

/**
 * Convert string to lowercase
 * Returns newly allocated string
 */
char* runtime_str_lower(const char* str);

/**
 * Convert integer to string
 * Returns newly allocated string
 */
char* runtime_int_to_str(int64_t value);

/**
 * Convert float to string
 * Returns newly allocated string
 */
char* runtime_float_to_str(double value);

/**
 * Convert boolean to string ("true" or "false")
 * Returns newly allocated string
 */
char* runtime_bool_to_str(int64_t value);

/**
 * Check if string contains substring
 * Returns 1 (true) if found, 0 (false) if not found
 */
int64_t runtime_str_contains(const char* haystack, const char* needle);

/**
 * Strip whitespace from both ends of string
 * Returns newly allocated string
 */
char* runtime_str_strip(const char* str);

/**
 * Split string by delimiter
 * Returns newly allocated RuntimeList of strings
 */
RuntimeList* runtime_str_split(const char* str, const char* delim);

/**
 * Join list of strings with delimiter
 * Returns newly allocated string
 */
char* runtime_str_join(RuntimeList* list, const char* delim);

/**
 * Replace all occurrences of old with new in string
 * Returns newly allocated string
 */
char* runtime_str_replace(const char* str, const char* old, const char* new);

/**
 * Encode string to bytes (UTF-8)
 * Returns newly allocated string (for now, just copies)
 */
char* runtime_str_encode(const char* str);

/**
 * Decode bytes to string (UTF-8)
 * Returns newly allocated string (for now, just copies)
 */
char* runtime_str_decode(const char* bytes);

/**
 * Convert string to integer
 * Returns 0 if conversion fails
 */
int64_t runtime_str_to_int(const char* str);

/**
 * Convert string to float
 * Returns 0.0 if conversion fails
 */
double runtime_str_to_float(const char* str);

// ============================================================================
// List Operations
// ============================================================================

/**
 * Create a new empty list
 */
RuntimeList* runtime_list_new();

/**
 * Append an integer to a list
 */
void runtime_list_append_int(RuntimeList* list, int64_t value);

/**
 * Get integer at index from list
 */
int64_t runtime_list_get_int(RuntimeList* list, int64_t index);
int64_t runtime_list_get_int_at(RuntimeList* list, int64_t index, int line);

/**
 * Set integer at index in list
 */
void runtime_list_set_int(RuntimeList* list, int64_t index, int64_t value);
void runtime_list_set_int_at(RuntimeList* list, int64_t index, int64_t value, int line);

/**
 * Get list length
 */
int64_t runtime_list_len(RuntimeList* list);

/**
 * Pop and return last element from list
 */
int64_t runtime_list_pop(RuntimeList* list);

/**
 * Create list from array of int64_t values
 */
RuntimeList* runtime_list_new_i64(int64_t* values, int64_t count);

/**
 * Create list from array of double values
 */
RuntimeList* runtime_list_new_f64(double* values, int64_t count);

/**
 * Create list from array of string pointers
 */
RuntimeList* runtime_list_new_str(char** values, int64_t count);

/**
 * Create list from array of bool values
 */
RuntimeList* runtime_list_new_bool(bool* values, int64_t count);

/**
 * Check if list contains value
 */
bool runtime_contains(RuntimeList* list, int64_t value);

/**
 * Free a list
 */
void runtime_list_free(RuntimeList* list);

// ============================================================================
// Set Operations
// ============================================================================

/**
 * Create a new empty set
 */
RuntimeSet* runtime_set_new();

/**
 * Add value to set
 */
void runtime_set_add(RuntimeSet* set, int64_t value);

/**
 * Add value to set with explicit type information
 * elem_type: 0=int, 1=string
 */
void runtime_set_add_typed(RuntimeSet* set, int64_t value, int elem_type);

/**
 * Remove value from set
 */
void runtime_set_remove(RuntimeSet* set, int64_t value);

/**
 * Check if set contains value
 */
bool runtime_set_contains(RuntimeSet* set, int64_t value);

/**
 * Get set size
 */
int64_t runtime_set_len(RuntimeSet* set);

/**
 * Free a set
 */
void runtime_set_free(RuntimeSet* set);

// ============================================================================
// Math Operations
// ============================================================================

/**
 * Compute absolute value
 */
int64_t runtime_abs_int(int64_t value);

/**
 * Compute absolute value (float)
 */
double runtime_abs_float(double value);

/**
 * Compute power
 */
double runtime_pow(double base, double exp);

/**
 * Compute square root
 */
double runtime_sqrt(double value);

/**
 * Compute floor
 */
double runtime_floor(double value);

/**
 * Compute ceil
 */
double runtime_ceil(double value);

// ============================================================================
// Python Interop (Stubs for now)
// ============================================================================

/**
 * Import a Python module
 */
RuntimePyObject* runtime_py_import(const char* module_name);

/**
 * Call a Python function with integer arguments
 */
int64_t runtime_py_call_int(RuntimePyObject* module, const char* func_name, 
                             int argc, int64_t* args);

/**
 * Get attribute from Python object
 */
RuntimePyObject* runtime_py_getattr(RuntimePyObject* obj, const char* attr_name);

// ============================================================================
// Additional Math Operations
// ============================================================================

/**
 * Minimum of two integers
 */
int64_t runtime_min_int(int64_t a, int64_t b);

/**
 * Maximum of two integers
 */
int64_t runtime_max_int(int64_t a, int64_t b);

/**
 * Minimum of two floats
 */
double runtime_min_float(double a, double b);

/**
 * Maximum of two floats
 */
double runtime_max_float(double a, double b);

/**
 * Sine function (via libm)
 */
double runtime_sin(double x);

/**
 * Cosine function (via libm)
 */
double runtime_cos(double x);

/**
 * Tangent function (via libm)
 */
double runtime_tan(double x);

/**
 * Round to nearest integer (via libm)
 */
double runtime_round(double x);

// ============================================================================
// Builtin Functions
// ============================================================================

/**
 * Exit the program with status code
 */
void runtime_exit(int64_t status);

/**
 * Sleep for specified seconds (accepts float)
 */
void runtime_sleep(double seconds);

/**
 * Assert a condition is true, exit if false
 */
void runtime_assert(bool condition, const char* message);

// ============================================================================
// String Formatting and Type Conversion
// ============================================================================

/**
 * Convert list to string representation
 */
char* runtime_list_to_str(RuntimeList* list);

/**
 * Convert set to string representation
 */
char* runtime_set_to_str(RuntimeSet* set);

/**
 * Get string representation of list
 */
char* runtime_list_repr(RuntimeList* list);

/**
 * Get string representation of set
 */
char* runtime_set_repr(RuntimeSet* set);

// ============================================================================
// Process Management
// ============================================================================

/**
 * Fork the current process
 * Returns the process ID (pid) of the child process in parent,
 * and 0 in the child process
 */
int64_t runtime_fork();

/**
 * Wait for a child process to terminate
 * Takes the process ID returned by fork()
 * Returns the exit status of the child process
 */
int64_t runtime_wait(int64_t pid);

// ============================================================================
// File I/O Operations
// ============================================================================

/**
 * Open a file for reading or writing
 * mode: "r" for read, "w" for write, "a" for append
 * Returns a file handle (int64_t)
 */
int64_t runtime_fopen(const char* path, const char* mode);

/**
 * Write data to an open file
 * Returns number of bytes written
 */
int64_t runtime_fwrite(int64_t fd, const char* data);

/**
 * Read data from an open file
 * Returns a string containing the read data
 */
char* runtime_fread(int64_t fd, int64_t size);

/**
 * Close an open file
 */
void runtime_fclose(int64_t fd);

// ============================================================================
// Exception Handling
// ============================================================================

#include <setjmp.h>

typedef struct {
    const char* exc_type;
    jmp_buf jump_buffer;      // Jump buffer for non-local jump
} RuntimeExceptionHandler;

/**
 * Initialize exception handler stack
 */
void runtime_exception_init();

/**
 * Push an exception handler onto the stack
 * Returns the handler index
 */
int runtime_exception_push(const char* exc_type);

/**
 * Get the jump buffer for the most recent exception handler
 * Returns NULL if no handlers on stack
 */
jmp_buf* runtime_exception_get_jump_buffer();

/**
 * Pop an exception handler from the stack
 */
void runtime_exception_pop();

/**
 * Raise an exception
 * If a matching handler is found, performs a non-local jump to it using longjmp
 * Otherwise, prints error and exits
 * This function never returns if a handler is found
 */
void runtime_exception_raise(const char* exc_type, const char* message) __attribute__((noreturn));

/**
 * Raise an exception with line number information
 * If a matching handler is found, performs a non-local jump to it using longjmp
 * Otherwise, prints error with line number and exits
 * This function never returns if a handler is found
 */
void runtime_exception_raise_at(const char* exc_type, const char* message, int line) __attribute__((noreturn));

/**
 * Report a runtime error with line,column format
 * Used for division by zero, index errors, etc.
 * Output format: ?line,column:message
 */
void runtime_error_at(const char* message, int line) __attribute__((noreturn));

/**
 * Set source file information for error reporting
 * This should be called once at program startup
 */
void runtime_set_source_info(const char* filename, const char* source);

/**
 * Check if division by zero would occur for integers
 */
void runtime_check_div_zero_i64(int64_t divisor);

/**
 * Check if division by zero would occur for integers with line info
 */
void runtime_check_div_zero_i64_at(int64_t divisor, int line);

/**
 * Check if division by zero would occur for floats
 */
void runtime_check_div_zero_f64(double divisor);

/**
 * Check if division by zero would occur for floats with line info
 */
void runtime_check_div_zero_f64_at(double divisor, int line);

// ============================================================================
// Memory Management
// ============================================================================

/**
 * Initialize runtime library
 */
void runtime_init();

/**
 * Cleanup runtime library
 */
void runtime_cleanup();

#endif /* FR_RUNTIME_LIB_H */

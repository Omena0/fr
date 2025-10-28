/*
 * Runtime Library Implementation for fr x86_64 Compiled Code
 */
// ============================================================================
// Basic I/O
// ============================================================================

#include "runtime_lib.h"
#include <stdio.h>
#include <stdlib.h>

char* runtime_int_to_str(int64_t value) {
    char* result = malloc(32);  // Enough for any int64
    if (!result) {
        fprintf(stderr, "Runtime error: out of memory\n");
        exit(1);
    }
    snprintf(result, 32, "%ld", value);
    return result;
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


void runtime_println_int(int64_t value) {
    printf("%ld\n", value);
}


void runtime_println_str(const char* str) {
    printf("%s\n", str);
}


double runtime_round(double x) {
    return round(x);
}


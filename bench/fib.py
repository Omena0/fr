import sys
sys.set_int_max_str_digits(1000000000)

def fibonacci(n: int):
    if n <= 1:
        return n

    a = 0
    b = 1
    c = 1
    for _ in range(n):
        c = a + b
        a = b
        b = c

    return b

print(fibonacci(1000000))

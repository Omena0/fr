
def fibonacci(n: int):
    if n <= 1:
        return n

    a = 0
    b = 1
    c = 1
    for _ in range(n):
        c = (a + b) % 1000000
        a = b
        b = c

    return b

print(fibonacci(1000000000))

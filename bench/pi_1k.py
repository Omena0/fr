
def pi_spigot(n_digits: int) -> str:
    n = int((10 * n_digits) // 3 + 1)
    a = [2 for _ in range(n)]
    result = ""
    nines = 0
    predigit = 1

    for i in range(n_digits):
        carry = 0
        k = n - 1

        # Main inner loop
        while k >= 1:
            x = a[k] * 10 + carry * k
            denom = 2 * k - 1
            a[k] = x % denom
            carry = x // denom
            k -= 1

        x = a[0] * 10 + carry
        q = x // 10
        a[0] = x % 10

        if i < 2:
            continue

        # Handle carries and 9-runs properly
        if q == 10:
            result += str(predigit + 1)
            for _ in range(nines):
                result += "0"
            predigit = 0
            nines = 0
        elif q == 9:
            nines += 1
        else:
            result += str(predigit)
            predigit = q
            if nines > 0:
                for _ in range(nines):
                    result += "9"
                nines = 0

    # Append last pending digit
    result += str(predigit)

    # Add the leading "3."
    return f"3.{result}"


def main():
    pi = pi_spigot(1000)
    print(pi)

if __name__ == "__main__":
    main()

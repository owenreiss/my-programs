def primes_to(arg_max: int):
    if arg_max <= 1:
        return
    if arg_max == 2:
        return 2,
    primes = [2]
    for num in range(3, arg_max + 1, 2):
        if not (num - 1) % 1_000_000:
            print(num, end="\r")
        is_prime = True
        for prime in primes:
            if prime > num ** 0.5:
                break
            if num % prime == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def twin_primes_to(arg_max: int):
    if arg_max <= 4:
        return
    primes = primes_to(arg_max)[2:]
    prev_prime = 3
    twin_primes = []
    for prime in primes:
        if prime == prev_prime + 2:
            twin_primes.append((prev_prime, prime))
        prev_prime = prime
    return twin_primes

# a = 1_000_000_000
# with open("primes_to_1,000,000,000.txt", "w") as handle:
#     handle.write("".join(str(x) + "\n" for x in primes_to(a)))

print(len(primes_to(50_000_000)))
from math import sqrt


def squared_primes(maximum):
    primes = []

    for number in range(2, maximum):
        primes.append(number ** 2)

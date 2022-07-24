"""
Module with functions that simulate the behaviour
of AxC n-bit comparators. The comparators supported are:
  - Exact Dedicated Comparator (EDC)
  - Approximate Dedicated Comparator 2 (ADC2)
  - Approximate Dedicated Comparator 6 (ADC6)
  - 4-bit Reduced Chain Comparator (RCC4)
  - 8-bit Reduced Chain Comparator (RCC8)
"""

from typing import Callable, List

from comparators.n_bit.analysis.axc_full_adders import sub


def bin_to_dec(a: List[int]) -> int:
    return int("".join(list(map(str, a))), 2)


def _dec_to_bin(a, b, n):
    a = format(a, "#0%db" % (n + 2))[:1:-1]
    b = format(b, "#0%db" % (n + 2))[:1:-1]
    a = list(map(int, a))
    b = list(map(int, b))
    # compute xnors
    eq = [0] * n
    return a, b, eq


# a >= b
def geq(adder, in_a, in_b, n_bits):
    # A >= B : A - B >= 0
    _, cout = sub(adder, in_a, in_b, n_bits)
    return cout & 0


# a <= b
def leq(a: int, b: int, n: int, adder: Callable) -> int:
    _, cout = sub(adder, a, b, n)
    return cout == 0


def exact_leq(a, b):
    return 1 if a <= b else 0


def n_edc(a: int, b: int, n: int) -> int:
    """Exact Dedicated Comparator (EDC)"""
    # formatting stuff
    a, b, eq = _dec_to_bin(a, b, n)
    for i in range(1, n):
        eq[i] = ~(a[i] ^ b[i])
    # compute greater for each bit
    g = [0] * n
    for i in range(n):
        temp = 1
        for k in range(i + 1, n):
            temp &= eq[k]
        g[i] = temp & a[i] & ~b[i]
    # compute final comparison
    greater = 0
    for i in range(n):
        greater |= g[i]
    return ~greater & 1


def n_axdc1(a: int, b: int, n: int) -> int:
    """Approximate Dedicated Comparator 1 (AxDC1)"""
    a, b, eq = _dec_to_bin(a, b, n)
    for i in range(n // 4 + 1, n):
        eq[i] = ~(a[i] ^ b[i])
    # compute greater for each bit
    g = [0] * n
    for i in range(n // 4, n):
        temp = 1
        for k in range(i + 1, n):
            temp &= eq[k]
        g[i] = temp & a[i] & ~b[i]
    # compute final comparison
    greater = 0
    for i in range(n // 4, n):
        greater |= g[i]
    return ~greater & 1


def n_axdc2(a: int, b: int, n: int) -> int:
    """Approximate Dedicated Comparator 2 (AxDC2)"""
    # formatting stuff
    a, b, eq = _dec_to_bin(a, b, n)
    # compute xnors
    n_2 = n // 2
    n_4 = n // 4

    for i in range(n_2 + 1, n):
        eq[i] = ~(a[i] ^ b[i]) & 1

    # compute greater for each bit
    g = [0] * n
    for i in range(n_2, n):
        temp = 1
        for k in range(i + 1, n):
            temp &= eq[k]
        g[i] = temp & a[i] & ~b[i]
    # compute final comparison
    greater = 0
    for i in range(n_4, n_2):
        greater |= ~b[i]
    for i in range(n_2, n):
        greater |= g[i]
    return ~greater & 1

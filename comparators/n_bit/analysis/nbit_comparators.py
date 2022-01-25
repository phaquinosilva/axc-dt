"""
Module with functions that simulate the behaviour
of AxC n-bit comparators. The comparators supported are:
  - Exact Dedicated Comparator (EDC)
  - Approximate Dedicated Comparator 2 (ADC2)
  - Approximate Dedicated Comparator 6 (ADC6)
  - 4-bit Reduced Chain Comparator (RCC4)
  - 8-bit Reduced Chain Comparator (RCC8)
"""
"""
Functions that emulate the behavior of
AxC Full Adders. Currently supported FAs are:
  - SMA
  - AMA1
  - AMA2
  - AXA2
  - AXA3
  - BXFA
  - exact
"""


def sma(a, b, c_in):
    sum = [0, 1, 0, 0, 0, 0, 0, 1]
    c_out = [0, 0, 1, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos] & 1, c_out[pos] & 1)


def ama1(a, b, c_in):
    sum = [1, 1, 0, 0, 1, 0, 0, 0]
    c_out = [0, 0, 1, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos] & 1, c_out[pos] & 1)


def ama2(a, b, c_in):
    sum = [0, 1, 0, 1, 0, 0, 0, 1]
    c_out = [0, 0, 0, 0, 1, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos] & 1, c_out[pos] & 1)


def axa2(a, b, c_in):
    sum = [1, 1, 0, 0, 0, 0, 1, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos] & 1, c_out[pos] & 1)


def axa3(a, b, c_in):
    sum = [0, 1, 0, 0, 0, 0, 0, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos] & 1, c_out[pos] & 1)


def exact(a, b, c_in):
    sum = [0, 1, 1, 0, 1, 0, 0, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return (sum[pos], c_out[pos])


def bxfa(a, b, c_in):
    return (a & 1, b & 1)


def n_edc(a: int, b: int, n: int) -> int:
    """Exact Dedicated Comparator (EDC)"""
    # formatting stuff
    a = format(a, "#0%db" % (n + 2))[:1:-1]
    b = format(b, "#0%db" % (n + 2))[:1:-1]
    a = list(map(int, a))
    b = list(map(int, b))
    # compute xnors
    eq = [0] * n
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
    return ~greater & 1 == 1


def n_axdc2(a: int, b: int, n: int) -> int:
    """Approximate Dedicated Comparator 2 (AxDC2)"""
    # formatting stuff
    a = format(a, "#0%db" % (n + 2))[:1:-1]
    b = format(b, "#0%db" % (n + 2))[:1:-1]
    a = list(map(int, a))
    b = list(map(int, b))
    # compute xnors
    eq = [0] * n
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
    return ~greater & 1 == 1


def n_axdc6(a: int, b: int, n: int) -> int:
    """Approximate Dedicated Comparator 6 (ADC6)"""
    # formatting stuff
    a = format(a, "#0%db" % (n + 2))[:1:-1]
    b = format(b, "#0%db" % (n + 2))[:1:-1]
    a = list(map(int, a))
    b = list(map(int, b))
    # compute xnors
    n_2 = n // 2
    n_4 = n // 4
    eq = [0] * n

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


# soma simples nbit
def add(adder, in_a, in_b, n_bits):
    final = ""
    cin = 0
    for i in range(n_bits - 1, -1, -1):
        fa = adder(int(in_a[i]) & 1, int(in_b[i]) & 1, cin)
        final += str(fa[0])
        cin = fa[1]
    final = final[::-1]
    return final, cin


# subtracao simples nbit
def sub(adder, in_a, in_b, n_bits):
    a = format(in_a, "#0%db" % (n_bits + 2))[:1:-1]
    b = format(in_b, "#0%db" % (n_bits + 2))[:1:-1]
    in_a = list(map(int, a))
    in_b = list(map(int, b))
    final = [0] * n_bits
    cin = 1
    for i in range(n_bits - 1, -1, -1):
        fa = adder(int(in_a[i]) & 1, ~int(in_b[i]) & 1, cin)
        final[i] = fa[0]
        cin = fa[1]
    return final, cin


# a >= b
def geq(adder, in_a, in_b, n_bits):
    # A >= B : A - B >= 0
    _, cout = sub(adder, in_a, in_b, n_bits)
    return cout & 1


# a <= b
def leq(adder, in_a, in_b, n_bits):
    _, cout = sub(adder, in_b, in_a, n_bits)
    return cout


def e_comp(a, b):
    return 1 if a <= b else 0


def error_metrics_nbits(n_bits, comparator):
    error_counter = 0
    for i in range(2 ** n_bits):
        for j in range(2 ** n_bits):
            if e_comp(i, j) != comparator(i, j, n_bits):
                error_counter += 1
    return {"ED": error_counter, "ER": 100 * error_counter / 2 ** (2 * n_bits)}


import pandas as pd

ADDERS = [sma, ama1, ama2]
DEDICATED = [n_edc, n_adc2, n_adc6]
COMPARATORS = DEDICATED
COMPARATOR_NAMES = [comparator.__name__ for comparator in COMPARATORS]
rates_4b = []
rates_8b = []
import functools

for comparator in COMPARATORS:
    # if comparator in ADDERS:
    #     rates_4b.append(pd.Series(error_metrics_nbits(4, comp)))
    #     rates_8b.append(pd.Series(error_metrics_nbits(8, comp)))

    rates_4b.append(pd.Series(error_metrics_nbits(4, comparator)))
    rates_8b.append(pd.Series(error_metrics_nbits(8, comparator)))
rates_4b = pd.concat(rates_4b, axis=0, keys=COMPARATOR_NAMES)
rates_8b = pd.concat(rates_8b, axis=0, keys=COMPARATOR_NAMES)
print(rates_4b)
print(rates_8b)

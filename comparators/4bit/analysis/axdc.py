"""
Functions that simulate the behaviour of AxC arithmetic
circuits. Currently supported are the 4-bit comparators:
  - AxC Dedicated Comparators (AxDCs)
  - AxC Full Adder-based Comparators (AxFAs)
"""


def edc(a, b):
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    eq1 = ~(a[1] ^ b[1])
    eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    eq0 = ~(a[0] ^ b[0])  # mais uma xnor
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    n0 = ~(a[0] & ~b[0] & eq3 & eq2 & eq1)
    return (n0 & n1 & n2 & n3) & 1  # , (eq0 & eq1 & eq2 & eq3) & 1 # mais uma and


def axdc1(a, b):
    ## primeira aproximação: sem nand a0 ~b0
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    eq1 = ~(a[1] ^ b[1])
    eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    n0 = ~(eq3 & eq2 & eq1)
    return (n0 & n1 & n2 & n3) & 1


def axdc2(a, b):
    ## aprrox 2: tirar a lógica do bit 0
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    # eq1 = ~(a[1] ^ b[1])
    eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    # n0 = ~(a[0] & ~b[0] & eq3 & eq2 & eq1)
    return (n1 & n2 & n3) & 1


def axdc3(a, b):
    ## substituir as portas com a0 por um buffer a0
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    # return (a[0] & n1 & n2 & n3) & 1
    return (b[0] & n1 & n2 & n3) & 1


def axdc4(a, b):
    # aproximação: trocar portas logicas com a1 por só a1
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    # eq1 = ~(a[1] ^ b[1])
    eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    # n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    # n0 = ~(a[0] & ~b[0] & eq3 & eq2 & a[1])
    # return (n0 & a[1] & n2 & n3) & 1
    n0 = ~(a[0] & ~b[0] & eq3 & eq2 & b[1])
    return (n0 & b[1] & n2 & n3) & 1


def axdc5(a, b):
    # aproximação: trocar lógica dos bits 0 e 1 por a0 e a1
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    # eq1 = ~(a[1] ^ b[1])
    # eq2 = ~(a[2] ^ b[2])
    n0, n1 = b[0], b[1]
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    # n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    # n0 = ~(a[0] & ~b[0] & eq3 & eq2 & eq1)
    return (n0 & n1 & n2 & n3) & 1


def axdc6(a, b):
    # aproximação: tirar lógica com bit 0 e trcar a do bit 1 por a1
    a = [int(i) for i in a][::-1]
    b = [int(i) for i in b][::-1]
    # eq1 = ~(a[1] ^ b[1])
    # eq2 = ~(a[2] ^ b[2])
    eq3 = ~(a[3] ^ b[3])
    n3 = ~(a[3] & ~b[3])
    n2 = ~(a[2] & ~b[2] & eq3)
    n1 = b[1]
    # n1 = ~(a[1] & ~b[1] & eq3 & eq2)
    # n0 = ~(a[0] & ~b[0] & eq3 & eq2 & eq1)
    return (n1 & n2 & n3) & 1


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
    (
        _,
        cout,
    ) = sub(adder, in_b, in_a, n_bits)
    return cout

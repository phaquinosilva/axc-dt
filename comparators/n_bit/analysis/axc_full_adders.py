from typing import Callable, List, Tuple


def sma(a, b, c_in):
    sum = [0, 1, 0, 0, 0, 0, 0, 1]
    c_out = [0, 0, 1, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos] & 1, c_out[pos] & 1


def ama1(a, b, c_in):
    sum = [1, 1, 0, 0, 1, 0, 0, 0]
    c_out = [0, 0, 1, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos] & 1, c_out[pos] & 1


def ama2(a, b, c_in):
    sum = [0, 1, 0, 1, 0, 0, 0, 1]
    c_out = [0, 0, 0, 0, 1, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos] & 1, c_out[pos] & 1


def axa2(a, b, c_in):
    sum = [1, 1, 0, 0, 0, 0, 1, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos] & 1, c_out[pos] & 1


def axa3(a, b, c_in):
    sum = [0, 1, 0, 0, 0, 0, 0, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos] & 1, c_out[pos] & 1


def exact(a, b, c_in):
    sum = [0, 1, 1, 0, 1, 0, 0, 1]
    c_out = [0, 0, 0, 1, 0, 1, 1, 1]
    pos = (a << 2) + (b << 1) + c_in
    return sum[pos], c_out[pos]


def bxfa(a, b, c_in):
    return a & 1, b & 1


# soma simples nbit
def add(adder, in_a, in_b, n_bits):
    a = format(in_a, f"#0{n_bits + 2}b")[2:]
    b = format(in_b, f"#0{n_bits + 2}b")[2:]
    a = list(map(int, a))
    b = list(map(int, b))
    final = []
    cin = 0
    for i in range(n_bits - 1, -1, -1):
        fa = adder(a[i] & 1, b[i] & 1, cin)
        final.append(fa[0])
        cin = fa[1]
    final = final[::-1]
    return final, cin


# subtracao simples nbit
def sub(adder: Callable, in_a: int, in_b: int, n_bits: int) -> Tuple[List[int], int]:
    a = format(in_a, f"#0{n_bits + 2}b")[2:]
    b = format(in_b, f"#0{n_bits + 2}b")[2:]
    a = list(map(int, a))
    b = list(map(int, b))
    final = []
    cin = 0
    for i in range(n_bits - 1, -1, -1):
        s, cout = adder(a[i] & 1, ~b[i] & 1, cin)
        final.append(s)
        cin = cout
    final = final[::-1]
    return final, cin

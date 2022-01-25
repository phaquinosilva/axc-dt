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

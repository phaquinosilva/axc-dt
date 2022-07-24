import pytest

from comparators.four_bit.analysis.axdc import axdc2, axdc6, edc
from comparators.n_bit.analysis.axc_full_adders import add, exact
from comparators.n_bit.analysis.nbit_comparators import (
    bin_to_dec,
    exact_leq,
    leq,
    n_axdc1,
    n_axdc2,
    n_edc,
)


@pytest.mark.parametrize(
    "original, n_bit", [(edc, n_edc), (axdc2, n_axdc1), (axdc6, n_axdc2)]
)
def test_4bit_comparators(original, n_bit):
    diff_counter = 0
    for i in range(2**4):
        for j in range(2**4):
            if original(i, j) != n_bit(i, j, 4):
                diff_counter += 1
    assert diff_counter == 0


def test_8bit_edc():
    def edc_8b(a, b):
        ## aprrox 2: tirar a lógica do bit 0
        a = format(a, "#0%db" % 10)[:1:-1]
        b = format(b, "#0%db" % 10)[:1:-1]
        a = [int(i) for i in a]
        b = [int(i) for i in b]
        eq1 = ~(a[1] ^ b[1])
        eq2 = ~(a[2] ^ b[2])
        eq3 = ~(a[3] ^ b[3])
        eq4 = ~(a[4] ^ b[4])
        eq5 = ~(a[5] ^ b[5])
        eq6 = ~(a[6] ^ b[6])
        eq7 = ~(a[7] ^ b[7])
        n7 = ~(a[7] & ~b[7])
        n6 = ~(a[6] & ~b[6] & eq7)
        n5 = ~(a[5] & ~b[5] & eq7 & eq6)
        n4 = ~(a[4] & ~b[4] & eq7 & eq6 & eq5)
        n3 = ~(a[3] & ~b[3] & eq7 & eq6 & eq5 & eq4)
        n2 = ~(a[2] & ~b[2] & eq7 & eq6 & eq5 & eq4 & eq3)
        n1 = ~(a[1] & ~b[1] & eq7 & eq6 & eq5 & eq4 & eq3 & eq2)
        n0 = ~(a[0] & ~b[0] & eq7 & eq6 & eq5 & eq4 & eq3 & eq2 & eq1)
        return (n7 & n6 & n5 & n4 & n3 & n2 & n1 & n0) & 1

    # assert test implementation works
    for i in range(2**8):
        for j in range(2**8):
            assert n_edc(i, j, 8) == exact_leq(i, j)

    for i in range(2**8):
        for j in range(2**8):
            assert edc_8b(i, j) == exact_leq(i, j)
    # assert generic version works
    for i in range(2**8):
        for j in range(2**8):
            assert edc_8b(i, j) == n_edc(i, j, 8)


def test_8bit_axdc1():
    def axdc1_8b(a, b):
        a = format(a, "#0%db" % 10)[:1:-1]
        b = format(b, "#0%db" % 10)[:1:-1]
        a = [int(i) for i in a]
        b = [int(i) for i in b]

        eq3 = ~(a[3] ^ b[3])
        eq4 = ~(a[4] ^ b[4])
        eq5 = ~(a[5] ^ b[5])
        eq6 = ~(a[6] ^ b[6])
        eq7 = ~(a[7] ^ b[7])
        n7 = ~(a[7] & ~b[7])
        n6 = ~(a[6] & ~b[6] & eq7)
        n5 = ~(a[5] & ~b[5] & eq7 & eq6)
        n4 = ~(a[4] & ~b[4] & eq7 & eq6 & eq5)
        n3 = ~(a[3] & ~b[3] & eq7 & eq6 & eq5 & eq4)
        n2 = ~(a[2] & ~b[2] & eq7 & eq6 & eq5 & eq4 & eq3)
        return (n7 & n6 & n5 & n4 & n3 & n2) & 1

    for i in range(2**8):
        for j in range(2**8):
            assert axdc1_8b(i, j) == n_axdc1(i, j, 8)


def test_nbit_adders():
    for i in range(2**8):
        for j in range(2**8):
            add_result, cout = add(adder=exact, in_a=i, in_b=j, n_bits=8)
            add_result = [cout] + add_result
            assert bin_to_dec(add_result) == i + j


def test_exact_fa_comparator():
    for i in range(2**8):
        for j in range(2**8):
            assert leq(i, j, 8, exact) == exact_leq(i, j)


def test_16bit_axdc2():
    def axdc2_16b(a, b):
        ## aprrox 2: tirar a lógica do bit 0
        a = format(a, "#0%db" % 18)[:1:-1]
        b = format(b, "#0%db" % 18)[:1:-1]
        a = [int(i) for i in a]
        b = [int(i) for i in b]
        eq = [~(a[i] ^ b[i]) for i in range(1, 16)]
        n15 = ~(a[15] & ~b[15])
        n14 = ~(a[14] & ~b[14] & eq[14])
        n13 = ~(a[13] & ~b[13] & eq[14] & eq[13])
        n12 = ~(a[12] & ~b[12] & eq[14] & eq[13] & eq[12])
        n11 = ~(a[11] & ~b[11] & eq[14] & eq[13] & eq[12] & eq[11])
        n10 = ~(a[10] & ~b[10] & eq[14] & eq[13] & eq[12] & eq[11] & eq[10])
        n9 = ~(a[9] & ~b[9] & eq[14] & eq[13] & eq[12] & eq[11] & eq[10] & eq[9])
        n8 = ~(
            a[8] & ~b[8] & eq[14] & eq[13] & eq[12] & eq[11] & eq[10] & eq[9] & eq[8]
        )
        n7 = b[7]
        n6 = b[6]
        n5 = b[5]
        n4 = b[4]
        return (n15 & n14 & n13 & n12 & n11 & n10 & n9 & n8 & n7 & n6 & n5 & n4) & 1

    import numpy as np

    np.random.seed(12345)
    test_i = np.random.randint(low=0, high=2**16, size=500)
    test_j = np.random.randint(low=0, high=2**16, size=500)
    for i in test_i:
        for j in test_j:
            assert axdc2_16b(i, j) == n_axdc2(i, j, 16)

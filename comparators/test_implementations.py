import pytest
from four_bit.analysis.axdc import axdc2, axdc6, edc
from nbit.analysis.nbit_comparators import n_adc2, n_adc6, n_edc


@pytest.mark.parametrize(
    "original, n_bit", [(edc, n_edc), (axdc2, n_adc2), (axdc6, n_adc6)]
)
def test_4bit_comparators(original, n_bit):
    diff_counter = 0
    for i in range(2 ** 4):
        for j in range(2 ** 4):
            if original(i, j) != n_bit(i, j, 4):
                diff_counter += 1
    assert diff_counter == 0

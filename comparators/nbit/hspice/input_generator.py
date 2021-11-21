"""
Source voltage file input generator for C5.0 applications.
Reads from a log file of the operands used during classification
and provide SPICE files with PWL transitions for simulation.
"""

from pathlib import Path
from typing import List, Tuple


def write_source(
    after_state: Tuple[int, int],
    n: int,
    saving_file: Path,
    before_state: Tuple[int, int] = (0, 0),
) -> None:
    """
    Writes PWL to sources file
    :param before_state:
        A tuple of integers containing the previous input values to the operation.
    :param after_state:
        A tuple of integers containing the current input values to the operation.
    :param n:
        An integer with the number of bits to be used in creating the sources.
    :param saving_file:
        A string with the name of the file to which the user wants to write.
    """
    format_binary = lambda x: format(x, "#0" + str(n + 2) + "b")[:1:-1]
    a0, a1, b0, b1 = tuple(
        format_binary(i) for _input in zip(before_state, after_state) for i in _input
    )
    with saving_file.open(mode="w+") as file:
        file.write("* sources \n\n")
        # writes all input sources for A
        file.write("* " + str(n) + "-bit input A\n")
        for i in range(n):
            if a0[i] == "0":
                if a1[i] == "0":
                    file.write("Va%d a%d_in gnd PWL(0n 0)\n" % (i, i))
                else:
                    file.write("Va%d a%d_in gnd PWL(0n 0 1n 0 1.1n vdd)\n" % (i, i))
            else:
                if a1[i] == "0":
                    file.write("Va%d a%d_in gnd PWL(0n vdd 1n vdd 1.1n 0)\n" % (i, i))
                else:
                    file.write("Va%d a%d_in gnd PWL(0n vdd)\n" % (i, i))
        # writes all input sources for A
        file.write("* %d-bit input B\n" % n)
        for i in range(n):
            if b0[i] == "0":
                if b1[i] == "0":
                    file.write("Vb%d b%d_in gnd PWL(0n 0)\n" % (i, i))
                else:
                    file.write("Vb%d b%d_in gnd PWL(0n 0 1n 0 1.1n vdd)\n" % (i, i))
            else:
                if b1[i] == "0":
                    file.write("Vb%d b%d_in gnd PWL(0n vdd 1n vdd 1.1n 0)\n" % (i, i))
                else:
                    file.write("Vb%d b%d_in gnd PWL(0n vdd)\n" % (i, i))


def count_repeated(input_file: Path) -> Tuple[List[int], List[int]]:
    import subprocess

    sort = subprocess.Popen(["sort", str(input_file)], stdout=subprocess.PIPE)
    count = subprocess.check_output(["uniq", "-c"], stdin=sort.stdout)
    unique = count.decode("utf-8")
    unique = unique.split("\n")
    pairs = []
    for line in unique[:-1]:
        num, values = line.split(" ")[-2:]
        val1, val2 = values.split(",")
        pairs.append((int(num), (int(float(val1)), int(float(val2)))))
    return pairs


def create_input_sources(
    inputs_file: Path, saving_dir: Path, n: int, dataset: str
) -> List[Tuple[int, Tuple[int, int]]]:
    """
    Creates sources for all inputs while simulating the energy consumption
    of an application.
    :param inputs_file:
        A Path object pointing to the log of the application to be simulated.
    :param saving_dir:
        A Path object containing the path to the directory where sources files
        are to be stored.
    :param n:
        An integer with the number of bits to be used in the application.
    :return:
        An integer with the number of operations to be simulated.
    """
    if not saving_dir.exists():
        saving_dir.mkdir()
    repeated = count_repeated(input_file=inputs_file)
    for id, pair in enumerate(repeated):
        _, operation = pair
        write_source(
            after_state=operation,
            n=n,
            saving_file=saving_dir / ("source_operation_%d.txt" % id),
        )
    return repeated

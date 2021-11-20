#!/usr/bin/python3

import os
from pathlib import Path
from input_generator import create_input_sources

NOMINAL_VOLTAGE = 0.7
SIMULATION_TIME = 2.5e-9
ADDERS = ["sma", "ama1", "ama2"]
COMPARATORS = ["edc", "axdc2", "axdc6"]

CATEGORICAL = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
MIXED = ["health", "iris", "forest"]


def simulate_operations(input_file: Path, name: str, n_bits: int) -> None:
    """
    Simulates the comparisons made in a DT application
    with n-bit comparators
    """
    for circuit in ADDERS + COMPARATORS:
        if circuit in ADDERS:
            create_rca_include(circuit, n_bits)
        num_samples = create_input_sources(
            inputs_file=input_file / f"logs/{name}_{circuit}.testlog",
            saving_dir=Path.cwd() / "sources",
            n=n_bits,
        )
        for i in range(num_samples):
            run_simulation(comparator=circuit, op_index=i, n_bits=n_bits, dataset=name)


def create_rca_include(fa: str, n: int) -> None:
    """Create SPICE description for n-bit Ripple Carry Adder using specified FA"""
    rca_text = f"* {n} bit Ripple Carry Adder\n"
    a = " ".join(["a%d" % i for i in range(n)])
    b = " ".join(["b%d" % i for i in range(n)])
    s = " ".join(["s%d" % i for i in range(n)])
    rca_text += f".subckt rca{n}b {a} {b} c0 {s} c{n} vdd\n"
    for i in range(n):
        rca_text += f"XFA{i} a{i} b{i} c{i} s{i} c{i+1} vdd {fa}\n"
    rca_text += ".ends"
    with open("rca.cir", "w") as f:
        f.write(rca_text)


def run_simulation(comparator: str, op_index: int, n_bits: int, dataset: str) -> None:
    """Runs simulation for a single operation"""
    with open("simulation_info.txt", "w") as f:
        f.seek(0)
        if comparator in ADDERS:
            f.write(f".include fas/{comparator}.cir\n")
            f.write(".include rca.cir\n")
            f.write(f".include comparators/axfa_{n_bits}b.cir\n")
        else:
            f.write(f".include comparators/{comparator}_{n_bits}b.cir\n")
        f.write(f".include sources/source_operation_{op_index}.txt\n")
    inputs = " ".join(["a%d" % i for i in range(n_bits)]) + " " +" ".join(
        ["b%d" % i for i in range(n_bits)]
    )
    with open("circuit.cir", "r") as f:
        contents = f.read()
    contents = contents.replace("<inputs>", inputs)
    with open("circuit.cir", "w") as f:
        f.seek(0)
        f.write(contents)
    os.system("hspice circuit.cir")
    with open("circuit.cir", "r") as f:
        contents = f.read()
    contents = contents.replace(inputs, "<inputs>")
    with open("circuit.cir", "w") as f:
        f.seek(0)
        f.write(contents)
    if not (Path(f"results/{dataset}")).exists():
        (Path(f"results/{dataset}")).mkdir()
    os.rename(
        "./circuit.mt0.csv",
        f"results/{dataset}/result_{comparator}_{op_index}.csv",
    )


if __name__ == "__main__":
    operations = Path.cwd()
    for name in CATEGORICAL:
        simulate_operations(operations, name, 4)
    for name in MIXED:
        simulate_operations(operations, name, 8)

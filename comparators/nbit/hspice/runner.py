#!/usr/bin/python3

import os
from pathlib import Path
from typing import Dict
from input_generator import create_input_sources

NOMINAL_VOLTAGE = 0.7
SIMULATION_TIME = 2.5e-9
ADDERS = ["sma", "ama1", "ama2"]
COMPARATORS = ["edc", "axdc2"]


def simulate_operations(input_file: Path, name: str, n_bits: int) -> None:
    """
    Simulates the comparisons made in a DT application
    with n-bit comparators
    """
    for circuit in ADDERS + COMPARATORS:
        if circuit in ADDERS:
            create_rca_include(circuit, n_bits)
        num_samples = create_input_sources(
            inputs_file=input_file / f"logs/{name}_{circuit}.comp",
            saving_dir=Path.cwd() / "sources",
            n=n_bits,
        )
        for i in range(num_samples):
            run_simulation(comparator=circuit, op_index=i, n_bits=n_bits)


def create_rca_include(fa: str, n: int) -> None:
    """Create SPICE description for n-bit Ripple Carry Adder using specified FA"""
    rca_text = f"* {n} bit Ripple Carry Adder\n"
    a = " ".join(["a%d" % i for i in range(n)])
    b = " ".join(["b%d" % i for i in range(n)])
    s = " ".join(["s%d" % i for i in range(n)])
    rca_text += f".subckt rca{n}b {a} {b} c0 {s} vdd\n"
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
            f.write(".include rca.cir\n")
        f.write(f".include comparators/{comparator}_{n_bits}b.cir\n")
        f.write(f".include sources/source_operation_{op_index}.txt\n")
    os.system("hspice circuit.cir")
    os.rename(
        "./circuit.mt0.csv",
        f"results/{dataset}/result_{comparator}_{op_index}.csv",
    )


if __name__ == "__main__":
    data = ["iris", "forest", "health"]
    operations = Path.cwd()
    for name in data:
        simulate_operations(operations, name, 8)

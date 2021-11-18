import os
import pandas as pd
from pathlib import Path


def sim_adders():
    adders = ["exact", "sma", "ama1", "ama2", "axa2", "axa3"]
    datasets = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
    ## make default
    os.system("make")
    os.system("mv c5.0 ../discrete-only/c5.0_default")
    for adder in adders:
        ## make approximate versions
        with open("classify.c", "r") as f:
            classify = f.read()
        # teste de atributo discreto
        classify = classify.replace(
            "if ( Dv <= T->Forks )", "if ( leq(Dv, T->Forks, " + adder + ", 4) )"
        )
        # teste de subconjunto discreto
        classify = classify.replace(
            "if ( Dv <= MaxAttVal[T->Tested] )",
            "if ( leq(Dv,  MaxAttVal[T->Tested], " + adder + ", 4) )",
        )
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)
        os.system("make")
        os.system("mv c5.0 ../discrete-only/c5.0_fa_" + adder)
        with open("classify.c", "r") as f:
            classify = f.read()
        classify = classify.replace(
            "if ( leq(Dv, T->Forks, " + adder + ", 4) )", "if ( Dv <= T->Forks )"
        )
        classify = classify.replace(
            "if ( leq(Dv,  MaxAttVal[T->Tested], " + adder + ", 4) )",
            "if ( Dv <= MaxAttVal[T->Tested] )",
        )
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def sim_dedicated():
    comparators = [
        "leq_exact",
        "leq_a1",
        "leq_a2",
        "leq_a3",
        "leq_a4",
        "leq_a5",
        "leq_a6",
    ]
    datasets = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
    for comp in comparators:
        ## make approximate versions
        with open("classify.c", "r") as f:
            classify = f.read()
        # teste de atributo discreto
        classify = classify.replace(
            "if ( Dv <= T->Forks )", "if ( " + comp + "(Dv, T->Forks) )"
        )
        # teste de subconjunto discreto
        classify = classify.replace(
            "if ( Dv <= MaxAttVal[T->Tested] )",
            "if ( " + comp + "(Dv,  MaxAttVal[T->Tested]) )",
        )
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)
        os.system("make")
        os.system("mv c5.0 ../discrete-only/c5.0_" + comp)
        with open("classify.c", "r") as f:
            classify = f.read()
        classify = classify.replace(
            "if ( " + comp + "(Dv, T->Forks) )", "if ( Dv <= T->Forks )"
        )
        classify = classify.replace(
            "if ( " + comp + "(Dv,  MaxAttVal[T->Tested]) )",
            "if ( Dv <= MaxAttVal[T->Tested] )",
        )
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def train():
    adders = ["exact", "sma", "ama1", "ama2", "axa2", "axa3"]
    comparators = [
        "leq_exact",
        "leq_a1",
        "leq_a2",
        "leq_a3",
        "leq_a4",
        "leq_a5",
        "leq_a6",
    ]
    datasets = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
    for dataset in datasets:
        # os.mkdir('../'+dataset+'/trees')
        os.system(
            "../discrete-only/c5.0_default -f ../"
            + dataset
            + "/"
            + dataset
            + " > ../"
            + dataset
            + "/trees/"
            + dataset
            + "_default"
            + ".output"
        )
        for adder in adders:
            os.system(
                "../discrete-only/c5.0_fa_"
                + adder
                + " -f ../"
                + dataset
                + "/"
                + dataset
                + " > ../"
                + dataset
                + "/trees/"
                + dataset
                + "_"
                + adder
                + ".output"
            )
        for comp in comparators:
            os.system(
                "../discrete-only/c5.0_"
                + comp
                + " -f ../"
                + dataset
                + "/"
                + dataset
                + " > ../"
                + dataset
                + "/trees/"
                + dataset
                + "_"
                + comp
                + ".output"
            )

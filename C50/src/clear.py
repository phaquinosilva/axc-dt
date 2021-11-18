import os


def clear():
    os.system(
        "rm c50_files/files/* trees/* temp/* pos/* pos/aig/* sop/* sop/aig/* *_table_results nohup* *results*"
    )
    os.system("rm *.o")


if __name__ == "__main__":
    clear()

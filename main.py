import argparse

from cdcl import cdcl
from utils import read_cnf


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", type=str, default="examples/and1.cnf"
    )

    return parser.parse_args()

def main(args):
    # Create problem.
    with open(args.input, "r") as f:
        sentence, num_vars = read_cnf(f)

    # Create CDCL solver and solve it!
    res = cdcl(sentence, num_vars)

    if res is None:
        print("✘ No solution found")
    else:
        solved = {}
        for clause in sentence:
            solved[str(clause)] = False
        for clause in sentence:
            for lit in res:
                if lit in clause:
                    solved[str(clause)] = True
                    break
        for clause in sentence:
            if solved[str(clause)] == False:
                print(f"✔ Successfully found a fake solution: {res}", "\n\nunsolved clause:", clause)
                return

            
        print(f"✔ Successfully found a solution: {res}")

if __name__ == "__main__":
    args = parse_args()
    main(args)

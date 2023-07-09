This repository is for the course project of CS3317 Artificial Intelligence B. I have implemented the CDCL algorithm for SAT problems.

---
## Introduction
In this CDCL SAT solver, I use VSIDS heuristic to score all literals. Below are VSIDS steps:
1. Initiate each literal’s VSIDS score with its count number.
2. Increase score by 1 each time add the learned clause.
3. Divide all scores by a constant periodically.

To understand how CDCL algorithm works, you can refer to this [demo](https://cse442-17f.github.io/Conflict-Driven-Clause-Learning/).
## Run
A powershell test script is provided to test all SAT problems in the `./examples` file.
But you can also test each problem with the following instruction:
```
python main.py -i [path to SAT problem file(*.cnf)]
```
The test result for `test.ps.1` can be found at `./record`.
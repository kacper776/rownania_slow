from base import *
from itertools import combinations
from functools import reduce
from z3 import Int, Solver, sat, ModelRef


def solve_block_eq(blocks_L, blocks_R, X, vanishing_vars) -> list:
    def sum_block(block, X):
        return reduce(lambda a, b: a + b.cnt if is_letter(b)
                                   else a + X[b.nr],
                      block, 0)

    len_L = len(blocks_L)
    len_R = len(blocks_R)
    X = {var_nr: Int(var_name) for var_nr, var_name in X.items()}
    solver = Solver()

    for x in X.values():
        solver.add(x >= 0)

    for var in vanishing_vars:
        var_l = X[var.nr * 2]
        var_r = X[var.nr * 2 + 1]
        solver.add(var_l + var_r > 0)

    if solver.check() != sat:
        return []

    result = []
    for equalities_cnt in range(min(len_L, len_R) + 1):
        for nonzero_blocks_L in combinations(blocks_L, equalities_cnt):
            for nonzero_blocks_R in combinations(blocks_R, equalities_cnt):
                solver.push()
                for block in blocks_L:
                    if block not in nonzero_blocks_L:
                        zero_block = sum_block(block, X)
                        solver.add(zero_block == 0)
                for block in blocks_R:
                    if block not in nonzero_blocks_R:
                        zero_block = sum_block(block, X)
                        solver.add(zero_block == 0)

                for i in range(equalities_cnt):
                    left_side = sum_block(nonzero_blocks_L[i], X)
                    right_side = sum_block(nonzero_blocks_R[i], X)
                    solver.add(left_side == right_side)

                if solver.check() == sat:
                    result.append(solver.model())
                solver.pop()
    return result

from base import *
from itertools import combinations
from functools import reduce
from z3 import Int, Solver, sat, ModelRef


def solve_block_eq(blocks_L, blocks_R, X, vanishing_vars):
    def sum_block(block, X):
        return reduce(lambda a, b: a + b.cnt if is_letter(b)
                                   else a + X[b.nr],
                      block)

    def find_nonzero_margins(blocks):
        nonzero_prefix = -1
        nonzero_suffix = -1
        for block in blocks:
            if any(filter(is_letter, block)):
                nonzero_prefix += 1
            else:
                break
        for block in reversed(blocks):
            if any(filter(is_letter, block)):
                nonzero_suffix += 1
            else:
                break
        return nonzero_prefix, nonzero_suffix

    len_L = len(blocks_L)
    len_R = len(blocks_R)
    X = {var_nr: Int(var_name) for var_nr, var_name in X.items()}
    nonzero_prefix_L, nonzero_suffix_L = find_nonzero_margins(blocks_L)
    nonzero_prefix_R, nonzero_suffix_R = find_nonzero_margins(blocks_R)

    if nonzero_prefix_L >= len_R or nonzero_suffix_L >= len_R:
        return None
    if nonzero_prefix_R >= len_L or nonzero_suffix_R >= len_L:
        return None

    solver = Solver()
    for i in range(max(nonzero_prefix_L, nonzero_prefix_R)):
        left_side = sum_block(blocks_L[i], X)
        right_side = sum_block(blocks_R[i], X)
        solver.add(left_side == right_side)

    for i in range(min(len_L - 1 - nonzero_prefix_L, len_R - 1 - nonzero_prefix_R), min(len_L, len_R)):
        left_side = sum_block(blocks_L[i], X)
        right_side = sum_block(blocks_R[i], X)
        solver.add(left_side == right_side)

    for x in X.values():
        solver.add(x >= 0)

    for var in vanishing_vars:
        var_l = X[var.nr * 2]
        var_r = X[var.nr * 2 + 1]
        solver.add(var_l + var_r > 0)

    if solver.check() != sat:
        return None

    blocks_L = blocks_L[nonzero_prefix_L + 1 : len_L - 1 - nonzero_suffix_L]
    blocks_R = blocks_R[nonzero_prefix_R + 1 : len_R - 1 - nonzero_suffix_R]
    len_L = len(blocks_L)
    len_R = len(blocks_R)

    result = []
    for equalities_cnt in range(min(len_L, len_R)):
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
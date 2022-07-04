from base import *
from diophantic_solver import *
from itertools import combinations
from copy import copy


class Node(object):
    def __init__(self, L: list, R: list):
        self.L, self.R = simplify_eq(L, R)
        self.letters = set()
        self.variables = set()
        for symbol in L + R:
            if(is_letter(symbol)):
                self.letters.add(symbol)
            if(is_variable(symbol)):
                self.variables.add(symbol)

    def __eq__(self, other):
        for l0, l1 in list(zip(self.L, other.L)):
            if l0 != l1:
                return False
        for r0, r1 in list(zip(self.R, other.R)):
            if r0 != r1:
                return False
        return True  
    
    def __repr__(self):
        return f'{self.L} = {self.R}'

    def children(self):
        def merge_blocks(L: list, R: list, letter: Letter, vanishing_vars: set):
            def get_blocks(side: list, letter: Letter):
                blocks = []
                curr_block = []
                for symbol in side:
                    if is_letter(symbol):
                        if(symbol == letter):
                            curr_block.append(symbol)
                        else:
                            if(curr_block):
                                blocks.append(tuple(curr_block))
                                curr_block = []
                    if is_variable(symbol):
                        curr_block.append(Variable(2 * symbol.nr)) # left
                        if(curr_block):
                            blocks.append(tuple(curr_block))
                            curr_block = []
                        curr_block = [Variable(2 * symbol.nr + 1)] # right
                if(curr_block):
                    blocks.append(tuple(curr_block))
                    curr_block = []
                return blocks

            def merge_solution_to_node(solution: ModelRef, letter: Letter):
                def build_eq_side(side: list):
                    result = []
                    for symbol in side:
                        if is_letter(symbol):
                            result.append(symbol)
                        else:
                            pop_cnt_L = solution[2 * symbol.nr]
                            pop_cnt_R = solution[2 * symbol.nr + 1]
                            if pop_cnt_L > 0:
                                new_letters = copy(letter)
                                new_letters.cnt = pop_cnt_L
                                result.append(new_letters)
                            if symbol not in vanishing_vars:
                                result.append(copy(symbol))
                            if pop_cnt_R > 0:
                                new_letters = copy(letter)
                                new_letters.cnt = pop_cnt_R
                                result.append(new_letters)
                    return result                

                new_L = build_eq_side(L)
                new_R = build_eq_side(R)
                return Node(new_L, new_R)

            blocks_L = get_blocks(L, letter)
            blocks_R = get_blocks(R, letter)
            X = {var.nr: f'x_{var.nr}' for block in blocks_L + blocks_R
                                       for var in block  
                                       if is_variable(var)}
            solutions = solve_block_eq(blocks_L, blocks_R, X, vanishing_vars)
            return [merge_solution_to_node(solution, letter) for solution in solutions]


        def merge_pair(letter0: Letter, letter1: Letter):
            def merge(side: list, result_letter: Letter):
                result = []
                for i in range(len(side) - 1):
                    if side[i] == letter0 and side[i + 1] == letter1:

                        result.append(result_letter)


def simplify_eq(L: list, R: list):
    def group_letters(side: list):
        new_side = []
        for symbol in side:
            if is_letter(symbol) and new_side and symbol == new_side[-1]:
                new_side[-1].cnt += symbol.cnt
            elif is_variable(symbol) or symbol.cnt > 0:
                new_side.append(symbol)
        return new_side

    def find_significant_infix(L: list, R: list):
        redundant_prefix_L = 0
        redundant_prefix_R = 0
        for symbol_L, symbol_R in zip(L, R):
            if symbol_L == symbol_R:
                if is_letter(symbol_L):
                    shared_letters_cnt = min(symbol_R.cnt, symbol_L.cnt)
                    symbol_L.cnt -= shared_letters_cnt
                    symbol_R.cnt -= shared_letters_cnt
                    if symbol_L.cnt == 0:
                        redundant_prefix_L += 1
                    if symbol_R.cnt == 0:
                        redundant_prefix_R += 1
                    if symbol_L.cnt + symbol_L.cnt > 0:
                        break
                else:
                    redundant_prefix_L += 1
                    redundant_prefix_R += 1
            else:
                break
        L = L[redundant_prefix_L :]
        R = R[redundant_prefix_R :]

        redundant_suffix_L = 0
        redundant_suffix_R = 0
        for symbol_L, symbol_R in zip(reversed(L), reversed(R)):
            if symbol_L == symbol_R:
                if is_letter(symbol_L):
                    shared_letters_cnt = min(symbol_R.cnt, symbol_L.cnt)
                    symbol_L.cnt -= shared_letters_cnt
                    symbol_R.cnt -= shared_letters_cnt
                    if symbol_L.cnt == 0:
                        redundant_suffix_L += 1
                    if symbol_R.cnt == 0:
                        redundant_suffix_R += 1
                    if symbol_L.cnt + symbol_L.cnt > 0:
                        break
                else:
                    redundant_suffix_L += 1
                    redundant_suffix_R += 1
            else:
                break
        L = L[: len(L) - redundant_suffix_L]
        R = R[: len(R) - redundant_suffix_R]
        return L, R

    L = group_letters(L)
    R = group_letters(R)
    L, R = find_significant_infix(L, R)
    return L, R


def equivalent_nodes(node, letters):
    def name_change(symbol, trans):
        if(not is_letter(symbol)):
            return symbol
        return Letter(trans[symbol.nr], symbol.cnt)

    res = []
    for trans in combinations(letters, len(node.letters)):
        L = [name_change(symbol, trans) for symbol in node.L]
        R = [name_change(symbol, trans) for symbol in node.R]
        res.append(Node(L, R))
    return res
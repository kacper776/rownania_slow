from base import *
from copy import copy


def simplify_eq(L: list, R: list) -> tuple:
    def group_letters(side: list):
        new_side = []
        for symbol in side:
            if is_letter(symbol) and new_side and symbol == new_side[-1]:
                new_side[-1].cnt += symbol.cnt
            elif is_variable(symbol) or symbol.cnt > 0:
                new_side.append(symbol)
        return new_side

    def find_significant_infix(L: list, R: list) -> tuple:
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

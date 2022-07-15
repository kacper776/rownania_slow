from base import *
from diophantic_solver import *
from simplify_equation import *
from copy import copy, deepcopy


class Node(object):
    def __init__(self, L: list, R: list, 
                 letter_unwrap: dict, variable_subs: dict) -> None:
        self.L = L
        self.R = R
        self.letter_unwrap = letter_unwrap
        self.variable_subs = variable_subs

    def __eq__(self, other) -> bool:
        if len(self.L) != len(other.L) or len(self.R) != len(other.R):
            return False
        for l0, l1 in list(zip(self.L, other.L)):
            if l0 != l1:
                return False
            elif is_letter(l0) and l0.cnt != l1.cnt:
                return False
        for r0, r1 in list(zip(self.R, other.R)):
            if r0 != r1:
                return False
            elif is_letter(r0) and r0.cnt != r1.cnt:
                return False
        return True

    def __len__(self) -> int:
        return len(self.L) + len(self.R)

    def __hash__(self) -> int:
        rep_L, rep_R = representative_eq(self.L, self.R)
        return hash((tuple(rep_L), tuple(rep_R)))
    
    def __repr__(self) -> str:
        return f'{self.L} = {self.R}'


    def terminal(self) -> bool:
        # checks if node represents correct solution
        for substitution in self.variable_subs.values():
            if not substitution[0] and not substitution[1]:
                return False

        if all(map(is_variable, self.L + self.R)):
            left_side = reduce(lambda a, b: a + read_result(self.variable_subs[b.nr]), self.L, '')
            right_side = reduce(lambda a, b: a + read_result(self.variable_subs[b.nr]), self.R, '')
            return left_side == right_side

        return not self.L and not self.R
    
    def bad(self):
        if self.L and self.R:
            if is_letter(self.L[0]) and is_letter(self.R[0]) and self.L[0] != self.R[0]:
                return True
            if is_letter(self.L[-1]) and is_letter(self.R[-1]) and self.L[-1] != self.R[-1]:
                return True
        return False

    def children(self) -> list:
        def merge_blocks(node: Node, letter: Letter, vanishing_vars: set) -> list:
            # creates list of all nodes obtained by merging maximal letter 'letter' blocks
            def get_blocks(side: list, letter: Letter) -> list:
                # creates list of maximal blocks of letter
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

            def merge_solution_to_node(solution: ModelRef, letter: Letter,
                                       vanishing_vars: set, letter_unwrap: dict,
                                       variable_subs: dict) -> Node:
                # builds node for given blocks equalities solution
                def build_eq_side(side: list) -> list:
                    # builds one side of equation using given solution
                    result = []
                    for symbol in side:
                        if is_letter(symbol):
                            result.append(copy(symbol))
                        else:
                            pop_cnt_L = solution[Int(f'x_{2 * symbol.nr}')].as_long()
                            pop_cnt_R = solution[Int(f'x_{2 * symbol.nr + 1}')].as_long()
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

                def compress_letters(L: list, R: list, letter_unwrap: dict) -> None:
                    # compresses maximal blocks of same size to the same new letter
                    taken_nrs = {let.nr for let in L + R if is_letter(let)}
                    group_nrs = {}
                    free_nr = 0
                    for symbol in L + R:
                        if symbol == letter:
                            if symbol.cnt in group_nrs:
                                symbol.nr = group_nrs[symbol.cnt]
                            else:
                                while free_nr in taken_nrs:
                                    free_nr += 1
                                group_nrs[symbol.cnt] = free_nr
                                letter_unwrap[free_nr] = (symbol.cnt, letter_unwrap[symbol.nr])
                                symbol.nr = free_nr
                                free_nr += 1
                            symbol.cnt = 1

                new_L = build_eq_side(node.L)
                new_R = build_eq_side(node.R)
                new_L, new_R = simplify_eq(new_L, new_R)
                compress_letters(new_L, new_R, letter_unwrap)

                # update variables substitutions
                var_nrs = {var.nr for var in node.L + node.R if is_variable(var)}
                for nr in var_nrs:
                    pop_cnt_L = solution[Int(f'x_{2 * nr}')].as_long()
                    pop_cnt_R = solution[Int(f'x_{2 * nr + 1}')].as_long()
                    if pop_cnt_L > 0:
                        variable_subs[nr][0].append((pop_cnt_L, letter_unwrap[letter.nr]))
                    if pop_cnt_R > 0:
                        variable_subs[nr][1].append((pop_cnt_R, letter_unwrap[letter.nr]))

                return Node(new_L, new_R, letter_unwrap, variable_subs)

            blocks_L = get_blocks(node.L, letter)
            blocks_R = get_blocks(node.R, letter)
            X = {var.nr: f'x_{var.nr}' for block in blocks_L + blocks_R
                                       for var in block  
                                       if is_variable(var)}
            solutions = solve_block_eq(blocks_L, blocks_R, X, vanishing_vars)
            return [merge_solution_to_node(solution, letter, vanishing_vars,
                                           copy(node.letter_unwrap), deepcopy(node.variable_subs)) 
                    for solution in solutions]


        def merge_pair(node: Node, letter0: Letter, letter1: Letter, vanishing_vars: set) -> list:
            # creates list of nodes obtained by merging pair <letter0, letter1>
            def variables_pop(side: list, variable_nrs: set) -> list:
                # adds letters popped from variables to equation side
                result = []
                for symbol in side:
                    if is_variable(symbol):
                        if symbol.nr * 2 in variable_nrs:
                            result.append(copy(letter1))
                        if symbol not in vanishing_vars:
                            result.append(copy(symbol))
                        if symbol.nr * 2 + 1 in variable_nrs:
                            result.append(copy(letter0))
                    else:
                        result.append(symbol)
                return result

            def merge(side: list, result_letter: Letter) -> list:
                # in equation side merges neighbouring pairs of <letter0, letter1>
                # into given result_letter
                result = []
                i = 0
                while i < len(side) - 1:
                    if side[i] == letter0 and side[i + 1] == letter1:
                        if side[i].cnt > 1:
                            result.append(Letter(side[i].nr, side[i].cnt - 1))
                        result.append(copy(result_letter))
                        if side[i + 1].cnt > 1:
                            result.append(Letter(side[i + 1].nr, side[i + 1].cnt - 1))
                        i += 1
                    elif is_letter(side[i]) or side[i] not in vanishing_vars:
                        result.append(copy(side[i]))
                    i += 1
                if i == len(side) - 1:
                    result.append(copy(side[-1]))
                return result

            # find letter not in equation to be merge result letter
            result_letter_nr = 0
            taken_nrs = {let.nr for let in node.L + node.R if is_letter(let)}
            while result_letter_nr in taken_nrs:
                result_letter_nr += 1
            result_letter = Letter(result_letter_nr, 1)
            all_variable_nrs = {var.nr * 2 + 1 for var in node.L + node.R if is_variable(var)}\
                               | {var.nr * 2 + 1 for var in node.L + node.R if is_variable(var)}

            # for each possible set of variable's sides popping letters
            # do the letters pair merging
            result = []
            for variables_pop_nrs in powerset(all_variable_nrs):
                # only variables which pop letters can vanish
                if [var.nr for var in vanishing_vars
                           if var.nr * 2 not in variables_pop_nrs
                              and var.nr * 2 + 1 not in variables_pop_nrs]:
                    continue

                letter_unwrap = copy(node.letter_unwrap)
                variable_subs = deepcopy(node.variable_subs)
                letter_unwrap[result_letter_nr] = (0, (letter_unwrap[letter0.nr], letter_unwrap[letter1.nr]))
                for var_nr in variables_pop_nrs:
                    if (var_nr & 1) == 0:
                        variable_subs[var_nr / 2][0].append((1, letter_unwrap[letter1.nr]))
                    else:
                        variable_subs[(var_nr - 1) / 2][1].append((1, letter_unwrap[letter0.nr]))
                L = variables_pop(node.L, variables_pop_nrs)
                R = variables_pop(node.R, variables_pop_nrs)
                L = merge(L, result_letter)
                R = merge(R, result_letter)
                L, R = simplify_eq(L, R)
                result.append(Node(L, R, letter_unwrap, variable_subs))
            return result

        # for each possible set of variables dissapearing after merge
        # try merging every possible pair of letters
        # and maximum blocks of every possible letter
        all_variables = {var for var in self.L + self.R if is_variable(var)}
        all_letters = {Letter(let.nr, 1) for let in self.L + self.R if is_letter(let)}
        result = []
        for vanishing_vars in powerset(all_variables):
            for letter0 in all_letters:
                for letter1 in all_letters:
                    if letter0 != letter1:
                        result += merge_pair(self, letter0, letter1, vanishing_vars)
                result += merge_blocks(self, letter0, vanishing_vars)
        return filter(lambda node: not node.bad(), result)


def representative_eq(L: list, R: list) -> Node:
    # for given equation build represantative node of it
    def translate(side: list, letter_nr_trans: dict, free_nr: int):
        result = []
        for symbol in side:
            if is_variable(symbol):
                result.append(copy(symbol))
            else:
                if symbol.nr in letter_nr_trans:
                    result.append(Letter(letter_nr_trans[symbol.nr], symbol.cnt))
                else:
                    letter_nr_trans[free_nr] = symbol.nr
                    result.append(Letter(free_nr, symbol.cnt))
                    free_nr += 1
        return result, free_nr

    letter_nr_trans = {}
    rep_L, free_nr = translate(L, letter_nr_trans, 0)
    rep_R, _ = translate(R, letter_nr_trans, free_nr)
    return rep_L, rep_R


def read_result(result: tuple) -> str:
    # reads substitution for a variable
    def read_part(part: tuple) -> str:
        cnt, res = part
        if cnt == -1:
            return res
        if cnt == 0:
            return read_part(res[0]) + read_part(res[1])
        return cnt * read_part(res)
    return reduce(lambda a, b: a + b,
                  [read_part(part) for part in result[0]], '')\
           + reduce(lambda a, b: a + b,
                    [read_part(part) for part in reversed(result[1])], '')

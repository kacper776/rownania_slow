from itertools import combinations, chain


def powerset(set: set) -> chain:
    s = list(set)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class Variable(object):
    def __init__(self, nr: int) -> None:
        self.nr = nr

    def __repr__(self) -> str:
        return f'var_{self.nr}'

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.nr == other.nr
    
    def __hash__(self):
        return hash(self.nr)


class Letter(object):
    def __init__(self, nr: int, cnt: int) -> None:
        self.nr = nr
        self.cnt = cnt

    def __repr__(self) -> str:
        return f'{self.cnt}({self.nr})'

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.nr == other.nr

    def __hash__(self) -> int:
        return hash((self.nr, self.cnt))


def is_letter(symbol) -> bool:
    return isinstance(symbol, Letter)


def is_variable(symbol) -> bool:
    return isinstance(symbol, Variable)
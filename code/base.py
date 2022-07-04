class Variable(object):
    def __init__(self, nr):
        self.nr = nr

    def __repr__(self):
        return chr(self.nr)

    def __eq__(self, other):
        return type(self) == type(other) and self.nr == other.nr
    
    def __hash__(self):
        return hash(self.nr)


class Letter(object):
    def __init__(self, nr, cnt):
        self.nr = nr
        self.cnt = cnt

    def __repr__(self):
        return self.cnt * chr(self.nr)

    def __eq__(self, other):
        return type(self) == type(other) and self.nr == other.nr

    def __hash__(self):
        return hash(self.nr)


def is_letter(symbol):
    return isinstance(symbol, Letter)


def is_variable(symbol):
    return isinstance(symbol, Variable)
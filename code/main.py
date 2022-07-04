from base import *
from graph import *
from curses.ascii import isupper


if __name__ == "__main__":
    equation = input()
    sides = equation.split('=')
    assert(len(sides) == 2)
    sides[0] = ''.join(sides[0].split())
    sides[1] = ''.join(sides[1].split())
    L = []
    for symbol in sides[0]:
        if isupper(symbol):
            L.append(Variable(ord(symbol)))
        else:
            L.append(Letter(ord(symbol), 1))
    R = []
    for symbol in sides[1]:
        if isupper(symbol):
            R.append(Variable(ord(symbol)))
        else:
            R.append(Letter(ord(symbol), 1))
    start = Node(L, R)

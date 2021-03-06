from base import *
from graph import *
from searching import *
from curses.ascii import isupper


if __name__ == "__main__":
    # parse input
    equation = input()
    sides = equation.split('=')
    if len(sides) != 2:
        print('Incorrect equation')
        exit(0)
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

    # no variables = nothing to do
    if not any(map(is_variable, L)) and not any(map(is_variable, R)):
        print('No variables in equation')
        exit(0)

    # no letters = equation is trivial
    if not any(map(is_letter, L)) and not any(map(is_letter, R)):
        print('No letters in equation')
        exit(0)

    # create starting node
    letter_unwrap = {let.nr: (-1, chr(let.nr))
                     for let in L + R if is_letter(let)}
    variable_subs = {var.nr: ([], [])
                     for var in L + R if is_variable(var)}
    L, R = simplify_eq(L, R)
    start = Node(L, R, letter_unwrap, variable_subs)

    # search the graph
    start_len = len(start)
    max_len = 8 * start_len * start_len + start_len
    result = bfs(start, max_len)
    if not result:
        print("No result found")
    else:
        print('Result:')
        for var_nr in variable_subs.keys():
            print(f'{chr(var_nr)} = {read_result(result[var_nr])}')

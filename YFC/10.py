import sys
from itertools import product

inp = sys.stdin.read()
symbols = set(inp)
print(inp, file=sys.stderr)
trash = ['+', '-', '=', ' ', '\n']
for t in trash:
    symbols.discard(t)
counter = [0 for i in range(len(symbols))]
for counter in product(range(10), repeat=len(symbols)):
    string = inp.replace('=', '==')
    if len(set(counter)) == len(counter):
        for char, val in zip(symbols, counter):
            string = string.replace(char, str(val))
        try:
            if eval(string):
                print(string.replace('==', '='))
                break
        except SyntaxError:
            a = 5


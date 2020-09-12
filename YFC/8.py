import sys
import random
from copy import deepcopy
from itertools import product
from collections import defaultdict
COOL, MAYBE, ERROR = 0, 1, 2


def small_check(nine_numbers):
    if sorted(nine_numbers) == list(str(i) for i in range(1, 10)):
        return COOL
    if nine_numbers.count('0') - 1 + len(set(nine_numbers)) == 9:
        return MAYBE
    return ERROR

def check(sudoku):
    status = COOL
    for i in range(9):
        status = max(status, small_check([sudoku[i][j] for j in range(9)]))
        status = max(status, small_check([sudoku[j][i] for j in range(9)]))
    for s_i in range(0, 7, 3):
        for s_j in range(0, 7, 3):
            block = [sudoku[s_i + i][s_j + j]
                     for i in range(3) for j in range(3)]
            status = max(status, small_check(block))
    return status

def calc_variants(condition):
    true_variants = True
    while True:
        true_variants = False
        variants = deepcopy(condition)
        for x, y in product(range(9), repeat=2):
            if condition[x][y] == '0':
                cands = set(str(i) for i in range(1, 10))
                for i in range(9):
                    cands.discard(condition[x][i])
                    cands.discard(condition[i][y])
                variants[x][y] = cands
            else:
                variants[x][y] = None
        for x, y, in product(range(0, 7, 3), repeat=2):
            banned = set()
            for i, j in product(range(3), repeat=2):
                banned.add(condition[x+i][y+j])
            for i, j in product(range(3), repeat=2):
                if variants[x+i][y+j] != None:
                    variants[x+i][y+j] -= banned
                    if len(variants[x+i][y+j]) == 1:
                        condition[x+i][y+j] = variants[x+i][y+j].pop()
                        variants[x+i][y+j] = None
                        print("AAA", x+i, y+j, condition[x+i][y+j])
                        true_variants = True
        if not true_variants:
            return variants

easy = """070900001
000250040
500000807
000000005
908060300
005308002
000000090
096040000
004100003"""
hard ="""812000000
943600000
675090200
154007000
000045700
000100030
001000068
008500010
090000400"""
condition = [list(row) for row in hard.split("\n")]

while check(condition) != COOL:
    variants = calc_variants(condition)
    #Is it working? 
    for i in range(9):
        row = defaultdict(lambda: 0)
        for j in range(9):
            if variants[i][j] != None:
                for v in variants[i][j]:
                    row[v] += 1
        for val, cnt in row.items():
            if cnt == 1:
                for j in range(9):
                    if variants[i][j] != None and val in variants[i][j]:
                        condition[i][j] = val
                        print("XXX", i, j, variants[i][j])
                        variants[i][j] = None
                        break
    variants = calc_variants(condition)
    for i in range(9):
        col = defaultdict(lambda: 0)
        for j in range(9):
            if variants[j][i] != None:
                for v in variants[j][i]:
                    col[v] += 1
        for val, cnt in col.items():
            if cnt == 1:
                for j in range(9):
                    if variants[j][i] != None and val in variants[j][i]:
                        condition[j][i] = val
                        print("YYY", j, i, variants[j][i])
                        variants[j][i] = None
                        break
    variants = calc_variants(condition)
    for x, y, in product(range(0, 7, 3), repeat=2):
        sqr = defaultdict(lambda: 0)
        for i, j in product(range(3), repeat=2):
            if variants[x+i][y+j] != None:
                for v in variants[x+i][y+j]:
                    sqr[v] += 1
        for val, cnt in sqr.items():
            if cnt == 1:
                for i, j in product(range(3), repeat=2):
                    if variants[x+i][y+j] != None and val in variants[x+i][y+j]:
                        condition[x+i][y+j] = val
                        print("SSS", x+i, y+j, variants[x+i][y+j])
                        variants[x+i][y+j] = None
                        break
    if check(condition) == ERROR:
        print("ERROR")
        break
for row in condition:
    print(row)


import sys
import random
from copy import deepcopy
COOL, MAYBE, ERROR = 0, 1, 2


def small_check(nine_numbers):
    if len(set(nine_numbers)) == len(nine_numbers):

    store = set()
    is_cool = True
    for value in nine_numbers:
        if value == '0':
            is_cool = False
        else:
            if value in store:
                return ERROR
            else:
                store.add(value)
    return COOL if is_cool else MAYBE


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


condition = [list(row) for row in sys.stdin.read().split("\n")]
while True:
    sudoku = deepcopy(condition)
    for _ in range(15):
        cands = []
        for y in range(9):
            for x in range(9):
                if sudoku[x][y] == '0':
                    cands.append((x, y))
        random.shuffle(cands)
        bad_places = []
        for cand in cands:
            all_right = False
            for value in range(1, 10):
                sudoku[cand[0]][cand[1]] = str(value)
                if check(sudoku) < ERROR:
                    all_right = True
                    break
            if not all_right:
                sudoku[cand[0]][cand[1]] = '0'
                bad_places.append(cand)
        if len(bad_places) > 3:
            for x, y in bad_places:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if x+i in range(0, 9) and y+j in range(0, 9) and condition[x+i][y+j] == '0':
                            sudoku[x+i][y+j] = '0'
        else:
            print("FINDED")
            for row in sudoku:
                print("".join(row))
            exit(1)

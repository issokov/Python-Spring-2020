import sys
from random import choice, seed
from copy import deepcopy
from itertools import product
from collections import defaultdict

seed(2)

class Sudoku:

    COOL, MAYBE, ERROR = 0, 1, 2

    def __init__(self, field):
        self.field = field
        self.variants = self.create_variants()

    def create_variants(self):
        variants = deepcopy(self.field)
        for x, y in product(range(9), repeat=2):
            if self.field[x][y] == '0':
                candidates = set(str(i) for i in range(1, 10))
                for i in range(9):
                    candidates.discard(self.field[x][i])
                    candidates.discard(self.field[i][y])
                variants[x][y] = candidates
            else:
                variants[x][y] = None
        for x, y, in product(range(0, 7, 3), repeat=2):
            banned = set()
            for i, j in product(range(3), repeat=2):
                banned.add(self.field[x + i][y + j])
            for i, j in product(range(3), repeat=2):
                if variants[x + i][y + j]:
                    variants[x + i][y + j] -= banned
        return variants

    def __str__(self):
        return "\n".join("".join(self.field[i])
                         for i in range(len(self.field)))

    def __setitem__(self, key, value):
        x, y = key
        self.field[x][y] = value
        self.variants[x][y] = None
        x_corner, y_corner = (x // 3) * 3, (y // 3) * 3
        for _x, _y in product(range(3), repeat=2):
            if self.variants[x_corner + _x][y_corner + _y]:
                self.variants[x_corner + _x][y_corner + _y].discard(value)
        for i in range(9):
            if self.variants[x][i]:
                self.variants[x][i].discard(value)
            if self.variants[i][y]:
                self.variants[i][y].discard(value)

    def __getitem__(self, key):
        return self.field[key[0]][key[1]]

    def check(self):

        def is_1_9(nine_numbers):
            store = set()
            is_cool = True
            for value in nine_numbers:
                if value == '0':
                    is_cool = False
                else:
                    if value in store:
                        return self.ERROR
                    else:
                        store.add(value)
            return self.COOL if is_cool else self.MAYBE

        status = self.COOL
        for i in range(9):
            status = max(status, is_1_9([self.field[i][j] for j in range(9)]))
            status = max(status, is_1_9([self.field[j][i] for j in range(9)]))
        for square_x in range(0, 7, 3):
            for square_y in range(0, 7, 3):
                block = [self.field[square_x + x][square_y + y]
                         for x in range(3) for y in range(3)]
                status = max(status, is_1_9(block))
        return status


class SudokuSolver:

    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.PRINT = False

    def try_fill_trivial(self, sudoku=None):
        sudoku = sudoku if sudoku else self.sudoku
        all_filled, has_loners = False, False
        while not all_filled:
            all_filled = True
            field, variants = sudoku.field, sudoku.variants
            for x, y in product(range(9), repeat=2):
                if variants[x][y] and len(variants[x][y]) == 1:
                    sudoku[(x, y)] = variants[x][y].pop()
                    has_loners = True
                    all_filled = False
                    if self.PRINT:
                        print("ALONE ", (x, y), field[x][y])
        if self.PRINT and has_loners:
            print(sudoku)
        return has_loners

    def try_fill_singles(self, sudoku=None):
        sudoku = sudoku if sudoku else self.sudoku
        all_filled, has_single = False, False
        while not all_filled:
            all_filled = True
            for x in range(9):
                row_count = defaultdict(lambda: 0)
                col_count = defaultdict(lambda: 0)
                for y in range(9):
                    if sudoku.variants[x][y] is not None:
                        for variant in sudoku.variants[x][y]:
                            row_count[variant] += 1
                    if sudoku.variants[y][x] is not None:
                        for variant in sudoku.variants[y][x]:
                            col_count[variant] += 1
                for candidate, count in row_count.items():
                    if count == 1:
                        for y in range(9):
                            if sudoku.variants[x][y]\
                                    and candidate in sudoku.variants[x][y]:
                                sudoku[(x, y)] = candidate
                                if self.PRINT:
                                    print("HORZ-SINGLED: ",
                                          (x, y), sudoku[(x, y)])
                                has_single = True
                                all_filled = False
                for candidate, count in col_count.items():
                    if count == 1:
                        for y in range(9):
                            if sudoku.variants[y][x]\
                                    and candidate in sudoku.variants[y][x]:
                                sudoku[(y, x)] = candidate
                                if self.PRINT:
                                    print("VERT-SINGLED: ",
                                          (y, x), sudoku[(y, x)])
                                has_single = True
                                all_filled = False

        if self.PRINT and has_single:
            print(sudoku)
        return has_single

    def try_logic_solve(self, sudoku=None):
        sudoku = sudoku if sudoku else self.sudoku
        solving = True
        while solving:
            solving = False
            solving = max(solving, self.try_fill_trivial(sudoku))
            solving = max(solving, self.try_fill_singles(sudoku))

    def try_random_step(self, sudoku=None):
        sudoku = sudoku if sudoku else self.sudoku
        possible_steps = []
        for x, y in product(range(9), repeat=2):
            if sudoku.variants[x][y] is not None:
                if sudoku.variants[x][y] == set():
                    if self.PRINT:
                        print("NO WAY: ", x, y)
                    return False
                possible_steps.append(((x, y), sudoku.variants[x][y]))
        if not possible_steps:
            return False
        key, candidates = min(possible_steps, key=lambda p: len(p[1]))
        sudoku[key] = choice(list(candidates))
        if self.PRINT:
            print("RANDOM STEP: ", key, sudoku[key])
        return True

    def solve(self):
        counter = 1
        copy_sudoku = deepcopy(self.sudoku)
        while True:
            self.try_logic_solve(copy_sudoku)
            if copy_sudoku.check() == copy_sudoku.COOL:
                return copy_sudoku
            if not self.try_random_step(copy_sudoku):
                counter += 1
                copy_sudoku = deepcopy(self.sudoku)
            if copy_sudoku.check() == copy_sudoku.ERROR:
                raise Exception("Algorithm is broken: sudoku is wrong")


sudoku = Sudoku([list(row) for row in sys.stdin.read().split("\n")])
solver = SudokuSolver(sudoku)
print(solver.solve())
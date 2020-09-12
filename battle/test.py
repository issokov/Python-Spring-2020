import numpy as np
from subprocess import Popen, PIPE, TimeoutExpired
from itertools import product
from time import time

init_field = "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n" \
             "0000000000\n"

field = init_field


def get_steps(data, me, dead_me, enemy):
    possibles = []
    looks = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    checks = np.zeros(shape=(10, 10), dtype=bool)
    for x, y in product(range(10), range(10)):
        if checks[x, y] == 0 and data[x, y] == me:
            checks[x, y] = 1
            queue = [(x, y)]
            while queue:
                cx, cy = queue.pop(0)
                for sx, sy in looks:
                    nx, ny = cx + sx, cy + sy
                    if 0 <= nx < 10 and 0 <= ny < 10 and (checks[nx, ny] == 0):
                        checks[nx, ny] = 1
                        value = data[nx, ny]
                        if value == dead_me or value == me:
                            queue.append((nx, ny))
                        elif value == 0 or value == enemy:
                            possibles.append((nx, ny))
    return possibles


def steps_by_player(field, player):
    data = np.empty(shape=(10, 10), dtype=int)
    for i, line in enumerate(field.split("\n")[:10]):
        data[i] = list(line)
    if data[9, 0] == 0 or data[0, 9] == 0:
        return [(9, 0), (9, 1), (8, 0)] if player=='1' else [(0, 8), (0, 9), (1, 9)]
    me, enemy, dead_me = 1, 2, 3
    if player == '2':
        me, enemy, dead_me = 2, 1, 4
    return get_steps(data, me, dead_me, enemy)


def make_steps(field, player, steps):
    data = np.empty(shape=(10, 10), dtype=int)
    for i, line in enumerate(field.split("\n")[:10]):
        data[i] = list(line)
    for x, y in steps:
        data[x, y] = (player if data[x][y] == '0' else ('3' if player == '1' else '4'))
    return '\n'.join(''.join(str(cell) for cell in row) for row in data) + '\n'


def calc_winner(field):
    first, second = 0, 0
    for v in field:
        if v == '1' or v == '4':
            first += 1
        if v == '2' or v == '3':
            second += 1
    if first > second:
        return '1'
    elif first < second:
        return '2'
    return '0'


player = '2'
no_steps_player = None
for _ in range(100):
    player = '2' if player == '1' else '1'
    steps = steps_by_player(field, player)
    if len(steps) < 3:
        field = make_steps(field, player, steps)
        if len(steps) == 0 and no_steps_player != player and no_steps_player is not None:
            print("GAME OVER")
            print("WINNER:", calc_winner(field))
            exit(0)
        no_steps_player = player
        print(f"Player {player} can't make steps")
    else:
        inp = field + player
        print(f"INPUT:\n{inp}")
        start = time()
        process = Popen(["python3 main.py"], stdin=PIPE, stdout=PIPE, shell=True)
        try:
            (output, err) = process.communicate(input=bytes(inp.encode('utf-8')), timeout=1.5)
            print("TIME: ", time() - start)
            field = output.decode('utf-8')
            print(f"OUTPUT:\n{field}")
        except TimeoutExpired:
            print('Timeout expired: ', time() - start)
            print("Winner: ", '2' if player == '1' else '1')
            exit(0)
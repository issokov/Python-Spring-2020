import argparse
import numpy as np

from itertools import product
from random import sample, seed
from time import time
# seed(1)


class Game:
    max_steps = 3
    field_size = (10, 10)
    me, enemy, dead_me, dead_enemy = 1, 2, 3, 4

    def __init__(self):
        self.start = time()
        self.data = np.empty(shape=self.field_size, dtype=int)
        for line in range(self.field_size[1]):
            self.data[line] = list(input())
        if int(input()) == 2:
            self.me, self.enemy = 2, 1
            self.dead_me, self.dead_enemy = 4, 3
        self.init_pos = (self.field_size[0] - 1, 0) if self.me == 1 else (0, self.field_size[1] - 1)
        self.rest_steps = self.max_steps
        if self.data[self.init_pos] == 0:
            self.data[self.init_pos] = self.me
            self.rest_steps -= 1

    def get_possible_steps(self, me, dead_me, enemy):
        possibles = []
        looks = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        checks = np.zeros(self.field_size)
        for x, y in product(range(self.field_size[0]), range(self.field_size[1])):
            if checks[x, y] == 0 and self.data[x, y] == me:
                checks[x, y] = 1
                queue = [(x, y)]
                while queue:
                    cx, cy = queue.pop(0)
                    for sx, sy in looks:
                        nx, ny = cx + sx, cy + sy
                        if 0 <= nx < self.field_size[0] and 0 <= ny < self.field_size[1] and (checks[nx, ny] == 0):
                            checks[nx, ny] = 1
                            value = self.data[nx, ny]
                            if value == dead_me or value == me:
                                queue.append((nx, ny))
                            elif value == 0 or value == enemy:
                                possibles.append((nx, ny))
        return possibles
    
    def get_step(self, possibles):
        if len(possibles) >= self.rest_steps:
            return sample(possibles, k=self.rest_steps)
        return []

    def step_stats(self, step):
        story = []
        for x, y in step:
            story.append((x, y, self.data[x, y]))
            self.data[x, y] = self.me if self.data[x, y] == 0 else self.dead_enemy
        stats = len(self.get_possible_steps(self.enemy, self.dead_enemy, self.me))
        for x, y, val in reversed(story):
            self.data[x, y] = val
        return stats

    def run(self):
        my_possibles = self.get_possible_steps(self.me, self.dead_me, self.enemy)
        if my_possibles:
            optimal = self.get_step(my_possibles)
            min_enemy_stats = self.step_stats(optimal)
            while time() - self.start < 0.4:
                step = self.get_step(my_possibles)
                stats = self.step_stats(step)
                if stats < min_enemy_stats:
                    min_enemy_stats = stats
                    optimal = step
            for x, y in optimal:
                self.data[x, y] = self.me if self.data[x, y] == 0 else self.dead_enemy
        print('\n'.join(''.join(str(cell) for cell in row) for row in self.data))


parser = argparse.ArgumentParser()
parser.add_argument('--name', dest='is_name', action='store_const', const=True, default=False)
args = parser.parse_args()
if args.is_name:
    print("Antonio Marghereeeiti")
else:
    Game().run()

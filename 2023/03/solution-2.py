import sys
import itertools as it
import collections as cl
from dataclasses import dataclass

from utils import Position, Grid

@dataclass
class Gear:
    part_1: int
    part_2: int

    def __int__(self):
        return self.part_1 * self.part_2

class MyGrid(Grid):
    def __init__(self, fp):
        grid = [ list(x.strip()) for x in fp ]
        super().__init__(grid)

    def stars(self):
        for (r, row) in enumerate(self):
            for (c, cell) in enumerate(row):
                if cell == '*':
                    yield Position(r, c)

    def digits(self, at):
        for i in at.around():
            c = self.grid[i.row][i.col]
            if c.isdigit():
                yield i

    def carve_and_fill(self, at):
        char = self.grid[at.row][at.col]
        if not char.isdigit():
            raise TypeError()

        word = cl.deque()
        word.extendleft(self.trample(at, range(at.col, -1, -1)))
        word.extend(self.trample(at, range(at.col + 1, self.shape.col)))

        return int(''.join(word))

    def trample(self, start, direction):
        row = self.grid[start.row]
        for c in direction:
            char = row[c]
            if not char.isdigit():
                break
            yield char
            row[c] = ''

def parts(grid):
    neighbors = []
    for s in grid.stars():
        for d in grid.digits(s):
            try:
                n = grid.carve_and_fill(d)
            except TypeError:
                continue
            neighbors.append(n)
        if len(neighbors) == 2:
            yield Gear(*neighbors)
        neighbors.clear()

if __name__ == '__main__':
    grid = MyGrid(sys.stdin)
    print(sum(map(int, parts(grid))))

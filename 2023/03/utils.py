import itertools as it
from dataclasses import dataclass

@dataclass
class Position:
    row: int
    col: int

    def around(self):
        for (r, c) in it.product((-1, 0, 1), repeat=2):
            if r or c:
                yield type(self)(self.row + r, self.col + c)

@dataclass
class Digit:
    pos: Position
    digit: str

class Part(list):
    def __int__(self):
        return int(''.join(x.digit for x in self))

    def push(self, x, y, value):
        self.append(Digit(Position(x, y), value))

class Grid:
    def __init__(self, grid, shape=None):
        self.grid = grid
        if shape is None:
            args = map(len, (self.grid, self.grid[0]))
            self.shape = Position(*args)
        else:
            self.shape = shape

    def __iter__(self):
        yield from self.grid

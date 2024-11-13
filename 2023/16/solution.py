import sys
import logging
import functools as ft
from dataclasses import dataclass
from argparse import ArgumentParser

#
#
#
@dataclass(frozen=True)
class Coordinate:
    row: int
    col: int

    def __neg__(self):
        return type(self)(-self.row, -self.col)

    def __invert__(self):
        return type(self)(self.col, self.row)

    def __add__(self, other):
        return type(self)(self.row + other.row, self.col + other.col)

#
#
#
class Action:
    def __init__(self, value, magnitude=0):
        self.value = value
        self.magnitude = magnitude

    def __str__(self):
        return self.value

    def __int__(self):
        return self.magnitude

    def __call__(self, trajectory):
        yield trajectory

class EmptySpace(Action):
    def __init__(self):
        super().__init__('.')

class Energized(Action):
    def	__init__(self):
        super().__init__('#', 1)

class UpwardMirror(Action):
    def __init__(self):
        super().__init__('/')

    def __call__(self, trajectory):
        yield -~trajectory

class DownwardMirror(Action):
    def __init__(self):
        super().__init__('\\')

    def __call__(self, trajectory):
        yield ~trajectory

class Splitter(Action):
    def __call__(self, trajectory):
        if self.act(trajectory):
            iterable = map(self.split, (-1, 1))
        else:
            iterable = super().__call__(trajectory)

        yield from iterable

    def act(self, trajectory):
        raise NotImplementedError()

    def split(self, value):
        raise NotImplementedError()

class VerticalSplitter(Splitter):
    def __init__(self):
        super().__init__('|')

    def act(self, trajectory):
        return not trajectory.row and trajectory.col

    def split(self, value):
        return Coordinate(value, 0)

class HorizontalSplitter(Splitter):
    def __init__(self):
        super().__init__('-')

    def act(self, trajectory):
        return trajectory.row and not trajectory.col

    def split(self, value):
        return Coordinate(0, value)

#
#
#
class Contraption(dict):
    @ft.cached_property
    def shape(self):
        (rows, cols) = (0, 0)
        for p in self:
            if p.row > rows:
                rows = p.row + 1
            if p.col > cols:
                cols = p.col + 1

        return Coordinate(rows, cols)

    def __str__(self):
        dim = self.shape
        board = [ [None] * dim.col for _ in range(dim.row) ]
        for (k, v) in self.items():
            board[k.row][k.col] = str(v)

        return '\n'.join(map(''.join, board))

    def __int__(self):
        return sum(map(int, self.values()))

    def _explore(self, position, trajectory):
        if position in self:
            action = self[position]
            self[position] = Energized()
            for a in action(trajectory):
                self._explore(position + a, a)

    def explore(self):
        return self._explore(Coordinate(0, 0), Coordinate(0, 1))

def scanf(fp):
    dtypes = {
        '.':  EmptySpace(),
        '/':  UpwardMirror(),
        '\\': DownwardMirror(),
        '|':  VerticalSplitter(),
        '-':  HorizontalSplitter(),
    }

    for (r, y) in enumerate(fp):
        for (c, cell) in enumerate(y.strip()):
            pos = Coordinate(r, c)
            action = dtypes[cell]
            yield (pos, action)

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    contraption = Contraption(dict(scanf(sys.stdin)))
    contraption.explore()
    print(contraption)
    print(int(contraption))

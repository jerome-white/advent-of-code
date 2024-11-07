import os
import sys
import logging
import functools as ft
import itertools as it
from dataclasses import dataclass
from argparse import ArgumentParser

#
#
#
@dataclass
class Position:
    row: int
    col: int

#
#
#
class Tilter:
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols

    def __str__(self):
        return type(self).__name__

    def __iter__(self):
        raise NotImplementedError()

    def walk(self, position):
        raise NotImplementedError()

class North(Tilter):
    def	__iter__(self):
        for c in range(self.ncols):
            for r in range(self.nrows):
                yield Position(r, c)

    def walk(self, position):
        for r in range(position.row + 1, self.nrows):
            yield Position(r, position.col)

class South(Tilter):
    def __iter__(self):
        nrows = self.nrows - 1
        for c in range(self.ncols - 1, -1, -1):
            for r in range(nrows, -1, -1):
                yield Position(r, c)

    def walk(self, position):
        for r in range(position.row - 1, -1, -1):
            yield Position(r, position.col)

class East(Tilter):
    def __iter__(self):
        ncols = self.ncols - 1
        for r in range(self.nrows - 1, -1, -1):
            for c in range(ncols, -1, -1):
                yield Position(r, c)

    def walk(self, position):
        for c in range(position.col - 1, -1, -1):
            yield Position(position.row, c)

class West(Tilter):
    def __iter__(self):
        for r in range(self.nrows):
            for c in range(self.ncols):
                yield Position(r, c)

    def walk(self, position):
        for c in range(position.col + 1, self.ncols):
            yield Position(position.row, c)

#
#
#
class Panel:
    _empty = '.'
    _round = 'O'

    @ft.cached_property
    def shape(self):
        return tuple(map(len, (self.panel, self.panel[0])))

    def __init__(self, pstring):
        self.panel = list(map(list, pstring.splitlines()))

    def __repr__(self):
        return ','.join(map(''.join, self.panel))

    def __getitem__(self, key):
        return self.panel[key.row][key.col]

    def __setitem__(self, key, value):
        self.panel[key.row][key.col] = value

    def tilt(self, direction):
        for pos in direction:
            if self[pos] == self._empty:
                for p in direction.walk(pos):
                    value = self[p]
                    if value != self._empty:
                        if value == self._round:
                            (self[pos], self[p]) = (self[p], self[pos])
                        break

    def spin(self, directions):
        for d in directions:
            self.tilt(d)

#
#
#
class Spinner:
    def __init__(self, panel, cycles, *args):
        self.cycles = cycles
        self.directions = [ x(*panel.shape) for x in args ]

    def __iter__(self):
        for i in range(self.cycles, 0, -1):
            yield (i, self.directions)

class SingleSpinner(Spinner):
    def __init__(self, panel):
        super().__init__(panel, 1, North)

class RepeatedSpinner(Spinner):
    def __init__(self, panel):
        directions = (
            North,
            West,
            South,
            East,
        )
        super().__init__(panel, int(1e9), *directions)

#
#
#

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    MySpinner = SingleSpinner if args.version == 1 else RepeatedSpinner

    panel = Panel(sys.stdin.read())
    spinner = MySpinner(panel)
    try:
        for (i, s) in spinner:
            panel.spin(s)
            print(i - 1, panel)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())

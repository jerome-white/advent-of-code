import os
import sys
import logging
import functools as ft
import itertools as it
import collections as cl
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

    def walk(self, row, col):
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
    @ft.cached_property
    def shape(self):
        return tuple(map(len, (self.panel, self.panel[0])))

    def __init__(self, pstring):
        self.panel = list(map(list, pstring.splitlines()))

    def __repr__(self):
        return ','.join(map(''.join, self.panel))

    def get(self, position):
        return self.panel[position.row][position.col]

    def swap(self, l, r):
        (self.panel[l.row][l.col], self.panel[r.row][r.col]) = (
            self.panel[r.row][r.col],
            self.panel[l.row][l.col],
        )

    def is_item(self, pos, item):
        return self.panel[pos.row][pos.col] == item

    def is_round(self, pos):
        return self.is_item(pos, 'O')

    def is_cube(self, pos):
        return self.is_item(pos, '#')

    def is_empty(self, pos):
        return self.is_item(pos, '.')

#
#
#
class Spinner:
    def __init__(self, panel, cycles, *args):
        self.panel = panel
        self.cycles = cycles
        self.directions = [ x(*panel.shape) for x in args ]

    def __iter__(self):
        for _ in self.cycles:
            print(self.panel)
            yield from self.directions

class SingleSpinner(Spinner):
    def __init__(self, panel):
        super().__init__(panel, range(1), North)

class RepeatedSpinner(Spinner):
    def __init__(self, panel):
        directions = (
            North,
            West,
            South,
            East,
        )
        super().__init__(panel, it.count(), *directions)

#
#
#
def spin(panel, spinner):
    for tilt in spinner:
        for pos in tilt:
            if panel.is_empty(pos):
                for p in tilt.walk(pos):
                    if not panel.is_empty(p):
                        if panel.is_round(p):
                            panel.swap(pos, p)
                        break

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    MySpinner = SingleSpinner if args.version == 1 else RepeatedSpinner

    panel = Panel(sys.stdin.read())
    spinner = MySpinner(panel)
    try:
        spin(panel, spinner)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())

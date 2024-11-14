import sys
import logging
import itertools as it
import functools as ft
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass, astuple

#
#
#
@dataclass(frozen=True)
class Coordinate:
    row: int
    col: int

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __add__(self, other):
        return type(self)(self.row + other.row, self.col + other.col)

class History:
    def __init__(self, maxlen=None, past=None):
        self.history = past or cl.deque(maxlen=maxlen)

    def __iter__(self):
        yield from zip(self.history, it.islice(self.history, 1, None))

    def __bool__(self):
        return len(self.history) < self.history.maxlen or not self.all_equal()

    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    def all_equal(self):
        g = it.groupby(self.history)
        return next(g, True) and not next(g, False)

    def __add__(self, other):
        history = self.history.copy()
        history.append(other)

        return type(self)(past=history)

class Board:
    @ft.cached_property
    def shape(self):
        return tuple(len(x) for x in (self.board, self.board[0]))

    def __init__(self, board):
        self.board = board
        self.end = Coordinate(*(x - 1 for x in self.shape))

    def __getitem__(self, key):
        return self.board[key.row][key.col]

    def __contains__(self, item):
        return all(0 <= x < y for (x, y) in zip(astuple(item), self.shape))

    def target(self, coord):
        return self.end == coord

    def to_strings(self, special=None):
        if special is None:
            special = set()

        for (r, row) in enumerate(self.board):
            record = []
            for (c, cell) in enumerate(row):
                coord = Coordinate(r, c)
                rec = ' ' if coord in special else str(cell)
                record.append(rec)
            yield ''.join(record)

class MachinePartsFactory:
    _navigation = (
        (-1, 0), # up
        ( 0, 1), # right
        ( 1, 0), # down
    )

    def __init__(self, board, history):
        self.board = board
        self.history = history

        self.navigation = tuple(it.starmap(Coordinate, self._navigation))
        self.lower = None
        self.visited = set()

    def __int__(self):
        return self.lower

    def __call__(self):
        self.visited.clear()
        return self.walk(Coordinate(0, 0), self.history, 0)

    def walk(self, coord, path, heat):
        if coord not in self.board or coord in self.visited or not path:
            return

        heat += self.board[coord]
        if self.lower is not None and heat >= self.lower:
            return

        if self.board.target(coord):
            self.lower = heat
            if logging.getLogger().isEnabledFor(logging.WARNING):
                for s in self.board.to_strings(self.visited):
                    logging.warning(s)
            logging.critical(self.lower)
        else:
            self.visited.add(coord)
            for c in self.navigation:
                self.walk(coord + c, path + c, heat)
            self.visited.discard(coord)

def scanf(fp):
    for row in fp:
        yield list(map(int, row.strip()))

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--max-direction', type=int, default=3)
    # arguments.add_argument('--recursive-limit', type=int)
    args = arguments.parse_args()

    board = Board(list(scanf(sys.stdin)))
    history = History(args.max_direction)

    machine = MachinePartsFactory(board, history)
    machine()
    print(int(machine))

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
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    @staticmethod
    def all_equal(iterable):
        g = it.groupby(iterable)
        return next(g, True) and not next(g, False)

    def __init__(self, maxlen=None, history=None):
        assert bool(maxlen) ^ bool(history)
        self.history = history or cl.deque(maxlen=maxlen)

    def __bool__(self):
        n = len(self.history)
        if n < self.history.maxlen:
            return True

        n -= self.history.maxlen
        return not self.all_equal(it.islice(self.history, n, None))

    def __add__(self, other):
        history = self.history.copy()
        history.append(other)

        return type(self)(history=history)

    def peek(self):
        return self.history[-1] if self.history else None

class BoardNavigator:
    _navigation = {
        '^': (-1,  0), # up
        'v': ( 1,  0), # down
        '<': ( 0, -1), # left
        '>': ( 0,  1), # right
    }

    def __init__(self, missing='*'):
        self.missing = missing
        self.navigation = {
            Coordinate(*y): x for (x, y) in self._navigation.items()
        }

    def __iter__(self):
        yield from self.navigation

    def to_string(self, coord):
        if coord not in self.navigation:
            return self.missing

        return self.navigation[coord]

class Board:
    @ft.cached_property
    def shape(self):
        return tuple(len(x) for x in (self.board, self.board[0]))

    @ft.cached_property
    def start(self):
        return self.board[0][0]

    def __init__(self, board):
        self.board = board
        self.navigation = BoardNavigator()
        self.end = Coordinate(*(x - 1 for x in self.shape))

    def __iter__(self):
        yield from self.navigation

    def __getitem__(self, key):
        return self.board[key.row][key.col]

    def __contains__(self, item):
        return all(0 <= x < y for (x, y) in zip(astuple(item), self.shape))

    def target(self, coord):
        return self.end == coord

    def to_strings(self, special=None):
        if special is None:
            special = {}

        for (r, row) in enumerate(self.board):
            record = []
            for (c, cell) in enumerate(row):
                coord = Coordinate(r, c)
                if coord in special:
                    rec = self.navigation.to_string(special.get(coord))
                else:
                    rec = str(cell)
                record.append(rec)
            yield ''.join(record)

class MachinePartsFactory:
    def __init__(self, board, history):
        self.board = board
        self.history = history

        self.lower = None
        self.visited = {}

    def __int__(self):
        return self.lower - self.board.start

    def __call__(self):
        self.visited.clear()
        return self.walk(Coordinate(0, 0), self.history, 0)

    def walk(self, coord, path, heat):
        if coord not in self.board or coord in self.visited or not path:
            return

        heat += self.board[coord]
        if self.lower is not None and heat >= self.lower:
            return

        self.visited[coord] = path.peek()
        if self.board.target(coord):
            self.lower = heat
            if logging.getLogger().isEnabledFor(logging.WARNING):
                for s in self.board.to_strings(self.visited):
                    logging.warning(s)
            logging.critical(int(self))
        else:
            for c in self.board:
                self.walk(coord + c, path + c, heat)
        self.visited.pop(coord)

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
    history = History(args.max_direction + 1)

    machine = MachinePartsFactory(board, history)
    machine()
    print(int(machine))

import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser

#
#
#
Coordinate = cl.namedtuple('Coordinate', 'row, col')

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

class MachinePartsFactory:
    _navigation = (
        (-1, 0), # up
        ( 0, 1), # right
        ( 1, 0), # down
    )
    _visited = '#'

    def __init__(self, board, history):
        self.board = board
        self.history = history
        self.shape = tuple(len(x) - 1 for x in (self.board, self.board[0]))
        self.lower = float('inf')
        self.navigation = tuple(it.starmap(Coordinate, self._navigation))

    def __call__(self):
        self.board[0][0] = 0
        return self.walk(Coordinate(0, 0), self.history, 0)

    def walk(self, coord, path, heat):
        if all(0 <= x <= y for (x, y) in zip(coord, self.shape)) and path:
            value = self.board[coord.row][coord.col]
            if value != self._visited:
                self.board[coord.row][coord.col] = self._visited
                self.explore(coord, path, heat + value)
                self.board[coord.row][coord.col] = value

    def explore(self, coord, path, heat):
        if heat < self.lower:
            if all(x == y for (x, y) in zip(coord, self.shape)):
                if heat < self.lower:
                    self.lower = heat
                    logging.error(self.lower)
                    if logging.getLogger().isEnabledFor(logging.WARNING):
                        for row in self.board:
                            logging.warning(''.join(map(str, row)))
            else:
                for n in self.navigation:
                    c = Coordinate(coord.row + n.row, coord.col + n.col)
                    self.walk(c, path + n, heat)



def scanf(fp):
    for row in fp:
        yield list(map(int, row.strip()))

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--recursive-limit', type=int)
    args = arguments.parse_args()

    machine = MachinePartsFactory(list(scanf(sys.stdin)), History(3))
    machine()
    print(machine.lower)

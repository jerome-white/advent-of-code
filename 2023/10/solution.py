import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

#
#
#
@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def __add__(self, other):
        return type(self)(self.row + other.row, self.col + other.col)

#
#
#
class Tile:
    def __init__(self, symbol, position, *args):
        self.symbol = symbol
        self.position = position
        self.navigation = args

    def __repr__(self):
        return self.symbol

    def __str__(self):
        return f'({self.position.row},{self.position.col}) {repr(self)}'

    def __iter__(self):
        for n in self.navigation:
            yield self.position + n

class NorthSouth(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(-1, 0), Position(1, 0))

class EastWest(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(0, -1), Position(0, 1))

class NorthEast(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(-1, 0), Position(0, 1))

class NorthWest(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(-1, 0), Position(0, -1))

class SouthWest(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(1, 0), Position(0, -1))

class SouthEast(Tile):
    def __init__(self, symbol, position):
        super().__init__(symbol, position, Position(1, 0), Position(0, 1))

#
#
#
class Grid:
    def __init__(self, fp):
        self.grid = {}
        self.start = []

        dtypes = {
            '|': NorthSouth,
            '-': EastWest,
            'L': NorthEast,
            'J': NorthWest,
            '7': SouthWest,
            'F': SouthEast,
        }

        for (r, line) in enumerate(fp):
            row = line.strip()
            for (c, cell) in enumerate(row):
                p = Position(r, c)
                if cell == 'S':
                    self.start.append(p)
                elif cell in dtypes:
                    _Tile = dtypes[cell]
                    self.grid[p] = _Tile(cell, p)

    def __iter__(self):
        compass = (
            ('|F7', -1,  0),
            ('J7-',  0,  1),
            ('|JL',  1,  0),
            ('-LF',  0, -1),
        )

        for (i, *j) in compass:
            name = set(i)
            position = Position(*j)
            for s in self.start:
                pos = s + position
                tile = self.grid.get(pos)
                if tile is not None and repr(tile) in name:
                    yield pos

    def __getitem__(self, item):
        return self.grid[item]

    def __contains__(self, item):
        return item in self.grid

    def walk(self, position, visited=None, distance=1):
        if visited is None:
            visited = set()

        if position in self and position not in visited:
            yield (position, distance)
            distance += 1
            visited.add(position)
            for p in self[position]:
                yield from self.walk(p, visited, distance)

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--recursive-limit', type=int)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    if args.recursive_limit:
        sys.setrecursionlimit(args.recursive_limit)

    grid = Grid(sys.stdin)
    distances = {}

    for p in grid:
        logging.warning(p)
        for (t, d) in grid.walk(p):
            logging.debug('%s %s', grid[t], d)
            distances[t] = min(distances[t], d) if t in distances else d

    print(max(distances.values()))

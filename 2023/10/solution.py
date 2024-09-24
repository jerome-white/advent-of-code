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

    def __str__(self):
        return f'({self.position.row},{self.position.col}) {self.symbol}'

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

class Start(Tile):
    def __init__(self, symbol, position):
        directions = list(it.starmap(Position, (
            (-1, 0),
            (0, 1),
            (1, 0),
            (0, -1),
        )))
        super().__init__(symbol, position, *directions)

#
#
#
@dataclass
class Cell:
    start: bool
    tile: Tile

    def __bool__(self):
        return self.start

def scanf(fp):
    start = 'S'
    dtypes = {
        '|': NorthSouth,
        '-': EastWest,
        'L': NorthEast,
        'J': NorthWest,
        '7': SouthWest,
        'F': SouthEast,
        start: Start,
    }

    for (r, line) in enumerate(fp):
        row = line.strip()
        for (c, cell) in enumerate(row):
            if cell in dtypes:
                s = cell == start
                p = Position(r, c)
                _Tile = dtypes[cell]

                yield Cell(s, _Tile(cell, p))

def walk(grid, position, visited=None, distance=1):
    if visited is None:
        visited = set()

    if position in grid and position not in visited:
        yield (position, distance)
        distance += 1
        visited.add(position)
        for p in grid.get(position):
            yield from walk(grid, p, visited, distance)

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

    grid = {}
    starts = []
    for c in scanf(sys.stdin):
        if c:
            starts.append(c.tile)
        else:
            grid[c.tile.position] = c.tile

    distances = {}
    for S in starts:
        for p in S:
            logging.warning(p)
            for (t, d) in walk(grid, p):
                logging.debug(f'\t {grid[t]}: {d}')
                distances[t] = min(distances[t], d) if t in distances else d

    print(max(distances.values()))

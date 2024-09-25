import itertools as it
import functools as ft
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
    def __init__(self, symbol, *args):
        self.symbol = symbol
        self.navigation = args

    def __str__(self):
        return self.symbol

    def explore(self, source):
        for n in self.navigation:
            yield source + n

class NorthSouth(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(-1, 0), Position(1, 0))

class EastWest(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(0, -1), Position(0, 1))

class NorthEast(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(-1, 0), Position(0, 1))

class NorthWest(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(-1, 0), Position(0, -1))

class SouthWest(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(1, 0), Position(0, -1))

class SouthEast(Tile):
    def __init__(self, symbol):
        super().__init__(symbol, Position(1, 0), Position(0, 1))

class StationaryTile(Tile):
    pass

class StartTile(Tile):
    pass

#
#
#
class Grid:
    _dtypes = {
        '|': NorthSouth,
        '-': EastWest,
        'L': NorthEast,
        'J': NorthWest,
        '7': SouthWest,
        'F': SouthEast,
        'S': StartTile,
    }
    _compass = (
        ('|F7', -1,  0),
        ('J7-',  0,  1),
        ('|JL',  1,  0),
        ('-LF',  0, -1),
    )

    def __init__(self, fp):
        self.grid = []

        for line in fp:
            row = []
            for r in line.strip():
                tile = self._dtypes.get(r, StationaryTile)
                row.append(tile(r))
            self.grid.append(row)

        self.shape = (len(self.grid), len(self.grid[0]))
        self.compass = {
            frozenset(x): Position(*y) for (x, *y) in self._compass
        }

    def __iter__(self):
        for (r, row) in enumerate(self.grid):
            for (c, tile) in enumerate(row):
                p = Position(r, c)
                yield (p, tile)

    def __getitem__(self, position):
        (r, c) = (position.row, position.col)
        if all(0 <= x < y for (x, y) in zip((r, c), self.shape)):
            return self.grid[r][c]

        raise IndexError()

    @ft.singledispatchmethod
    def _starts(self, tile, position):
        return
        yield

    @_starts.register
    def _(self, tile: StartTile, position):
        for (k, v) in self.compass.items():
            pos = position + v
            try:
                tile = self[pos]
            except IndexError:
                continue
            if str(tile) in k:
                yield pos

    def sources(self):
        for (p, t) in self:
            yield from self._starts(t, p)

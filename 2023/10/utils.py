import itertools as it
from dataclasses import dataclass

#
#
#
@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def __iter__(self):
        yield from (
            self.row,
            self.col,
        )

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

    def __call__(self, source):
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

class GroundTile(Tile):
    pass

class StartTile(Tile):
    pass

#
#
#

@dataclass(frozen=True)
class Visit:
    tile: Tile
    position: Position
    distance: int

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
        self.grid = {}

        for (r, row) in enumerate(fp):
            for (c, cell) in enumerate(row.strip()):
                pos = Position(r, c)
                tile = self._dtypes.get(cell, GroundTile)
                self.grid[pos] = tile(cell)

        self.compass = {
            frozenset(x): Position(*y) for (x, *y) in self._compass
        }

    def __iter__(self):
        yield from self.grid.items()

    def starts(self):
        for (u, src) in self:
            if isinstance(src, StartTile):
                for (n, pos) in self.compass.items():
                    v = u + pos
                    if v in self.grid:
                        dst = self.grid[v]
                        if str(dst) in n:
                            yield (u, v)

    def walk(self, u, v, visited=None):
        if visited is None:
            visited = set()

        if u in self.grid and v not in visited:
            visited.add(v)
            yield (u, v)
            tile = self.grid[v]
            for w in tile(v):
                if w != u:
                    yield from self.walk(v, w, visited)

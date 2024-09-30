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
        self.grid = []

        for line in fp:
            row = []
            for r in line.strip():
                tile = self._dtypes.get(r, GroundTile)
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

    def select(self, dtype):
        for (p, t) in self:
            if isinstance(t, dtype):
                yield (p, t)

    def starts(self):
        for (p, t) in self.select(StartTile):
            for (k, v) in self.compass.items():
                position = p + v
                try:
                    tile = self[position]
                except IndexError:
                    continue
                if str(tile) in k:
                    yield position

    def walk(self, position, visited=None, distance=1):
        if visited is None:
            visited = set()

        if position not in visited:
            visited.add(position)
            try:
                tile = self[position]
            except IndexError:
                return
            yield Visit(tile, position, distance)

            distance += 1
            for p in tile(position):
                yield from self.walk(p, visited, distance)

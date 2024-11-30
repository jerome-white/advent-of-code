import sys
import logging
import itertools as it
import operator as op
from argparse import ArgumentParser
from dataclasses import dataclass, fields, replace, astuple

from shapely import Point, Polygon

@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def __add__(self, other):
        return type(self)(self.row + other.row, self.col + other.col)

@dataclass(frozen=True)
class Step:
    direction: Position
    length: int
    color: str

    def __iter__(self):
        yield from it.repeat(self.direction, self.length)

#
#
#
def scanf(fp):
    directions = { x: Position(*y) for (x, y) in (
        ('U', (-1,  0)),
        ('D', ( 1,  0)),
        ('L', ( 0, -1)),
        ('R', ( 0,  1)),
    )}

    for line in fp:
        (d, l, c) = line.strip().split()

        d = directions[d]
        l = int(l)
        assert c.startswith('(#') and c.endswith(')')
        c = c[2:-1]

        yield Step(d, l, c)

def dig(instructions, position):
    for step in instructions:
        for s in step:
            position += s
            yield position

def area(polygon):
    (*_, rows, cols) = (int(x) + 1 for x in polygon.bounds)
    for r in range(rows):
        for c in range(cols):
            pt = Point(r, c)
            yield polygon.intersects(pt)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    start = Position(0, 0)
    iterable = dig(scanf(sys.stdin), start)
    polygon = Polygon(map(astuple, it.chain([start], iterable)))
    print(sum(area(polygon)))

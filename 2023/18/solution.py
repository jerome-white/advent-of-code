import sys
# import logging
import itertools as it
from argparse import ArgumentParser
from dataclasses import dataclass

from shapely import Point, Polygon

@dataclass(frozen=True)
class Step:
    direction: Point
    length: int
    color: str

#
#
#
def scanf(fp):
    directions = { x: Point(*y) for (x, y) in (
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

def dig(instructions, pt):
    for step in instructions:
        for s in it.repeat(step.direction, step.length):
            pt = Point(pt.x + s.x, pt.y + s.y)
            yield pt

def area(polygon):
    (x1, y1, x2, y2) = map(int, polygon.bounds)
    iterable = (range(x, y + 1) for (x, y) in ((x1, x2), (y1, y2)))

    for (r, c) in it.product(*iterable):
        yield polygon.intersects(Point(r, c))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    start = Point(0, 0)
    iterable = dig(scanf(sys.stdin), start)
    polygon = Polygon(it.chain([start], iterable))

    print(sum(area(polygon)))

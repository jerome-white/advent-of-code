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

#
#
#
class MapReader:
    def __init__(self, fp, up, down, left, right):
        self.fp = fp
        self.navigation = { x: Point(*y) for (x, y) in (
            (up,    (-1,  0)),
            (down,  ( 1,  0)),
            (left,  ( 0, -1)),
            (right, ( 0,  1)),
        )}

    def __iter__(self):
        for line in self.fp:
            (d, l) = self.parse(*line.strip().split())
            d = self.navigation[d]

            yield Step(d, l)

    def direction(self, d, l, c):
        raise NotImplementedError()

class StandardMapReader(MapReader):
    def __init__(self, fp):
        super().__init__(fp, 'U', 'D', 'L', 'R')

    def parse(self, d, l, c):
        return (d, int(l))

class SwappedMapReader(MapReader):
    def __init__(self, fp):
        super().__init__(fp, '3', '1', '2', '0')

    def parse(self, d, l, c):
        assert c.startswith('(#') and c.endswith(')')

        (l, d) = (c[2:-2], c[-2])
        return (d, int(l, 16))

#
#
#
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

    reader = StandardMapReader if args.version == 1 else SwappedMapReader

    start = Point(0, 0)
    iterable = dig(reader(sys.stdin), start)
    polygon = Polygon(it.chain([start], iterable))

    print(sum(area(polygon)))

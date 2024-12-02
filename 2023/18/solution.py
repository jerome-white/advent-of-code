import sys
import itertools as it
from argparse import ArgumentParser
from dataclasses import dataclass
from shapely import Point, Polygon, LineString
from shapely.ops import linemerge

@dataclass(frozen=True)
class Step:
    direction: Point
    length: int

    def advance(self, point):
        coords = []
        for ((u, *_), (v, *_)) in zip(point.xy, self.direction.xy):
            magnitude = u + (v * self.length)
            coords.append(magnitude)

        return Point(*coords)

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

    def parse(self, d, l, c):
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
        pt = step.advance(pt)
        yield pt

def area(polygon):
    (min_x, min_y, max_x, max_y) = map(int, polygon.bounds)

    for x in range(min_x, max_x + 1):
        line = LineString([ (x, y) for y in (min_y, max_y) ])
        overlap = line.intersection(polygon)
        try:
            additional = len(linemerge(overlap).geoms)
        except (AttributeError, ValueError):
            additional = 1

        yield overlap.length + additional

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    reader = StandardMapReader if args.version == 1 else SwappedMapReader

    start = Point(0, 0)
    iterable = dig(reader(sys.stdin), start)
    polygon = Polygon(it.chain([start], iterable))

    print(sum(area(polygon)))

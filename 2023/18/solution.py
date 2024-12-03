import sys
import logging
import itertools as it
import functools as ft
from argparse import ArgumentParser
from dataclasses import dataclass, replace
from multiprocessing import Pool, Queue

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

@dataclass(frozen=True)
class Boundary:
    min_x: int
    min_y: int
    max_x: int
    max_y: int

    @ft.cached_property
    def shape(self):
        return (
            self.max_x - self.min_x, # height
            self.max_y - self.min_y, # width
        )

    def __str__(self):
        return f'({self.min_x}, {self.min_y}) ({self.max_x}, {self.max_y})'

    def __iter__(self):
        for x in range(self.min_x, self.max_x + 1):
            args = ((x, y) for y in (self.min_y, self.max_y))
            yield LineString(args)

    def __call__(self, size):
        min_x = self.min_x
        max_x = min_x + size

        while min_x <= self.max_x:
            yield replace(self, min_x=min_x, max_x=max_x)
            min_x = max_x + 1
            max_x = min(self.max_x, max_x + size)

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
def func(incoming, outgoing, polygon):
    while True:
        boundary = incoming.get()
        logging.warning(boundary)

        size = 0
        for line in boundary:
            overlap = line.intersection(polygon)
            try:
                merged = linemerge(overlap)
                edges = len(merged.geoms)
            except (AttributeError, ValueError):
                edges = 1
            size += overlap.length + edges
        assert size.is_integer()

        outgoing.put(int(size))

def dig(instructions, pt):
    for step in instructions:
        pt = step.advance(pt)
        yield pt

def build(reader):
    start = Point(0, 0)
    iterable = dig(reader, start)

    return Polygon(it.chain([start], iterable))

def area(polygon, args):
    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        polygon,
    )

    with Pool(args.workers, func, initargs) as pool:
        boundary = Boundary(*map(int, polygon.bounds))
        (height, _) = boundary.shape
        segments = height // pool._processes

        jobs = 0
        for s in boundary(segments):
            outgoing.put(s)
            jobs += 1

        for _ in range(jobs):
            size = incoming.get()
            yield size

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    reader = StandardMapReader if args.version == 1 else SwappedMapReader
    print(sum(area(build(reader(sys.stdin)), args)))

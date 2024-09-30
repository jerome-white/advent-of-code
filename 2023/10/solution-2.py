import sys
import logging
import operator as op
import itertools as it
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

from shapely import Point, Polygon

from utils import Grid, Position, GroundTile

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
    paths = set()
    enclosed = set()

    for (u, v) in grid.starts():
        polygon = Polygon(it.chain.from_iterable(map(tuple, grid.walk(u, v))))
        for (p, _) in grid:
            point = Point(tuple(p))
            if polygon.contains(point):
                logging.warning(p)
                enclosed.add(p)

    print(len(enclosed))

import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

from utils import (
    Grid,
    Position,
)

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
    distances = {}

    for p in grid.sources():
        logging.warning(p)
        for v in grid.walk(p):
            logging.debug('%s %s', v.tile, v.distance)
            if v.tile in distances:
                distances[v.tile] = min(distances[v.tile], v.distance)
            else:
                distances[v.tile] = v.distance

    print(max(distances.values()))

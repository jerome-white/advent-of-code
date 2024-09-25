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
class PipeGrid(Grid):
    def walk(self, position, visited, distance=1):
        if position not in visited:
            visited.add(position)

            try:
                tile = self[position]
            except IndexError:
                return
            yield (tile, distance)

            distance += 1
            for p in tile.explore(position):
                yield from self.walk(p, visited, distance)

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

    grid = PipeGrid(sys.stdin)
    visited = set()
    distances = {}

    for p in grid.sources():
        logging.warning(p)
        for (t, d) in grid.walk(p, visited):
            logging.debug('%s %s', t, d)
            distances[t] = min(distances[t], d) if t in distances else d
        visited.clear()

    print(max(distances.values()))

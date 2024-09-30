import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

import networkx as nx

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
    G = nx.Graph()
    distance = None

    for (u, v) in grid.starts():
        G.add_edges_from(grid.walk(u, v))
        paths = nx.shortest_path_length(G, source=u)
        furthest = max(paths.values())
        if distance is None or distance < furthest:
            distance = furthest

    print(distance)

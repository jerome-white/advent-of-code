import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool, Queue

import networkx as nx
from shapely import Point, Polygon

from utils import Grid

class PipeMaze:
    def __init__(self, grid):
        self.grid = grid

    def __call__(self, incoming, outgoing, args):
        if args.recursive_limit:
            sys.setrecursionlimit(args.recursive_limit)

        while True:
            (u, v) = incoming.get()
            logging.warning('%s %s', u, v)
            for i in self.handle(u, v):
                outgoing.put(i)
            outgoing.put(None)

class PathLengthMaze(PipeMaze):
    def handle(self, u, v):
        G = nx.Graph()
        G.add_edges_from(self.grid.walk(u, v))
        paths = nx.shortest_path_length(G, source=u)
        yield from paths.values()

    def collect(self, values):
        return max(values)

class EnclosedMaze(PipeMaze):
    def stream(self, u, v):
        for edge in self.grid.walk(u, v):
            yield from map(tuple, edge)

    def handle(self, u, v):
        polygon = Polygon(self.stream(u, v))
        for (p, _) in self.grid:
            point = Point(tuple(p))
            if polygon.contains(point):
                yield p

    def collect(self, values):
        return len(set(values))

#
#
#
def solve(args, grid, func):
    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for u_v in grid.starts():
            outgoing.put(u_v)
            jobs += 1

        while jobs:
            result = incoming.get()
            if result is None:
                jobs -= 1
            else:
                yield result

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--recursive-limit', type=int)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    grid = Grid(sys.stdin)
    _Maze = PathLengthMaze if args.version == 1 else EnclosedMaze
    maze = _Maze(grid)

    print(maze.collect(solve(args, grid, maze)))

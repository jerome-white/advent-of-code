import sys
import logging
import functools as ft
import itertools as it
import collections as cl
from argparse import ArgumentParser

import networkx as nx

Coordinate = cl.namedtuple('Coordinate', 'row, col')

class Grid:
    _galaxy = '#'

    @ft.cached_property
    def shape(self):
        return (len(self.grid), len(self.grid[0]))

    def __init__(self, fp):
        self.grid = [ x.strip() for x in fp ]

    def __iter__(self):
        for (r, row) in enumerate(self.grid):
            for (c, cell) in enumerate(row):
                if cell == self._galaxy:
                    yield Coordinate(r, c)

def shortest_paths(grid):
    G = nx.grid_2d_graph(*grid.shape)
    for (u, v) in it.combinations(grid, r=2):
        plength = nx.shortest_path_length(G, source=u, target=v)
        logging.warning('%s -> %s: %d', u, v, plength)
        yield plength

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    grid = Grid(sys.stdin)
    print(sum(shortest_paths(grid)))

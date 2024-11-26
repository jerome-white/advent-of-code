import sys
import math
import heapq
import logging
import itertools as it
import functools as ft
from argparse import ArgumentParser
from dataclasses import dataclass

#
#
#
@dataclass(order=True, frozen=True)
class Position:
    x: int
    y: int

    def __str__(self):
        return f'({self.x},{self.y})'

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

@dataclass(frozen=True)
class Node:
    position: Position
    heading: Position
    momentum: int

    @ft.singledispatchmethod
    def __add__(self, other):
        raise TypeError(type(other))

    @__add__.register
    def _(self, other: Position):
        position = self.position + other

        momentum = 1
        if self.heading == other:
            momentum += self.momentum

        return type(self)(position, other, momentum)

#
#
#
class Compass:
    _directions = (
        (-1,  0), # up
        ( 0,  1), # right
        ( 1,  0), # down
        ( 0, -1), # left
    )

    def __init__(self):
        self.directions = list(it.starmap(Position, self._directions))

    def __iter__(self):
        yield from self.directions

    def __call__(self, node):
        yield from (node + x for x in self)

#
#
#
class VertextPolice:
    @staticmethod
    def okay(u, v):
        return True

    def __init__(self, police=None):
        self.police = police or self.okay

    def __call__(self, u, v):
        return self.check(u, v) and self.police(u, v)

    def check(self, u, v):
        raise NotImplementedError()

class MomentumChecker(VertextPolice):
    def __init__(self, upper, police=None):
        super().__init__(police)
        self.upper = upper

    def check(self, u, v):
        return v.momentum <= self.upper

class HeadingChecker(VertextPolice):
    _stationary = Position(0, 0)

    def check(self, u, v):
        return u.heading + v.heading != self._stationary

class PositionChecker(VertextPolice):
    def __init__(self, positions, police=None):
        super().__init__(police)
        self.positions = positions

    def check(self, u, v):
        return v.position in self.positions

#
#
#
class Graph(dict):
    @ft.cached_property
    def shape(self):
        return (Position(0, 0), max(self))

    @ft.singledispatchmethod
    def at(self, item):
        raise TypeError(type(item))

    @at.register
    def _(self, item: Position):
        return self[item]

    @at.register
    def _(self, item: Node):
        return self.at(item.position)

class PathFinder:
    @dataclass
    class Route:
        node: Node
        distance: int

        def __int__(self):
            return self.distance

        def __lt__(self, other):
            return self.distance < other.distance

    def __init__(self, node):
        route = self.Route(node, 0)

        self.unseen = [ route ]
        self.cache = {
            node: route.distance,
        }

    def __iter__(self):
        heapq.heapify(self.unseen)
        return self

    def __next__(self):
        if not self.unseen:
            raise StopIteration()

        return heapq.heappop(self.unseen)

    def at(self, node):
        return self.cache.get(node, math.inf)

    def push(self, node, distance):
        self.cache[node] = distance
        route = self.Route(node, distance)
        heapq.heappush(self.unseen, route)

    def touched(self, route):
        return not math.isinf(route.distance)

#
#
#
def scanf(fp):
    for (r, row) in enumerate(fp):
        for (c, cell) in enumerate(row.strip()):
            position = Position(r, c)
            yield (position, int(cell))

def walk(graph, args):
    (source, target) = graph.shape
    node = Node(source, Position(0, 0), 0)
    gpath = PathFinder(node)

    acceptable = MomentumChecker(args.max_direction)
    acceptable = HeadingChecker(acceptable)
    acceptable = PositionChecker(graph.keys(), acceptable)

    compass = Compass()

    for src in gpath:
        if src.node.position == target or not gpath.touched(src):
            logging.critical(src)
            return src

        logging.info(src)
        for n in compass(src.node):
            if acceptable(src.node, n):
                distance = graph.at(n) + src.distance
                if distance < gpath.at(n):
                    gpath.push(n, distance)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--max-direction', type=int, default=3)
    args = arguments.parse_args()

    graph = Graph(scanf(sys.stdin))
    route = walk(graph, args)
    print(int(route))

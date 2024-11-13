import sys
import logging
import itertools as it
import functools as ft
from dataclasses import dataclass
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

#
#
#
@dataclass(frozen=True)
class Coordinate:
    row: int
    col: int

    def __iter__(self):
        yield from (
            self.row,
            self.col,
        )

    def __neg__(self):
        return type(self)(-self.row, -self.col)

    def __add__(self, other):
        return type(self)(self.row + other.row, self.col + other.col)

    def __invert__(self):
        return type(self)(self.col, self.row)

@dataclass(frozen=True)
class State:
    pos: Coordinate
    traj: Coordinate

#
#
#
class Action:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __call__(self, trajectory):
        yield trajectory

class EmptySpace(Action):
    def __init__(self):
        super().__init__('.')

class UpwardMirror(Action):
    def __init__(self):
        super().__init__('/')

    def __call__(self, trajectory):
        yield -~trajectory

class DownwardMirror(Action):
    def __init__(self):
        super().__init__('\\')

    def __call__(self, trajectory):
        yield ~trajectory

class Splitter(Action):
    def __call__(self, trajectory):
        if self.act(trajectory):
            iterable = map(self.split, (-1, 1))
        else:
            iterable = super().__call__(trajectory)

        yield from iterable

    def act(self, trajectory):
        raise NotImplementedError()

    def split(self, value):
        raise NotImplementedError()

class VerticalSplitter(Splitter):
    def __init__(self):
        super().__init__('|')

    def act(self, trajectory):
        return not trajectory.row and trajectory.col

    def split(self, value):
        return Coordinate(value, 0)

class HorizontalSplitter(Splitter):
    def __init__(self):
        super().__init__('-')

    def act(self, trajectory):
        return trajectory.row and not trajectory.col

    def split(self, value):
        return Coordinate(0, value)

#
#
#
class ContraptionParser:
    def __init__(self, contraption):
        self.contraption = contraption

    def __iter__(self):
        raise NotImplementedError()

class SingleStartContraption(ContraptionParser):
    def	__iter__(self):
        args = (Coordinate(0, x) for x in (range(2)))
        yield State(*args)

class MultiStartContraption(ContraptionParser):
    _up    = Coordinate(-1,  0)
    _down  = Coordinate( 1,  0)
    _left  = Coordinate( 0, -1)
    _right = Coordinate( 0,  1)

    @ft.cached_property
    def shape(self):
        (rows, cols) = (None, None)
        for p in self.contraption:
            if rows is None or p.row > rows:
                rows = p.row
            if cols is None or p.col > cols:
                cols = p.col

        return Coordinate(rows, cols)

    def __init__(self, contraption):
        super().__init__(contraption)
        self.dim = Coordinate(*(x - 1 for x in self.shape))

    def __iter__(self):
        trajectories = []
        for e in self.edge():
            if not e.row:
                trajectories.append(self._down)
            if not e.col:
                trajectories.append(self._right)
            if e.row == self.dim.row:
                trajectories.append(self._up)
            if e.col == self.dim.col:
                trajectories.append(self._left)

            for t in trajectories:
                yield State(e, t)

            trajectories.clear()

    def edge(self):
        for i in it.product(*map(range, self.shape)):
            if any(x in (0, y) for (x, y) in zip(i, self.dim)):
                yield Coordinate(*i)

#
#
#
class ContraptionBeam:
    def __init__(self, contraption):
        self.contraption = contraption
        self.history = set()

    def __call__(self, start):
        self.history.clear()
        yield from self.explore(start)

    def explore(self, state):
        if state not in self.history and state.pos in self.contraption:
            self.history.add(state)
            yield state.pos

            action = self.contraption[state.pos]
            for a in action(state.traj):
                s = State(state.pos + a, a)
                yield from self.explore(s)

#
#
#
def func(incoming, outgoing, contraption, args):
    beam = ContraptionBeam(contraption)
    if args.recursive_limit:
        sys.setrecursionlimit(args.recursive_limit)

    while True:
        start = incoming.get()
        logging.warning(start)
        outgoing.put(len(set(beam(start))))

def scanf(fp):
    dtypes = { str(x): x for x in (
        EmptySpace(),
        UpwardMirror(),
        DownwardMirror(),
        VerticalSplitter(),
        HorizontalSplitter(),
    )}

    for (r, row) in enumerate(fp):
        for (c, cell) in enumerate(row.strip()):
            pos = Coordinate(r, c)
            action = dtypes[cell]
            yield (pos, action)

def energized(contraption, args):
    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        contraption,
        args,
    )

    with Pool(args.workers, func, initargs):
        if args.version == 1:
            MyStarter = SingleStartContraption
        else:
            MyStarter = MultiStartContraption
        starter = MyStarter(contraption)

        jobs = 0
        for s in starter:
            outgoing.put(s)
            jobs += 1

        for _ in range(jobs):
            result = incoming.get()
            yield result

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--recursive-limit', type=int)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    print(max(energized(dict(scanf(sys.stdin)), args)))

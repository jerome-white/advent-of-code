import sys
import math
import logging
import operator as op
import itertools as it
import functools as ft
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool

from sympy import solve_univariate_inequality
from sympy.abc import x

#
#
#
@dataclass
class BoatRace:
    time: int
    distance: int

#
#
#
class RaceParser:
    def	__call__(self, fp):
        for i in self.parse(fp):
            yield BoatRace(*map(int, i))

    def parse(self, fp):
        raise NotImplementedError()

class StandardRaceParser(RaceParser):
    def parse(self, fp):
        iterable = (it.islice(l.strip().split(), 1, None) for l in fp)
        yield from zip(*iterable)

class KernedRaceParser(RaceParser):
    def parse(self, fp):
        yield tuple(self.scanf(fp))

    def scanf(self, fp):
        for line in fp:
            (_, *tail) = line.strip().split()
            yield ''.join(tail)

#
#
#
def func(race):
    logging.warning(race)

    inequality = (race.time - x) * x > race.distance
    solution = solve_univariate_inequality(inequality, x, relational=False)

    left = math.floor(solution.left + 1)
    right = math.ceil(solution.right - 1)

    return right - left + 1

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        if args.version == 1:
            parser = StandardRaceParser()
        else:
            parser = KernedRaceParser()
        winners = pool.imap_unordered(func, parser(sys.stdin))
        print(ft.reduce(op.mul, winners))

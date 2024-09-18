import sys
import random
import logging
import functools as ft
import itertools as it
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool

@dataclass
class AlmanacCategory:
    dst: int
    src: int
    span: int

    def __post_init__(self):
        self.length = self.src + self.span

    def __getitem__(self, item):
        if self.src <= item < self.length:
            return self.dst + (item - self.src)

        raise IndexError(item)

@dataclass
class Record:
    target: str
    categories: AlmanacCategory

class Almanac:
    def __init__(self, categories, parent=None):
        self.categories = categories
        self.parent = parent

    def __call__(self, seed):
        if self.parent is not None:
            seed = self.parent(seed)

        for c in self.categories:
            try:
                seed = c[seed]
                break
            except IndexError:
                continue

        return seed

class AlmanacReader:
    @staticmethod
    def dump(origin, target, categories):
        cats = list(it.starmap(AlmanacCategory, categories))
        record = Record(target, cats)
        yield (origin, record)

    def __call__(self, fp):
        records = dict(self.scanf(fp))

        sources = set(records.keys())
        targets = set(x.target for x in records.values())
        start = sources.difference(targets)
        if len(start) != 1:
            raise ValueError()
        start = start.pop()

        while start in records:
            rec = records[start]
            yield rec.categories
            start = rec.target

    def scanf(self, fp):
        values = []
        for i in fp:
            line = i.strip()
            if not line:
                if values:
                    yield from self.dump(origin, target, values)
                    values.clear()
            elif line.startswith('seeds:'):
                continue
            elif line.endswith('map:'):
                (direction, _) = line.split()
                (origin, _, target) = direction.split('-')
            else:
                values.append(list(map(int, line.split())))

        if values:
            yield from self.dump(origin, target, values)

#
#
#
class SeedIterator:
    def __init__(self, fp):
        (_, *seeds) = (fp
                       .readline()
                       .strip()
                       .split())
        self.seeds = list(map(int, seeds))

    def __iter__(self):
        raise NotImplementedError()

class SingleSeed(SeedIterator):
    def __iter__(self):
        yield from self.seeds

class RangeSeed(SeedIterator):
    _jump = 2

    def __init__(self):
        super().__init__()
        (self.left, self.right) = (None, ) * 2

        for i in range(0, len(self.seeds), self._jump):
            (left, right) = it.islice(self.seeds, i, i + self._jump)
            right += left

            if self.left is None or left < self.left:
                self.left = left
            if self.right is None or right > self.right:
                self.right = right

    def __iter__(self):
        yield from range(self.left, self.right + 1)

#
#
#
def func(args):
    (seeds, almanac) = args
    location = min(map(almanac, seeds))
    logging.info('%d %d: %d', seeds[0], seeds[-1], location)

    return location

def deal(args, seeds):
    jobs = []
    (lower, upper) = (round(args.buffer_size * x) for x in (0.85, 1.15))
    limit = random.randint(lower, upper)

    for (i, s) in enumerate(seeds, 1):
        jobs.append(s)
        if not (i % limit):
            yield jobs
            jobs = []
            limit = random.randint(lower, upper)

    if jobs:
        yield jobs

def each(args):
    Seeds = SingleSeed if args.version == 1 else RangeSeed
    with args.almanac.open() as fp:
        seeds = Seeds(fp)

    reader = AlmanacReader()
    with args.almanac.open() as fp:
        almanac = None
        for entry in reader(fp):
            almanac = Almanac(entry, almanac)

    for i in deal(args, seeds):
        yield (i, almanac)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--almanac', type=Path)
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--buffer-size', type=int, default=int(1e6))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        lowest = None
        for i in pool.imap_unordered(func, each(args)):
            if lowest is None or i < lowest:
                lowest = i
                logging.warning(lowest)

        print(lowest)

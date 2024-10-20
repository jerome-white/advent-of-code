import sys
import logging
import operator as op
import itertools as it
import functools as ft
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

#
#
#
class PuzzleParser:
    def __init__(self, start=1):
        self.start = start

    def __call__(self, text):
        raise NotImplementedError()

class RowParser(PuzzleParser):
    def __call__(self, text):
        yield from map(reversed, enumerate(text, self.start))

class ColumnParser(PuzzleParser):
    def	__call__(self, text):
        (nrow, ncol) = map(len, (text, text[0]))
        for c in range(ncol):
            col = ''.join(text[x][c] for x in range(nrow))
            yield (col, c + self.start)

#
#
#
class ReflectionCollector:
    def __init__(self, strict=True):
        self.strict = strict
        self.distance = None
        self.reflections = set()

    def __iter__(self):
        if not self.strict or self.distance == 1:
            yield from self.reflections

    def add(self, u, v):
        distance = abs(u - v)
        if self.distance is None or distance < self.distance:
            self.distance = distance
            self.reflections.clear()

        if distance == self.distance:
            self.reflections.add(tuple(sorted((u, v))))

class ReflectionExplorer:
    @ft.cached_property
    def shape(self):
        axes = list(self.puzzle)
        return tuple(x(axes) for x in (min, max))

    def __init__(self, puzzle):
        self.puzzle = puzzle

    def __iter__(self):
        for i in self.reflections():
            try:
                yield self(*i) + 1
            except ValueError:
                pass

    def __call__(self, u, v):
        if any(x == y for (x, y) in zip((u, v), self.shape)):
            return 1

        (u, v) = (u - 1, v + 1)
        if not self.legal(u, v):
            raise ValueError()

        return 1 + self(u, v)

    def reflections(self):
        collector = ReflectionCollector()
        for (u, edges) in self.puzzle.items():
            for v in edges:
                collector.add(u, v)

        yield from collector

    def legal(self, u, v):
        edge = (u, v)
        n = len(edge)

        for i in range(n):
            (u_, v_) = (edge[x % n] for x in (i, i + 1))
            if u_ not in self.puzzle or v_ not in self.puzzle[u_]:
                return False

        return True

#
#
#
def collect(parser):
    puzzle = cl.defaultdict(set)
    boundaries = [ None ] * 2

    for (i, (k, v)) in enumerate(parser):
        puzzle[k].add(v)
        boundaries[bool(i)] = k
    if not any(len(puzzle[x]) > 1 for x in boundaries):
        raise ValueError('Invalid dimension')

    yield from puzzle.values()

def invert(collection):
    for dim in collection:
        for d in dim:
            exclusion = dim.difference([d])
            yield (d, sorted(exclusion))

def func(incoming, outgoing):
    parsers = {
        'r': RowParser(),
        'c': ColumnParser(),
    }

    while True:
        text = incoming.get()
        counts = cl.Counter()

        for (n, extract) in parsers.items():
            try:
                puzzle = dict(invert(collect(extract(text))))
            except ValueError as err:
                logging.error('%s: %s', err, n)
                continue
            explorer = ReflectionExplorer(puzzle)
            counts[n] += sum(explorer)
        assert sum(map(bool, counts.values())) == 1,\
            '{}\n{}'.format(counts, '\n'.join(text))

        outgoing.put(counts)

def scanf(fp):
    text = []
    for line in fp:
        row = line.strip()
        if row:
            text.append(row)
        else:
            yield text
            text = []

    if text:
        yield text

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for i in scanf(sys.stdin):
            outgoing.put(i)
            jobs += 1

        counts = cl.Counter()
        for _ in range(jobs):
            result = incoming.get()
            logging.warning(result)
            counts.update(result)

        print(counts['c'] + 100 * counts['r'])

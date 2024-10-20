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
class PuzzleIterator:
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def __iter__(self):
        raise NotImplementedError()

class RowIterator(PuzzleIterator):
    def __iter__(self):
        yield from self.puzzle

class ColumnIterator(PuzzleIterator):
    def __iter__(self):
        yield from map(''.join, zip(*self.puzzle))

#
#
#
def reflection(puzzle):
    lhs = cl.deque()
    walker = (enumerate(it.islice(puzzle, x, None), x) for x in range(2))
    
    for ((i, l), (j, r)) in zip(*walker):
        lhs.appendleft(l)
        if l == r:
            rhs = it.islice(puzzle, j, None)
            if all(x == y for (x, y) in zip(lhs, rhs)):
                return j

    raise ValueError()            
    
def func(incoming, outgoing):
    parsers = {
        'r': RowIterator,
        'c': ColumnIterator,
    }

    while True:
        text = incoming.get()

        counts = cl.Counter()                
        for (i, j) in parsers.items():
            try:
                n = reflection(list(j(text)))
            except ValueError:
                logging.error(i)
                continue
            counts[i] += n

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

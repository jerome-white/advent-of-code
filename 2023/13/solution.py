import sys
import logging
import operator as op
import itertools as it
import functools as ft
import collections as cl
from dataclasses import dataclass
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

#
#
#
@dataclass
class PuzzlePiece:
    index: int
    piece: str

    def __eq__(self, other):
        return self.piece == other.piece

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
def walk(puzzle):
    iterable = (enumerate(it.islice(puzzle, x, None), x) for x in range(2))
    for p in zip(*iterable):
        yield tuple(it.starmap(PuzzlePiece, p))

def reflect(puzzle):
    lhs = cl.deque()

    for (left, right) in walk(puzzle):
        lhs.appendleft(left.piece)
        if left == right:
            rhs = it.islice(puzzle, right.index, None)
            if all(x == y for (x, y) in zip(lhs, rhs)):
                return right.index

    raise ValueError()            
    
def func(incoming, outgoing):
    _parsers = {
        'r': RowIterator,
        'c': ColumnIterator,
    }

    while True:
        text = incoming.get()

        counts = cl.Counter()                
        for (axis, parse) in _parsers.items():
            view = list(parse(text))
            try:
                c = reflect(view)
            except ValueError:
                logging.error(axis)
                continue
            counts[axis] += c

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

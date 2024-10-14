import sys
import logging
import itertools as it
import functools as ft
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool

@dataclass(frozen=True)
class ConditionRecord:
    springs: str
    layout: tuple

    def align(self):
        pivot = None

        for ((i, l), s) in zip(enumerate(self.layout, 1), spans(self.springs)):
            if not s.completely('#'):
                break
            if len(s) != l:
                raise ValueError()
            pivot = (i, s.index)

        if pivot is None:
            return self

        (i, s) = pivot
        layout = self.layout[i:]
        springs = forward(self.springs, s)

        return type(self)(springs, layout)

@dataclass
class Span:
    span: str
    index: int

    def __init__(self, window, index):
        self.span = ''.join(window)
        self.index = index

    def __len__(self):
        return len(self.span)

    def completely(self, c):
        return all(x == c for x in self.span)

def spans(springs):
    window = []
    for (i, s) in enumerate(springs):
        if s == '.':
            if window:
                yield Span(window, i)
                window.clear()
        else:
            window.append(s)

    if window:
        yield Span(window, len(springs))

def forward(springs, start):
    for (i, s) in enumerate(it.islice(springs, start, None), start):
        if s != '.':
            return springs[i:]

    return ''

@ft.cache
def gather(crecord):
    try:
        crecord = crecord.align()
    except ValueError:
        return 0

    if not crecord.layout:
        return not crecord.springs.count('#')

    configs = 0
    if crecord.springs.find('?') >= 0:
        for i in ('#', '.'):
            s = crecord.springs.replace('?', i, 1)
            c = ConditionRecord(s, crecord.layout)
            configs += gather(c)

    return configs

def func(args):
    arrangements = gather(args)
    logging.warning('%s %d', args, arrangements)
    return arrangements

def records(fp, args):
    if args.folds is None:
        replicas = 1 if args.version == 1 else 5
    else:
        replicas = args.folds

    for line in fp:
        (springs, layout) = line.strip().split()
        layout = tuple(map(int, layout.split(',')))
        if replicas > 1:
            springs = '?'.join(it.repeat(springs, replicas))
            layout *= replicas

        yield ConditionRecord(springs, layout)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--folds', type=int)
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        counts = pool.imap_unordered(func, records(sys.stdin, args))
        print(sum(counts))

import sys
import logging
import itertools as it
import functools as ft
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool

ConditionRecord = cl.namedtuple('ConditionRecord', 'springs, layout')

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

def align(springs, target):
    pivot = None

    for ((i, t), s) in zip(enumerate(target, 1), spans(springs)):
        if not s.completely('#'):
            break
        if len(s) != t:
            raise ValueError()
        pivot = (i, s.index)

    if pivot is not None:
        (i, s) = pivot
        target = target[i:]
        springs = forward(springs, s)

    return (springs, target)

@ft.cache
def gather(springs, target):
    try:
        (springs, target) = align(springs, target)
    except ValueError:
        return 0

    if not target:
        return not springs.count('#')

    configs = 0
    if springs.find('?') >= 0:
        for i in ('#', '.'):
            s = springs.replace('?', i, 1)
            configs += gather(s, target)

    return configs

def func(args):
    arrangements = gather(*args)
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

import sys
import logging
import itertools as it
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

def sense(values):
    if not any(values):
        return 0

    iterable = zip(values, it.islice(values, 1, None))
    values_ = [ y - x for (x, y) in iterable ]

    return values[-1] + sense(values_)

def func(args):
    logging.warning(args)
    return sense(args)

def scanf(fp):
    for line in fp:
        yield list(map(int, line.strip().split()))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        values = pool.imap_unordered(func, scanf(sys.stdin))
        print(sum(values))

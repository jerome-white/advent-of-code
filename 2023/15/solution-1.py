import sys
import logging
from argparse import ArgumentParser
from multiprocessing import Pool

from utils import Step, scanf

def func(step):
    logging.warning(step)
    return hash(step)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        iterable = map(Step, scanf(sys.stdin))
        steps = pool.imap_unordered(func, iterable)
        print(sum(steps))

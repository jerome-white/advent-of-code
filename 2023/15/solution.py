import sys
import csv
import logging
from argparse import ArgumentParser
from multiprocessing import Pool

def func(word):
    logging.warning(word)

    current = 0
    for w in word:
        current += ord(w)
        current *= 17
        current %= 256

    return current

def scanf(fp):
    reader = csv.reader(fp)
    for row in reader:
        yield from row

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        steps = pool.imap_unordered(func, scanf(sys.stdin))
        print(sum(steps))

import re
import sys
import logging
import itertools as it
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool

ConditionRecord = cl.namedtuple('ConditionRecord', 'springs, layout')

def accept(springs, target):
    source = map(len, filter(None, springs.split('.')))
    return all(x == y for (x, y) in it.zip_longest(source, target))

def valid(springs, target):
    # src = cl.Counter(target)
    # dst = cl.Counter(map(len, re.findall('#+', springs)))
    # # logging.critical(f'{src} {dst}')

    # upper = max(src)
    # for (k, v) in dst.items():
    #     if k in src and v > src[k] or k > upper:
    #         return False

    return True

def gather(springs, target, layout=None, start=0):
    if layout is None:
        layout = target

    if valid(springs, target):
        if not layout:
            s = springs.replace('?', '.')
            if accept(s, target):
                yield s
        else:
            (head, *tail) = layout
            pounds = '#' * head
            stop = start + len(springs)
            for i in range(start, stop):
                j = i + head
                view = springs[i:j]
                if len(view) != j - i:
                    break
                if not any(x == '.' for x in view):
                    s = f'{springs[:i]}{pounds}{springs[j:]}'
                    yield from gather(s, target, tail, i)

def func(args):
    arrangements = set(gather(*args))
    n = len(arrangements)

    logging.error('%s %d', args, n)
    for a in arrangements:
        logging.warning(a)

    return n

def records(fp):
    for line in fp:
        (springs, layout) = line.strip().split()
        layout = tuple(map(int, layout.split(',')))
        yield ConditionRecord(springs, layout)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        counts = pool.imap_unordered(func, records(sys.stdin))
        print(sum(counts))

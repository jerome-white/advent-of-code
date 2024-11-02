import sys
import csv
import logging
import collections as cl
from argparse import ArgumentParser

class CycleTracker:
    def __init__(self):
        self.panels = cl.OrderedDict()

    def __iter__(self):
        start = False
        for (panel, cycle) in self.panels.items():
            start |= cycle
            if start:
                yield panel

    def push(self, panel):
        if panel in self.panels:
            self.panels[panel] = True
            raise ValueError()
        self.panels[panel] = False

    def trace(self):
        yield from self.panels

def load(panel):
    for (i, p) in enumerate(reversed(panel.splitlines()), 1):
        yield i * p.count('O')

def scanf(fp):
    reader = csv.reader(fp)
    yield from map('\n'.join, reader)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--rotations', type=int, default=int(1e9))
    args = arguments.parse_args()

    cycle = CycleTracker()
    for (i, row) in enumerate(scanf(sys.stdin)):
        try:
            cycle.push(row)
        except ValueError:
            break
        logging.info('{} {} {}'.format(
            i,
            row.replace('\n', '|'),
            sum(load(row)),
        ))
    (t_full, t_cycle) = map(list, (cycle.trace(), cycle))
    (m, n) = map(len, (t_full, t_cycle))
    c = m - n

    index = (args.rotations - c) % n
    print(sum(load(t_cycle[index])))

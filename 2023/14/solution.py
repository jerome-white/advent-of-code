import sys
import csv
import logging
import collections as cl

class PanelTracker:
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

#
#
#
def load(panel):
    for (i, p) in enumerate(reversed(panel.splitlines()), 1):
        yield i * p.count('O')

def scanf(fp):
    for line in fp:
        (index, panel) = line.rstrip().split()
        yield (
            int(index),
            panel.replace(',', '\n'),
        )

if __name__ == '__main__':
    panels = PanelTracker()
    rotations = None
    for (i, row) in scanf(sys.stdin):
        if rotations is None:
            rotations = i
        try:
            panels.push(row)
        except ValueError:
            break
        logging.info('{} {} {}'.format(
            i,
            row.replace('\n', '|'),
            sum(load(row)),
        ))

    (t_full, t_cycle) = map(list, (panels.trace(), panels))
    if t_cycle:
        (m, n) = map(len, (t_full, t_cycle))
        c = m - n
        index = (rotations - c) % n
        panel = t_cycle[index]
    else:
        panel = t_full[-1]
    print(sum(load(panel)))

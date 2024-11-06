import sys
import logging
import functools as ft
import collections as cl
from dataclasses import dataclass

#
#
#
@dataclass
class PanelInstance:
    rotation: int
    panel: str

#
#
#
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
class PanelHandler:
    def __init__(self, tracker, rotations):
        self.tracker = tracker
        self.rotations = rotations

    def __str__(self):
        raise NotImplementedError()

class StandardPanel(PanelHandler):
    def __str__(self):
        trace = list(self.tracker.trace())
        return trace[-1]

class CyclicPanel(PanelHandler):
    def __str__(self):
        (trace, cycle) = map(list, (self.tracker.trace(), self.tracker))
        (m, n) = map(len, (trace, cycle))
        c = m - n
        index = (self.rotations - c) % n

        return cycle[index]

#
#
#
@ft.singledispatch
def load(panel):
    raise TypeError(type(panel))

@load.register
def _(panel: str):
    for (i, p) in enumerate(reversed(panel.splitlines()), 1):
        yield i * p.count('O')

@load.register
def _(panel: PanelHandler):
    return load(str(panel))

def scanf(fp):
    for line in fp:
        (index, panel) = line.rstrip().split()
        yield PanelInstance(int(index), panel.replace(',', '\n'))

def handle(panels):
    tracker = PanelTracker()
    rotations = None

    for p in panels:
        if rotations is None:
            rotations = p.rotation

        try:
            tracker.push(p.panel)
        except ValueError:
            MyPanelHandler = CyclicPanel
            break

        logging.info(
            '%d %s %d',
            p.rotation,
            p.panel.replace('\n', '|'),
            sum(load(p.panel)),
        )
    else:
        MyPanelHandler = StandardPanel

    return MyPanelHandler(tracker, rotations)

#
#
#
if __name__ == '__main__':
    print(sum(load(handle(scanf(sys.stdin)))))

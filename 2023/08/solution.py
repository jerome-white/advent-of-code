import sys
import math
import string
import logging
import itertools as it
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool, Queue

#
#
#
@dataclass
class Node:
    left: str
    right: str

    def __getitem__(self, item):
        if item == 'L':
            return self.left
        if item == 'R':
            return self.right

        raise ValueError(item)

#
#
#
class NetworkState:
    (_a, _z) = ('A', 'Z')

    def __init__(self, network, a, z):
        self.network = network
        self.prefix = self._a * a
        self.suffix = self._z * z

    def __iter__(self):
        yield from filter(lambda x: x.endswith(self.prefix), self.network)

class StandardState(NetworkState):
    def __init__(self, network):
        super().__init__(network, 3, 3)

class GhostState(NetworkState):
    def __init__(self, network):
        super().__init__(network, 1, 1)

#
#
#
def scanf(fp):
    keep = set(string.ascii_uppercase + string.digits + ' ')
    for line in fp:
        letters = ''.join(filter(lambda x: x in keep, line))
        if letters:
            (key, *values) = letters.split()
            node = Node(*values)
            yield (key, node)

def func(incoming, outgoing, network, directions):
    while True:
        (loc, suffix) = incoming.get()
        logging.warning(loc)

        for (i, d) in enumerate(it.cycle(directions), 1):
            loc = network[loc][d]
            if loc.endswith(suffix):
                outgoing.put(i)
                break

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    directions = sys.stdin.readline().strip()
    network = dict(scanf(sys.stdin))

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        network,
        directions,
    )

    with Pool(args.workers, func, initargs):
        _State = StandardState if args.version == 1 else GhostState
        state = _State(network)

        jobs = 0
        for s in state:
            outgoing.put((s, state.suffix))
            jobs += 1

        results = []
        for _ in range(jobs):
            results.append(incoming.get())

        print(math.lcm(*results))

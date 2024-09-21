import sys
import string
import itertools as it
from argparse import ArgumentParser
from dataclasses import dataclass

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
    def __init__(self, network):
        self.network = network
        self.state = list(self.start())

    def __bool__(self):
        return not all(map(self.end, self.state))

    def step(self, direction):
        for (i, s) in enumerate(self.state):
            self.state[i] = self.network[s][direction]

    def start(self):
        raise NotImplementedError()

    def end(self):
        raise NotImplementedError()

class StandardState(NetworkState):
    def start(self):
        yield from (
            'AAA',
        )

    def end(self, key):
        return key == 'ZZZ'

class GhostState(NetworkState):
    def start(self):
        yield from filter(lambda x: x.endswith('A'), self.network)

    def end(self, key):
        return key.endswith('Z')

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

def walk(network, directions, state):
    for (i, d) in enumerate(it.cycle(directions), 1):
        state.step(d)
        if not state:
            return i
#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    directions = sys.stdin.readline().strip()
    network = dict(scanf(sys.stdin))

    _State = StandardState if args.version == 1 else GhostState
    state = _State(network)

    print(walk(network, directions, state))

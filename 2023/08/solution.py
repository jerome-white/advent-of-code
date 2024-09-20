import sys
import string
import itertools as it
from argparse import ArgumentParser
from dataclasses import dataclass

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

def scanf(fp):
    keep = set(string.ascii_uppercase + ' ')
    for line in fp:
        letters = ''.join(filter(lambda x: x in keep, line))
        if letters:
            (key, *values) = letters.split()
            node = Node(*values)
            yield (key, node)

def walk(network, directions, start='AAA', end='ZZZ'):
    for i in it.cycle(directions):
        start = network[start][i]
        yield start
        if start == end:
            break

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    directions = sys.stdin.readline().strip()
    network = dict(scanf(sys.stdin))

    print(sum(1 for _ in walk(network, directions)))

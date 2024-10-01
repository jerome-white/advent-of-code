import sys
import logging
import itertools as it

#
#
#
class Universe:
    @property
    def nrow(self):
        return len(self.sky)

    @property
    def ncol(self):
        return max(map(len, self.sky))

    def __init__(self, fp):
        self.sky = [ list(x.strip()) for x in fp ]

    def __str__(self):
        return '\n'.join(''.join(x) for x in self.sky)

    def expand(self):
        for E in (RowExpander, ColumnExpander):
            expander = E(self)
            expander()

#
#
#
class UniverseExpander:
    _empty = '.'

    def __init__(self, universe):
        self.universe = universe

    def __call__(self):
        i = 0
        while self.proceed(i):
            if all(self.empty(i)):
                self.insert(i)
                i += 2
            else:
                i += 1

    def proceed(self, loc):
        raise NotImplementedError()

    def empty(self, loc):
        raise NotImplementedError()

    def insert(self, loc):
        raise NotImplementedError()

class RowExpander(UniverseExpander):
    def proceed(self, loc):
        return loc < self.universe.nrow

    def empty(self, loc):
        yield from (x == self._empty for x in self.universe.sky[loc])

    def insert(self, loc):
        row = [ self._empty ] * self.universe.ncol
        self.universe.sky.insert(loc, row)

class ColumnExpander(UniverseExpander):
    def proceed(self, loc):
        return loc < self.universe.ncol

    def empty(self, loc):
        iterable = range(self.universe.nrow)
        yield from (self.universe.sky[x][loc] == self._empty for x in iterable)

    def insert(self, loc):
        for row in self.universe.sky:
            row.insert(loc, self._empty)

#
#
#
if __name__ == '__main__':
    universe = Universe(sys.stdin)
    universe.expand()
    print(universe)

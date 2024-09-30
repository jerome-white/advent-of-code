import sys

class Universe:
    _empty = '.'

    def __init__(self, fp):
        self.sky = [ list(x.strip()) for x in fp ]
        (self.nrow, self.ncol) = (len(self.sky), len(self.sky[0]))

    def __str__(self):
        return '\n'.join(''.join(x) for x in self.sky)

    def rows(self):
        r = 0
        while r < self.nrow:
            row = self.sky[r]
            if all(x == self._empty for x in row):
                row_ = [ self._empty ] * self.nrow
                self.sky.insert(r, row_)
                r += 2
            else:
                r += 1

    def cols(self):
        for i in range(self.ncol - 1, -1, -1):
            if all(self.sky[x][i] == self._empty for x in range(self.nrow)):
                for r in self.sky:
                    r.insert(i, '.')

    def expand(self):
        self.rows()
        self.cols()

if __name__ == '__main__':
    universe = Universe(sys.stdin)
    universe.expand()
    print(universe)

import sys
import string

from utils import Position, Digit, Part, Grid

class MyGrid(Grid):
    _ctrl = frozenset(string.digits + '.')

    def __init__(self, fp):
        grid = list(map(list, fp))
        shape = Position(*(len(x) - 1 for x in (grid, grid[0])))
        super().__init__(grid, shape)

    def is_part(self, digit):
        for i in digit.pos.around():
            if 0 <= i.row < self.shape.row and 0 <= i.col < self.shape.col:
                value = self.grid[i.row][i.col]
                if value not in self._ctrl:
                    return True

        return False

def parts(grid):
    part = Part()
    for (i, row) in enumerate(grid):
        part.clear()
        for (j, cell) in enumerate(row):
            if cell.isdigit():
                part.push(i, j, cell)
            elif part:
                if any(map(grid.is_part, part)):
                    yield int(part)
                part.clear()

if __name__ == '__main__':
    grid = MyGrid(sys.stdin)
    print(sum(parts(grid)))

import sys
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass, field

@dataclass
class Puzzle:
    rows: dict = field(default_factory=lambda: cl.defaultdict(list))
    cols: dict = field(default_factory=lambda: cl.defaultdict(list))

    @classmethod
    def from_txt(cls, fp):
        puzzle = cls()
        columns = cl.defaultdict(list)

        for (r, line) in enumerate(fp, 1):
            row = line.strip()
            puzzle.rows[row].append(r)
            for (c, cell) in enumerate(row, 1):
                columns[c].append(cell)

        for (k, v) in columns.items():
            col = ''.join(v)
            puzzle.cols[col].append(k)

        return puzzle

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    # arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    puzzle = Puzzle.from_txt(sys.stdin)

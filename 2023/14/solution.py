import sys
import logging
from argparse import ArgumentParser

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    panel = list(map(list, sys.stdin.read().splitlines()))
    (nrows, ncols) = map(len, (panel, panel[0]))

    (r_rock, c_rock, empty) = ('O', '#', '.')

    for c in range(ncols):
        for r in range(nrows):
            if panel[r][c] == empty:
                for i in range(r + 1, nrows):
                    cell = panel[i][c]
                    if cell != empty:
                        if cell == 'O':
                            (panel[r][c], panel[i][c]) = (
                                panel[i][c],
                                panel[r][c],
                            )
                        break

    total = 0
    for (i, row) in zip(range(nrows, 0, -1), panel):
        value = ''.join(row)
        total += value.count(r_rock) * i
        logging.warning(value)

    print(total)

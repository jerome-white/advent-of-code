import sys

if __name__ == '__main__':
    universe = []
    for line in sys.stdin:
        row = list(line.strip())
        universe.append(row)
        if all(x == '.' for x in row):
            universe.append(row.copy())

    (nrows, ncols) = (len(universe), len(universe[0]))
    for i in range(ncols - 1, -1, -1):
        if all(universe[x][i] == '.' for x in range(nrows)):
            for r in universe:
                r.insert(i, '.')

    print(*(''.join(x) for x in universe), sep='\n')

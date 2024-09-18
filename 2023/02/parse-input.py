import sys
import csv
import collections as cl

Record = cl.namedtuple('Record', [
    'game',
    'grab',
    'color',
    'count',
])

def records(fp):
    for i in fp:
        line = i.strip()
        (index, plays) = line.split(':')

        (_, game) = index.split()
        for (grab, cubes) in enumerate(plays.split(';')):
            for c in cubes.split(','):
                (cnt, clr) = c.split()
                record = Record(game, grab, clr, cnt)
                yield record

if __name__ == '__main__':
    fieldnames = list(Record._fields)
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(x._asdict() for x in records(sys.stdin))

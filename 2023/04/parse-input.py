import sys
import csv
import collections as cl

Record = cl.namedtuple('Record', [
    'card',
    'winning',
    'value',
])

def records(fp):
    for i in fp:
        line = i.strip()
        (index, numbers) = line.split(':')

        (_, card) = index.split()
        for (i, n) in enumerate(numbers.split('|')):
            winning = int(not i)
            for v in n.split():
                if v:
                    yield Record(card, winning, v)

if __name__ == '__main__':
    fieldnames = list(Record._fields)
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(x._asdict() for x in records(sys.stdin))

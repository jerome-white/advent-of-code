import csv

class Step:
    def __init__(self, step):
        self.step = step

    def __str__(self):
        return self.step

    def __eq__(self, other):
        return self.step == other.step

    def __hash__(self):
        current = 0
        for s in self.step:
            current += ord(s)
            current *= 17
            current %= 256

        return current

def scanf(fp):
    reader = csv.reader(fp)
    for row in reader:
        yield from row

import csv
from dataclasses import dataclass

@dataclass
class Step:
    step: str

    def __str__(self):
        return self.step

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

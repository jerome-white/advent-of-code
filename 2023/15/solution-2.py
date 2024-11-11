import sys
import logging
import functools as ft
import itertools as it
import collections as cl

from utils import Step, scanf

#
#
#
class SubtractiveStep(Step):
    def __init__(self, step, *args):
        super().__init__(step)

class AdditiveStep(Step):
    def __init__(self, step, *args):
        super().__init__(step)
        (focal_length, ) = args
        self.focal_length = int(focal_length)

    def __str__(self):
        return f'{self.step} {self.focal_length}'

#
#
#
class Boxes:
    def __init__(self):
        self.lenses = cl.defaultdict(list)

    def __iter__(self):
        for l in sorted(self.lenses):
            lenses = self.lenses[l]
            if lenses:
                yield (l, lenses)

    def __int__(self):
        fpower = 0
        for (b, lenses) in self:
            box = 1 + b
            for (i, l) in enumerate(lenses, 1):
                fpower += box * i * l.focal_length

        return fpower

    def boxes(self):
        for (b, lenses) in self:
            yield '{} {}'.format(b, ' '.join(map('[{}]'.format, lenses)))

    @ft.singledispatchmethod
    def update(self, step):
        raise TypeError(type(step))

    @update.register
    def _(self, step: SubtractiveStep):
        bucket = self.lenses[hash(step)]
        if bucket:
            try:
                bucket.remove(step)
            except ValueError:
                pass

    @update.register
    def _(self, step: AdditiveStep):
        bucket = self.lenses[hash(step)]
        try:
            index = bucket.index(step)
            bucket[index] = step
        except ValueError:
            bucket.append(step)

#
#
#
def steps(scan):
    dtypes = {
        '=': AdditiveStep,
        '-': SubtractiveStep,
    }

    for s in scan:
        for (k, v) in dtypes.items():
            if s.find(k) >= 0:
                (name, *args) = s.split(k)
                yield v(name, *args)
                break
        else:
            raise ValueError(s)

if __name__ == '__main__':
    boxes = Boxes()

    for s in steps(scanf(sys.stdin)):
        index = hash(s)
        boxes.update(s)

    if logging.isEnabledFor(logging.INFO):
        for r in boxes.boxes():
            logging.info(r)

    print(int(boxes))

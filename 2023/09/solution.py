import sys
import logging
import operator as op
import itertools as it
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

class Sensor:
    def __init__(self, combine, index):
        self.combine = combine
        self.index = index

    def __call__(self, values):
        if not any(values):
            return 0

        iterable = zip(values, it.islice(values, 1, None))
        values_ = [ y - x for (x, y) in iterable ]

        return self.combine(values[self.index], self(values_))

class RightSensor(Sensor):
    def	__init__(self):
        super().__init__(op.add, -1)

class LeftSensor(Sensor):
    def	__init__(self):
        super().__init__(op.sub, 0)

#
#
#
def func(incoming, outgoing, version):
    sensor = RightSensor() if version == 1 else LeftSensor()

    while True:
        values = incoming.get()

        answer = sensor(values)
        logging.warning(f'{values}: {answer}')

        outgoing.put(answer)

def extrapolate(args, fp):
    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args.version,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for line in fp:
            values = list(map(int, line.strip().split()))
            outgoing.put(values)
            jobs += 1

        for _ in range(jobs):
            answer = incoming.get()
            yield answer

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    print(sum(extrapolate(args, sys.stdin)))

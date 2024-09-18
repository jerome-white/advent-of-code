import sys
import logging
import collections as cl
from argparse import ArgumentParser

import pandas as pd

def scratch(df):
    counts = (df
              .groupby('winning', sort=False)['value']
              .value_counts())
    (guess, win) = (counts[x].to_dict() for x in range(2))

    for (k, v) in guess.items():
        for _ in range(v):
            if k in win and win[k] > 0:
                win[k] -= 1
                yield 1

class ScratchCardGame:
    def __init__(self, df):
        self.df = df

    def __call__(self):
        for (c, g) in self.df.groupby('card'):
            logging.info(c)
            points = sum(scratch(g))
            yield self.tally(c, points)

    def tally(self, card, points):
        raise NotImplementedError()

class PointScratcher(ScratchCardGame):
    def	tally(self, card, points):
        if points:
            points = 2 ** (points - 1)

        return points

class CardScratcher(ScratchCardGame):
    def __init__(self, df):
        super().__init__(df)
        self.counts = cl.Counter(df['card'].unique())

    def tally(self, card, match):
        start = card + 1
        copies = self.counts[card]
        for i in range(start, start + match):
            self.counts[i] += copies

        return copies

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    MyScratcher = PointScratcher if args.version == 1 else CardScratcher

    df = pd.read_csv(sys.stdin)
    scratcher = MyScratcher(df)
    print(sum(scratcher()))

import sys
import logging
import operator as op
import functools as ft
from argparse import ArgumentParser
from dataclasses import dataclass, fields
from multiprocessing import Pool, Queue

import pandas as pd

#
#
#
@dataclass
class Grab:
    red: int
    blue: int
    green: int

    def __le__(self, other):
        for i in fields(self):
            (left, right) = (getattr(x, i.name) for x in (self, other))
            if left > right:
                return False

        return True

    @classmethod
    def from_tuple(cls, tup):
        kwargs = { x.name: getattr(tup, x.name) for x in fields(cls) }
        return cls(**kwargs)

#
#
#
class PuzzleHandler:
    def __call__(self, df):
        raise NotImplementedError()

    def play(self, game, df, query):
        raise NotImplementedError()

class PossibleGames(PuzzleHandler):
    def __call__(self, df):
        (game, possible) = ('game', 'possible')
        return (df
                .groupby(game)[possible]
                .all()
                .reset_index()
                .query(possible)[game]
                .sum())

    def play(self, game, df, query):
        df = df.pivot_table(
            index='grab',
            columns='color',
            values='count',
            fill_value=0,
        )
        for i in df.itertuples():
            grab = Grab.from_tuple(i)
            yield {
                'game': game,
                'grab': i.Index,
                'possible': grab <= query,
            }

class CubePower(PuzzleHandler):
    def __call__(self, df):
        return (df
                .drop(columns='game')
                .apply(lambda x: ft.reduce(op.mul, x), axis='columns')
                .sum())

    def play(self, game, df, query):
        result = (df
                  .groupby('color')['count']
                  .max()
                  .to_dict())
        result['game'] = game
        yield result

#
#
#
def func(incoming, outgoing, handler, query):
    while True:
        (game, df) = incoming.get()
        logging.info(game)

        results = handler.play(game, df, query)
        outgoing.put(list(results))

def play(args, handler, fp):
    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        handler,
        Grab.from_tuple(args),
    )

    with Pool(args.workers, func, initargs):
        groups = (pd
                  .read_csv(fp)
                  .groupby('game', sort=False))
        for i in groups:
            outgoing.put(i)

        for _ in range(groups.ngroups):
            results = incoming.get()
            yield from results

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    for i in fields(Grab):
        option = f'--{i.name}'
        arguments.add_argument(option, type=int, default=0)
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    handler = PossibleGames() if args.version == 1 else CubePower()
    records = play(args, handler, sys.stdin)
    df = pd.DataFrame.from_records(records)
    print(handler(df))

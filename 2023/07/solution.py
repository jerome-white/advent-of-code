import sys
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

#
#
#
@dataclass
class Hand:
    cards: list
    order: int

    def __lt__(self, other):
        if isinstance(other, type(self)):
            for (i, j) in zip(self.cards, other.cards):
                if i != j:
                    return i < j
            return False

        return self.order < other.order

@dataclass
class FiveOfaKind(Hand):
    pass

@dataclass
class FourOfaKind(Hand):
    pass

@dataclass
class ThreeOfaKind(Hand):
    pass

@dataclass
class FullHouse(Hand):
    pass

@dataclass
class TwoPair(Hand):
    pass

@dataclass
class OnePair(Hand):
    pass

@dataclass
class HighCard(Hand):
    pass

#
#
#
class HandBuilder:
    _dtypes = {
        '5':     FiveOfaKind,
        '41':    FourOfaKind,
        '32':    FullHouse,
        '311':   ThreeOfaKind,
        '221':   TwoPair,
        '2111':  OnePair,
        '11111': HighCard,
    }

    def __init__(self):
        self.fill = max(map(len, self._dtypes))

    def __call__(self, cards):
        counts = cl.Counter(cards)
        encoding = ''.join(str(y) for (_, y) in counts.most_common())

        order = encoding
        short = self.fill - len(order)
        if short:
            order += '0' * short

        return self._dtypes.get(encoding)(
            cards,
            int(order),
        )

#
#
#
class CardBuilder:
    _numbers = range(2, 10)
    _symbols = (
        'A',
        'K',
        'Q',
        'J',
        'T',
    )

    def __init__(self):
        self.values = { str(x): x for x in self._numbers }
        start = max(self._numbers) + 1
        iterable = enumerate(reversed(self._symbols), start)
        self.values.update(map(reversed, iterable))

    def __call__(self, cstring):
        yield from map(self.values.get, cstring)

#
#
#
@dataclass
class CamelCard:
    hand: Hand
    bid: int

    def __lt__(self, other):
        return self.hand < other.hand

#
#
#
def scanf(fp):
    cbuilder = CardBuilder()
    hbuilder = HandBuilder()

    for line in fp:
        (values, bid) = line.strip().split()
        hand = hbuilder(tuple(cbuilder(values)))

        yield CamelCard(hand, int(bid))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    game = sorted(scanf(sys.stdin))
    print(sum(x * y.bid for (x, y) in enumerate(game, 1)))

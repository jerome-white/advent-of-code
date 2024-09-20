import sys
import collections as cl
from argparse import ArgumentParser
from dataclasses import dataclass

#
#
#
class CardBuilder:
    (_low, _high) = (2, 9)

    @property
    def joker(self):
        return 'J'

    def __init__(self, joker=False):
        high = self._high + 1
        symbols = [ # reversed to make enumeration work
            'T',
            'Q',
            'K',
            'A',
        ]

        self.values = { str(x): x for x in range(self._low, high) }
        if joker:
            self.values[self.joker] = self._low - 1
        else:
            symbols.insert(1, self.joker)
        self.values.update(map(reversed, enumerate(symbols, high)))

    def __call__(self, cstring):
        yield from map(self.values.get, cstring)

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

    def __init__(self, cbuilder):
        self.cbuilder = cbuilder
        self.fill = max(map(len, self._dtypes))

    def __call__(self, cards):
        counts = cl.Counter(self.remap(cards))
        encoding = ''.join(str(y) for (_, y) in counts.most_common())

        order = encoding
        short = self.fill - len(order)
        if short:
            order += '0' * short

        return self._dtypes.get(encoding)(
            tuple(self.cbuilder(cards)),
            int(order),
        )

    def remap(self, cards):
        raise NotImplementedError()

class StandardHand(HandBuilder):
    def remap(self, cards):
        return cards

class JokerHand(HandBuilder):
    def remap(self, cards):
        if self.cbuilder.joker in cards:
            counts = cl.Counter(cards)
            for (c, _) in counts.most_common():
                if c != self.cbuilder.joker:
                    cards = cards.replace(self.cbuilder.joker, c)
                    break

        return cards

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
def scanf(args, fp):
    _Hand = StandardHand if args.version == 1 else JokerHand
    hbuilder = _Hand(CardBuilder(args.version == 2))

    for line in fp:
        (values, bid) = line.strip().split()
        hand = hbuilder(values)

        yield CamelCard(hand, int(bid))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    game = sorted(scanf(args, sys.stdin))
    print(sum(x * y.bid for (x, y) in enumerate(game, 1)))

import sys
from argparse import ArgumentParser

#
#
#
class DigitParser:
    def __call__(self, word):
        raise NotImplementedError()

class NumericDigitParser(DigitParser):
    def __call__(self, word):
        yield from map(int, filter(lambda x: x.isdigit(), word))

class AlphaNumericDigitParser(DigitParser):
    _numbers = {
        'one':   1,
        'two':   2,
        'three': 3,
        'four':  4,
        'five':  5,
        'six':   6,
        'seven': 7,
        'eight': 8,
        'nine':  9,
    }

    def __init__(self):
        super().__init__()
        self.numbers = { str(x): x for x in self._numbers.values() }
        self.numbers.update(self._numbers)

    def __call__(self, word):
        while word:
            for (k, v) in self.numbers.items():
                if word.startswith(k):
                    yield v
                    break
            word = word[1:]

#
#
#
def extract(fp, parser):
    for i in fp:
        line = i.strip()
        words = list(parser(line))
        if words:
            yield words

def combine(words):
    for w in words:
        if len(w) == 1:
            w *= 2
        text = ''.join(str(w[x]) for x in (0, -1))
        yield int(text)

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    if args.version == 1:
        parser = NumericDigitParser()
    else:
        parser = AlphaNumericDigitParser()

    print(sum(combine(extract(sys.stdin, parser))))

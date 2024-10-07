import re
import sys
import logging
import collections as cl
from dataclasses import dataclass

@dataclass
class ConditionRecord:
    springs: str
    layout: tuple

    def simplify(self):
        (temp, pound) = ('-', '#')
        assert temp not in self.springs
        layout = []
        counts = cl.Counter(self.layout)

        springs = self.springs
        for (k, v) in counts.items():
            # gpt-4o prompt:
            #  Write a regular expression using Python's re library
            #  that does the following:
            #  * match "#" i number of times
            #  * matches "?" or "." or the beginning of the string on
            #    the left side
            #  * matches "?" or "." or the end of the string on the
            #    right side
            #  Make sure the pattern avoids look-behind errors
            regex = f'(?:^|[?.]){pound}{{{k}}}(?:[?.]|$)'

            res = list(re.finditer(regex, springs))
            if len(res) == v:
                for r in res:
                    (left, right) = r.span()
                    middle = (springs[left:right]
                              .replace(pound, temp)
                              .replace('?', '.'))
                    springs = substitute(springs, middle, left, right)
            else:
                layout.extend(k for _ in range(v))
        springs = springs.replace(temp, pound)

        return type(self)(springs, tuple(layout))

class ArrangementIterator:
    def __init__(self, record):
        self.record = record
        self.counts = cl.Counter(self.record.layout)

    def __str__(self):
        return str(self.record)

    def __iter__(self):
        record = self.record.simplify()
        yield from self(record.springs, record.layout)

    def __call__(self, springs, layout):
        if not layout:
            s = springs.replace('?', '.')
            if self.accept(s):
                yield s
        else:
            (head, *tail) = layout
            pounds = '#' * head
            for m in re.finditer(f'[^.]{{{head}}}', springs):
                s = substitute(springs, pounds, *m.span())
                yield from self(s, tail)

    def accept(self, springs):
        counts = cl.Counter(map(len, filter(None, springs.split('.'))))
        return counts == self.counts

def substitute(word, replacement, left, right):
    return f'{word[:left]}{replacement}{word[right:]}'

def records(fp):
    for line in fp:
        (springs, layout) = line.strip().split()
        layout = tuple(map(int, layout.split(',')))
        yield ConditionRecord(springs, layout)

if __name__ == '__main__':
    for r in records(sys.stdin):
        aitr = ArrangementIterator(r)
        arrangements = set(aitr)
        logging.critical(f'{r} {len(arrangements)}')

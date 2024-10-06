import re
import sys
import collections as cl
from dataclasses import dataclass

@dataclass
class ConditionRecord:
    springs: str
    layout: tuple

    def simplify(self):
        (temp, pound) = ('-', '#')
        assert temp not in self.springs
        counts = cl.Counter(self.layout)
        layout = []

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
                    springs = f'{springs[:left]}{middle}{springs[right:]}'
            else:
                layout.extend(k for _ in range(v))
        springs = springs.replace(temp, pound)

        return type(self)(springs, tuple(layout))

def records(fp):
    for line in fp:
        (springs, layout) = line.strip().split()
        layout = tuple(map(int, layout.split(',')))

        yield ConditionRecord(springs, layout)

if __name__ == '__main__':
    for r in records(sys.stdin):
        print(r, r.simplify(), '', sep='\n')

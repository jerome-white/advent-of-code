import re
import sys
from dataclasses import dataclass

@dataclass
class ConditionRecord:
    springs: str
    layout: tuple

    def simplify(self):
        (temp, pound) = ('-', '#')
        assert temp not in self.springs
        layout = []

        springs = self.springs
        for i in self.layout:
            # gpt-4o prompt:
            #  Write a regular expression using Python's re library
            #  that does the following:
            #  * match "#" i number of times
            #  * matches "?" or "." or the beginning of the string on
            #    the left side
            #  * matches "?" or "." or the end of the string on the
            #    right side
            #  Make sure the pattern avoids look-behind errors
            res = re.search(f'(?:^|[?.]){pound}{{{i}}}(?:[?.]|$)', springs)

            if res is None:
                layout.append(i)
            else:
                (left, right) = res.span()
                middle = (springs[left:right]
                          .replace(pound, temp)
                          .replace('?', '.'))
                springs = f'{springs[:left]}{middle}{springs[right:]}'
        springs = springs.replace(temp, pound)

        return type(self)(springs, tuple(layout))

def records(fp):
    for line in fp:
        (springs, layout) = line.strip().split()
        layout = tuple(map(int, layout.split(',')))

        yield ConditionRecord(springs, layout)

if __name__ == '__main__':
    for r in records(sys.stdin):
        print(r, r.simplify(), sep='\n')

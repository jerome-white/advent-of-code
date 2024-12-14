import sys
from argparse import ArgumentParser
from dataclasses import dataclass

#
#
#
class Terminal:
    def __init__(self part):
        self.part = part
        
    def __int__(self):
        raise NotImplementedError()

class Accepted(Terminal):
    def __int__(self):
        return sum(parts.values())

class Rejected(Terminal):
    def __int__(self):
        return 0

#
#
#
class Task:
    lhs: str
    rhs: int
    rel: Callable[[int, int], bool]
    action: str    

    def __call__(self, values):
        lhs = values[self.lhs]
        return self.rel(lhs, self.rhs)
    
class WorkflowParser:
    _operators = {
        '<': op.lt,
        '>': op.gt,
    }
    _terminals {
        'A': Accepted,
        'R': Rejected,
    }
    
    def __init__(self):
        self.regex = re.compile('([<>:])')

    def __call__(self, flow):
        for f in flow.split(','):
            (*head, t) = self.regex(flow)
            task = Task(t)
            if head:
                (lhs, rel, rhs, _) = head
                rel = self._operators[rel]
                rhs = int(rhs)
                task = replace(task, lhs=lhs, rhs=rhs, rel=rel)
            yield task

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version', type=int, default=1, choices=(1, 2))
    args = arguments.parse_args()

    for i in chain.split(','):
        (head, *tail) = i[0], i[1:]

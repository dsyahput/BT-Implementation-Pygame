from enum import Enum

class Status(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3

class Node:
    def tick(self):
        raise NotImplementedError()

class Sequence(Node):
    def __init__(self, children):
        self.children = children
        self.current = 0

    def tick(self):
        while self.current < len(self.children):
            status = self.children[self.current].tick()
            if status == Status.RUNNING:
                return Status.RUNNING
            if status == Status.FAILURE:
                self.current = 0
                return Status.FAILURE
            self.current += 1
        self.current = 0
        return Status.SUCCESS

class Selector(Node):
    def __init__(self, children):
        self.children = children
        self.current = 0

    def tick(self):
        while self.current < len(self.children):
            status = self.children[self.current].tick()
            if status == Status.RUNNING:
                return Status.RUNNING
            if status == Status.SUCCESS:
                self.current = 0
                return Status.SUCCESS
            self.current += 1
        self.current = 0
        return Status.FAILURE

class Repeater(Node):
    def __init__(self, child):
        self.child = child

    def tick(self):
        self.child.tick()
        return Status.RUNNING

class Condition(Node):
    def __init__(self, func):
        self.func = func

    def tick(self):
        return Status.SUCCESS if self.func() else Status.FAILURE

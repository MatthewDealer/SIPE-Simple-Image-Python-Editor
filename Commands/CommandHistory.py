from Commands.Command import *

class CommandHistory:
    def __init__(self, max_stack):
        self.history = []
        self.max_stack = max_stack

    def pop(self):
        return self.history.pop()

    def push(self, command: Command):
        self.history.append(command)

    def isEmpty(self) -> bool:
        if not self.history:
            return True
        else:
            return False

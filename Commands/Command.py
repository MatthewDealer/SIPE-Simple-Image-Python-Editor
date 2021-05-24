from abc import ABC, abstractmethod
from Editor import *
import copy


class Command(ABC):
    def __init__(self, editor):
        self.editor = editor
        self.index = copy.deepcopy(self.editor.selected_canvas_index)
        self._back_up = copy.deepcopy(self.editor.canvas_list[self.index])

    @abstractmethod
    def execute(self) -> bool:
        pass

    def backUp(self):
        self.index = self.editor.selected_canvas_index
        self._back_up = self.editor.canvas_list[self.index]

    def undo(self):
        self.editor.canvas_list[self.index] = self._back_up

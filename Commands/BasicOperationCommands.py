from Commands.Command import *
import copy

class NewLayerCommand(Command):
    def __init__(self, editor, r, g, b):
        super().__init__(editor)
        self.r = r
        self.g = g
        self.b = b

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].addNewLayer(self.r, self.g, self.b)
        self.editor.selected_layer_index = len(self.editor.canvas_list[self.editor.selected_canvas_index].layers_list)-1
        return True

class RenameLayerCommand(Command):
    def __init__(self, editor, new_name):
        super().__init__(editor)
        self.new_name = new_name

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index].setName(self.new_name)
        return True

class DeleteLayerCommand(Command):
    def execute(self):
        self.editor.deleteLayer()
        return True

class MoveLayerUpCommand(Command):
    def execute(self):
        self.editor.moveLayerUp()
        return True

class MoveLayerDownCommand(Command):
    def execute(self):
        self.editor.moveLayerDown()
        return True

class ChangeLayerModeCommand(Command):
    def __init__(self, editor, value):
        super().__init__(editor)
        self.value = value

    def execute(self):
        self.editor.setMode(self.value)
        return True

class ChangeLayerPositionCommand(Command):
    def __init__(self, editor, value_x, value_y):
        super().__init__(editor)
        self.x = value_x
        self.y = value_y

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index].setPosition(self.x, self.y)
        return True

class ChangeLayerRotationCommand(Command):
    def __init__(self, editor, value_r,):
        super().__init__(editor)
        self.r = value_r

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index].setRotation(self.r)
        return True

class ChangeLayerScaleCommand(Command):
    def __init__(self, editor, value_width, value_height):
        super().__init__(editor)
        self.width = value_width
        self.height = value_height

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index].setScale(self.width, self.height)
        return True

class OpenImageCommand(Command):
    def __init__(self, editor, data_name,  data_image):
        super().__init__(editor)
        self.name = data_name
        self.data = data_image

    def execute(self):
        self.editor.canvas_list[self.editor.selected_canvas_index].newLayerFromImage(self.name, self.data)
        return True

class DuplicateLayerCommand(Command):
    def execute(self):
        layer = copy.deepcopy(self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index])
        layer.name = layer.name + "-copy"
        self.editor.canvas_list[self.editor.selected_canvas_index].layers_list.append(layer)
        return True

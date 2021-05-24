from Commands.Command import *

class RenderEffectCommand(Command):
    def __init__(self, editor, module_name,  module_path):
        super().__init__(editor)
        self.module_name = module_name
        self.module_path = module_path
        print(module_name)
        print(module_path)
        spec = importlib.util.spec_from_file_location(self.module_name, self.module_path)
        module = importlib.util.module_from_spec(spec)
        self.effect = module
        spec.loader.exec_module(module)
        print(self.effect)

    def execute(self):
        layer = self.editor.canvas_list[self.editor.selected_canvas_index].layers_list[self.editor.selected_layer_index]
        done_effect = self.effect.effect(layer.data)
        layer.data = done_effect
        return True
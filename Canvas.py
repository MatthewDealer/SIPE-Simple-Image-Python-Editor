import numpy as np
from PIL import Image

from Layer import Layer, Mode

DEFAULT_NAME = "Layer"


class Canvas:
    def __init__(self, canvas_name, first_layer=None, width=0, height=0):
        self.name = canvas_name
        self.layers_list = []
        self.canvas_width = width
        self.canvas_height = height
        self.bg = self.drawBg()
        if first_layer is None:
            self.addNewLayer(255, 255, 255)
        else:
            first = first_layer.convert("RGBA")
            name = DEFAULT_NAME + str(len(self.layers_list))
            self.layers_list.append(Layer(name, first, self.canvas_width, self.canvas_height, Mode.NORMAL))

    def drawBg(self):
        bg = Image.open("img/bg.png").convert("RGBA")  # resize?

        bg_w, bg_h = bg.size

        new_im = Image.new('RGBA', (self.canvas_width, self.canvas_height))

        w, h = new_im.size

        for i in range(0, w, bg_w):
            for j in range(0, h, bg_h):
                new_im.paste(bg, (i, j))

        return new_im

    def newLayerFromImage(self, name, layer_data):
        self.layers_list.append(Layer(name, layer_data.convert("RGBA"), self.canvas_width, self.canvas_height))

    def addNewLayer(self, r, g, b):
        color_array = np.ones((self.canvas_height, self.canvas_width, 3))
        color_array[:, :, 0] = color_array[:, :, 0] * r
        color_array[:, :, 1] = color_array[:, :, 1] * g
        color_array[:, :, 2] = color_array[:, :, 2] * b
        new_layer = Image.fromarray(np.uint8(color_array)).convert("RGBA")
        name = DEFAULT_NAME + str(len(self.layers_list))
        self.layers_list.append(Layer(name, new_layer, self.canvas_width, self.canvas_height))

    def getPreview(self) -> Image:
        final_array = Image.alpha_composite(self.bg, self.getFinalImage())

        return final_array

    def getFinalImage(self) -> Image:
        final_array = Image.fromarray(np.uint8(np.zeros((self.canvas_height, self.canvas_width, 4))))
        for layer in self.layers_list:
            if self.layers_list.index(layer) == 0:
                final_array = Image.alpha_composite(final_array, layer.getCanvasImage())
            else:
                if layer.mode == Mode.NORMAL:
                    final_array = Image.alpha_composite(final_array, layer.getCanvasImage())
                if layer.mode == Mode.DARKER:
                    result_layer = Image.fromarray(np.uint8(np.minimum(np.array(final_array), layer.getCanvasMatrix())))
                    final_array = Image.alpha_composite(final_array, result_layer)
                if layer.mode == Mode.MULTIPLY:
                    result_layer = np.multiply(np.array(final_array, dtype=float) / 255,
                                               np.array(layer.getCanvasMatrix(), dtype=float) / 255)
                    final_array = Image.alpha_composite(final_array, Image.fromarray(np.uint8(result_layer * 255)))
                if layer.mode == Mode.ADD:
                    result_layer = np.clip(
                        np.array(final_array, dtype=float) / 255 + np.array(layer.getCanvasMatrix(), dtype=float) / 255,
                        0, 1)
                    final_array = Image.alpha_composite(final_array, Image.fromarray(np.uint8(result_layer * 255)))
                if layer.mode == Mode.LIGHTER:
                    result_layer = Image.fromarray(np.uint8(np.maximum(np.array(final_array), layer.getCanvasMatrix())))
                    final_array = Image.alpha_composite(final_array, result_layer)

        return final_array

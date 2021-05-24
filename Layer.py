import numpy as np
from PIL import ImageTk, Image
from enum import Enum


class Mode(Enum):
    NORMAL = 1
    DARKER = 2
    MULTIPLY = 3
    ADD = 4
    LIGHTER = 5


class Layer:
    def __init__(self, layer_name, data: Image, canvas_width, canvas_height, mode=Mode.NORMAL):
        self.name = layer_name
        self.original_save = data
        self.data = data
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.rotation = 0
        self.width, self.height = self.data.size
        self.position_x = round(self.width/2)
        self.position_y = round(self.height/2)
        self.mode = mode

    def setName(self, new_name):
        self.name = new_name

    def getName(self):
        return self.name

    def setMode(self, value):
        self.mode = Mode(value)

    def setPosition(self, new_x, new_y):
        self.position_x = new_x
        self.position_y = new_y
        return True

    def setScale(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.data = self.data.resize((self.width, self.height))
        return True

    def setRotation(self, new_rotation):
        self.rotation = new_rotation
        self.data = self.original_save.rotate((-1)*self.rotation)
        self.width, self.height = self.data.size

    def getCanvasImage(self):
        return Image.fromarray(np.uint8(self.getCanvasMatrix()))

    def getCanvasMatrix(self):
        temp_image = np.zeros((self.canvas_height, self.canvas_width, 4))
        #print("__________________________________________________________")
        #print("Position x: %s, y: %s" % (self.position_x, self.position_y))
        #print("Image shape: %s x %s" % (self.width, self.height))
        #print("Canvas shape: %s x %s" % (self.canvas_width, self.canvas_height))
        ###Select Canvas Active Area
        w_start = min(max(0, self.position_y-round(self.height/2)), self.canvas_height)
        w_end = max(0, min(self.canvas_height, self.position_y+round(self.height/2)))
        h_start = min(max(0, self.position_x - round(self.width/2)), self.canvas_width)
        h_end = max(0, min(self.canvas_width, self.position_x+round(self.width/2)))
        #print("Canvas area y from %s to %s, x from %s to %s" % (w_start, w_end, h_start, h_end))

        ###Select Active Image Area
        iw_start = max(0, self.height - self.position_y - round(self.height/2))
        iw_end = min(self.height, self.canvas_height - self.position_y + round(self.height/2))
        ih_start = max(0, self.width - self.position_x - round(self.width/2))
        ih_end = min(self.width, self.canvas_width - self.position_x + round(self.width/2))
        #print("Img area y from %s to %s, x from %s to %s" % (iw_start, iw_end, ih_start, ih_end))
        #print("__________________________________________________________")

        temp_image[w_start:w_end, h_start:h_end] = np.array(self.data)[iw_start:iw_end, ih_start:ih_end]

        return temp_image

    def getIcon(self):
        img_width, img_height = self.data.size
        return ImageTk.PhotoImage(image=self.data.resize((round(32/img_height*img_width), 32)))
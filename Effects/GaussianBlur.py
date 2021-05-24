from PIL import Image, ImageFilter
import tkinter.simpledialog as simpleDialog

class MyGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"
    def __init__(self, radius=2):
        self.radius = radius
    def filter(self, image):
        return image.gaussian_blur(self.radius)


def effect(image_data) -> Image:
    x = int(simpleDialog.askstring("Gaussian Blur", "Enter value:"))
    img = image_data.filter(MyGaussianBlur(radius=x))
    img = img.convert("RGBA")
    return img

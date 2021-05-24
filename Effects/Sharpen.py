from PIL import Image, ImageFilter
from PIL.ImageFilter import SHARPEN
import tkinter.simpledialog as simpleDialog


def effect(image_data) -> Image:
    img = image_data.filter(SHARPEN)
    img = img.convert("RGBA")
    return img
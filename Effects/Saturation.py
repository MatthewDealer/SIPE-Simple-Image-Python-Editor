from PIL import Image, ImageEnhance
import tkinter.simpledialog as simpleDialog


def effect(image_data) -> Image:
    x = float(simpleDialog.askstring("Saturation", "Enter value (0-1):"))
    img = image_data
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(x)
    img = img.convert("RGBA")
    return img
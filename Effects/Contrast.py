from PIL import Image, ImageEnhance
import tkinter.simpledialog as simpleDialog


def effect(image_data) -> Image:
    x = float(simpleDialog.askstring("Contrast", "Enter value :"))
    img = image_data
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(x)
    img = img.convert("RGBA")
    return img
from PIL import Image

def effect(image_data) -> Image:
    img = image_data.convert("L")
    img = img.convert("RGBA")
    return img
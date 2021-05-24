from PIL import Image, ImageDraw
from tkinter import colorchooser

def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


def gradient(width, height, color_one, color_two):
    im = Image.new('RGBA', (width, height), color=0)
    my_gradient = Image.new('RGBA', (width, height), color=0)
    draw = ImageDraw.Draw(my_gradient)

    f_co = color_one
    t_co = color_two
    for i, color in enumerate(interpolate(f_co, t_co, im.width * 2)):
        draw.line([(i, 0), (0, i)], tuple(color), width=1)
    im_composite = Image.alpha_composite(my_gradient, im)
    return im_composite


def effect(image_data) -> Image:
    color_code_one = colorchooser.askcolor(title="Choose color one")[0]
    color_code_two = colorchooser.askcolor(title="Choose color two")[0]
    width, height = image_data.size
    img = gradient(width, height, color_code_one, color_code_two)
    img = img.convert("RGBA")
    return img
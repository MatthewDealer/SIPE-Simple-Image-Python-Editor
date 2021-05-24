from PIL import Image
import cv2
import numpy as np
from scipy import ndimage


def effect(image_data) -> Image:
    opencv_image = cv2.cvtColor(np.array(image_data), cv2.COLOR_RGBA2GRAY)

    opencv_image = ndimage.sobel(opencv_image)

    color_converted= cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(color_converted).convert("RGBA")

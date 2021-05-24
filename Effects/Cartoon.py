from PIL import Image
import cv2
import numpy as np


def effect(image_data) -> Image:
    opencv_image = cv2.cvtColor(np.array(image_data), cv2.COLOR_RGBA2BGR)

    opencv_image = cv2.stylization(opencv_image, sigma_s=60, sigma_r=0.6)

    color_converted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(color_converted).convert("RGBA")
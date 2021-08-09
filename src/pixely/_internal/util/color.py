# ========================= #
# PIXELY COLOR UTILITY      #
# ========================= #

from cv2 import cvtColor, COLOR_RGB2HSV, COLOR_HSV2RGB
import numpy as np

def rgb_to_hsv(color):
    """
    Convert an RGB input color to HSV.
    """
    color = np.uint8([[color]])
    return cvtColor(color,COLOR_RGB2HSV)[0][0]

def hsv_to_rgb(color: list):
    """
    Convert an HSV input color to RGB.
    """
    color = np.uint8([[color]])
    return cvtColor(color,COLOR_HSV2RGB)[0][0]
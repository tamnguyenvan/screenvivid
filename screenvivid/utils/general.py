import os
import tempfile
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np


def str2bool(x: str) -> bool:
    x = x.lower()
    return x == "true" or x == "1"

def generate_video_path(prefix: str = "ScreenVivid", extension: str = ".mp4"):
    # Use the system"s temporary directory
    root = Path(tempfile.gettempdir())

    # Create a unique file name using current datetime
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{prefix}_{time_str}{extension}"

    # Generate the full path
    return str(root / file_name)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


def create_gradient_image(width, height, first_color, second_color, angle):
    first_color = hex_to_rgb(first_color)
    second_color = hex_to_rgb(second_color)

    angle_rad = np.radians(angle)

    x, y = np.meshgrid(np.arange(width), np.arange(height))

    gradient = (x * np.cos(angle_rad) + y * np.sin(angle_rad)) / np.sqrt(width**2 + height**2)

    gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min())

    r = (second_color[0] - first_color[0]) * gradient + first_color[0]
    g = (second_color[1] - first_color[1]) * gradient + first_color[1]
    b = (second_color[2] - first_color[2]) * gradient + first_color[2]

    gradient_image = np.dstack((b, g, r)).astype(np.uint8)

    return gradient_image


def find_largest_leq_sorted(arr, x):
    if len(arr) == 0:
        return -1

    idx = np.searchsorted(arr, x, side="right") - 1

    if idx >= 0 and arr[idx] <= x:
        return idx
    else:
        return -1


def find_smallest_geq_sorted(arr, x):
    if len(arr) == 0:
        return -1

    idx = np.searchsorted(arr, x, side="left")

    if idx < len(arr) and arr[idx] >= x:
        return idx
    else:
        return -1

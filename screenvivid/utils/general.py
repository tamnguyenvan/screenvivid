import sys
import os
import platform
import tempfile
from pathlib import Path
from datetime import datetime

import numpy as np
from screenvivid.utils.logging import logger

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

def get_os_name():
    system_code = platform.system().lower()
    os_name = "unknown"
    if system_code == "windows":
        os_name = "windows"
    elif system_code == "linux":
        os_name = "linux"
    elif system_code == "darwin":
        os_name = "macos"
    return os_name

def get_ffmpeg_path():
    """
    Get the FFmpeg executable path based on the operating system and environment.
    Returns the path wrapped in appropriate quotes if needed.

    Returns:
        str: The quoted path to the FFmpeg executable
    """
    if os.getenv("FFMPEG_PATH"):
        ffmpeg_path = os.environ["FFMPEG_PATH"]
    else:
        os_name = get_os_name()

        # Set base path based on environment
        if os_name == "linux":
            base_path = Path("")
        else:
            if getattr(sys, 'frozen', False):
                # If running in a PyInstaller bundle
                base_path = Path(sys._MEIPASS)
            else:
                # If running in a regular Python environment
                base_path = Path(__file__).parents[2]

        # Set binary name based on OS
        ffmpeg_binary_name = "ffmpeg.exe" if os_name == "windows" else "ffmpeg"

        # Construct full path
        ffmpeg_path = str(base_path / ffmpeg_binary_name)

    return ffmpeg_path

def generate_temp_file(extension):
    return tempfile.mktemp(suffix=extension)

def safe_delete(file_path):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            logger.warning(f"Failed to remove {file_path}")

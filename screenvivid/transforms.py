import io
import os
import sys
import re
import time
import platform
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import cairo
import pyautogui
from PIL import Image, ImageDraw, ImageFilter
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QCursor

from screenvivid.utils.general import hex_to_rgb, create_gradient_image


class BaseTransform:
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        raise NotImplementedError('Transform __call__ method must be implemented.')


class Compose(BaseTransform):
    def __init__(self, transforms):
        super().__init__()

        self.transforms = transforms

    def __call__(self, **kwargs):
        input = kwargs
        for _, t in self.transforms.items():
            input = t(**input)

        return input

    def __getitem__(self, key):
        return self.transforms.get(key)

    def __setitem__(self, key, value):
        self.transforms[key] = value

class AspectRatio(BaseTransform):
    def __init__(self, aspect_ratio: str):
        super().__init__()
        self.aspect_ratio = aspect_ratio
        self.screen_size = pyautogui.size()
        self.output_resolution_cache = None

        self._resolutions = {
            "16:9": [(1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)],
            "4:3": [(960, 720), (1440, 1080), (1920, 1440), (2880, 2160)],
            "1:1": [(720, 720), (1080, 1080), (1440, 1440), (2160, 2160)],
            "9:16": [(720, 1280), (1080, 1920), (1440, 2560), (2160, 3840)],
            "3:4": [(720, 960), (1080, 1440), (1440, 1920), (2160, 2880)],
            "16:10": [(1280, 800), (1440, 900), (1680, 1050), (1920, 1200), (2560, 1600), (2880, 1800), (3072, 1920), (3840, 2400)],
            "10:16": [(800, 1280), (900, 1440), (1050, 1680), (1200, 1920), (1600, 2560), (1800, 2880), (1920, 3072), (2400, 3840)]
        }

    def _resolution_to_aspect_ration(self, width, height):
        def gcd(a, b):
            while b != 0:
                tmp = b
                b = a % b
                a = tmp
            return a

        divisor = gcd(width, height)
        aspect_width = int(width / divisor)
        aspect_height = int(height / divisor)
        return f"{aspect_width}:{aspect_height}"

    # @lru_cache(maxsize=32)
    def calculate_output_resolution(self, aspect_ratio, input_width, input_height):
        if aspect_ratio.lower() == "auto":
            aspect_ratio = self._resolution_to_aspect_ration(input_width, input_height)

        def fit_input(max_width, max_height, input_width, input_height):
            if input_width > max_width or input_height > max_height:
                scale = min(max_width / input_width, max_height / input_height)
                input_width = int(scale * input_width)
                input_height = int(scale * input_height)

            return input_width, input_height

        screen_width, screen_height = self.screen_size
        if aspect_ratio not in self._resolutions:
            # Not a standard aspect ratio
            input_width, input_height = fit_input(screen_width, screen_height, input_width, input_height)
            return screen_width, screen_height, input_width, input_height

        # Get the highest resolution
        possible_resolutions = self._resolutions[aspect_ratio]

        output_width, output_height = 0, 0
        for width, height in possible_resolutions:
            if width >= height:
                # Landscape
                if width <= screen_width and height <= screen_height:
                    output_width, output_height = width, height
                else:
                    break
            else:
                # Portrait
                if width <= screen_height and height <= screen_width:
                    output_width, output_height = width, height
                else:
                    break

        width, height = output_width, output_height
        if input_width > width or input_height > height:
            input_width, input_height = fit_input(width, height, input_width, input_height)

        return output_width, output_height, input_width, input_height

    def __call__(self, **kwargs):
        input = kwargs['input']
        input_height, input_width = input.shape[:2]

        width, height, input_width, input_height = self.calculate_output_resolution(
            self.aspect_ratio, input_width, input_height)

        kwargs.update({
            "video_width": width,
            "video_height": height,
            "frame_width": input_width,
            "frame_height": input_height,
        })
        return kwargs

class Padding(BaseTransform):
    def __init__(self, padding: int):
        super().__init__()

        self.padding = padding

    def __call__(self, **kwargs):
        frame_width = kwargs['frame_width']
        frame_height = kwargs['frame_height']
        video_width = kwargs['video_width']
        video_height = kwargs['video_height']

        pad_x = int(frame_width * self.padding) if isinstance(self.padding, float) and (0 <= self.padding <= 1.) else self.padding
        new_width = max(50, frame_width - 2 * pad_x)
        new_height = int(new_width * frame_height / frame_width)

        x_offset = (video_width - new_width) // 2
        y_offset = (video_height - new_height) // 2

        kwargs['frame_width'] = new_width
        kwargs['frame_height'] = new_height
        kwargs['x_offset'] = x_offset
        kwargs['y_offset'] = y_offset

        return kwargs

class Inset(BaseTransform):
    def __init__(self, inset, color=(0, 0, 0)):
        super().__init__()

        self.inset = inset
        self.color = color
        self.inset_frame = None

    def __call__(self, **kwargs):
        input = kwargs['input']
        height, width = input.shape[:2]

        if self.inset > 0:
            inset_x = self.inset
            inset_y = int(inset_x * height / width)
            new_width = width - 2 * inset_x
            new_height = height - 2 * inset_y

            if self.inset_frame is None:
                self.inset_frame = np.full_like(input, fill_value=self.color, dtype=np.uint8)

            resized_frame = cv2.resize(input, (new_width, new_height))
            self.inset_frame[inset_y:inset_y+new_height, inset_x:inset_x+new_width] = resized_frame

            kwargs['input'] = self.inset_frame
        return kwargs

class Cursor(BaseTransform):
    def __init__(self, move_data, cursors_map, offsets, size=64):
        super().__init__()

        self.size = size
        self.offsets = offsets
        self.move_data = move_data
        self.cursors_map = cursors_map
        self.cursors = self._load()
        self.default_cursors = self._load()

    def _load(self):
        sub_folder = get_os_name()
        arrow_image = self._load_image(f":/resources/images/cursor/{sub_folder}/cursor.png")
        arrow_image = cv2.cvtColor(arrow_image, cv2.COLOR_RGBA2BGRA)
        height, width = arrow_image.shape[:2]
        if height > width:
            new_height = self.size
            new_width = int(self.size * width / height)
        else:
            new_width = self.size
            new_height = int(self.size * height / width)

        arrow_image = cv2.resize(arrow_image, (new_width, new_height))

        pointing_hand = self._load_image(f':/resources/images/cursor/linux/pointinghand.png')
        pointing_hand = cv2.cvtColor(pointing_hand, cv2.COLOR_RGBA2BGRA)
        pointing_hand = cv2.resize(pointing_hand, (self.size, self.size))

        return {'arrow': arrow_image, 'pointing_hand': pointing_hand}

    def _load_image(self, resource: str):
        file = QFile(resource)
        if not file.open(QIODevice.ReadOnly):  # Ensure the file is opened in read-only mode
            raise IOError(f"Cannot open resource: {resource}")

        byte_data = file.readAll().data()
        file.close()

        bytes_io = io.BytesIO(byte_data)
        image_arr = np.frombuffer(bytes_io.getvalue(), np.uint8)
        return cv2.imdecode(image_arr, cv2.IMREAD_UNCHANGED)

    def blend(self, image, x, y, cursor_id):
        # Get cursor image
        if cursor_id in self.cursors_map:
            cursor_image = self.cursors_map.get(cursor_id)
        else:
            cursor_image = self.default_cursors["arrow"]
        scale = 1
        cursor_image = cv2.resize(cursor_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
        cursor_height, cursor_width = cursor_image.shape[:2]
        image_height, image_width = image.shape[:2]

        # Calculate the position of the cursor on the image
        x1, y1 = int(image_width * x), int(image_height * y)
        x2, y2 = x1 + cursor_width, y1 + cursor_height

        # The coordinates would be used to crop
        crop_x1 = max(0, -x1)
        crop_y1 = max(0, -y1)
        crop_x2 = min(cursor_width, image_width - x1)
        crop_y2 = min(cursor_height, image_height - y1)

        # Crop the cursor image
        cropped_cursor_image = cursor_image[crop_y1:crop_y2, crop_x1:crop_x2]
        cropped_cursor_rgb = cropped_cursor_image[:, :, :3]
        mask = cropped_cursor_image[:, :, 3]

        # Crop the image
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image_width, x2), min(image_height, y2)
        fg_roi = image[y1:y2, x1:x2]

        fg_cursor = cv2.bitwise_and(cropped_cursor_rgb, cropped_cursor_rgb, mask=mask)
        fg = cv2.bitwise_and(fg_roi, fg_roi, mask=cv2.bitwise_not(mask))
        blended = cv2.add(fg_cursor, fg)
        image[y1:y2, x1:x2] = blended
        return image

    def __call__(self, **kwargs):
        if "start_frame" in kwargs and kwargs["start_frame"] in self.move_data:
            start_frame = kwargs["start_frame"]
            input = kwargs["input"]
            x, y, _, cursor_id = self.move_data[start_frame]
            kwargs["input"] = self.blend(input, x, y, cursor_id)

        return kwargs

class BorderShadow(BaseTransform):
    def __init__(self, radius, shadow_blur: int = 10, shadow_opacity: float = 0.5) -> None:
        self.radius = radius
        self.shadow_blur = shadow_blur
        self.shadow_opacity = shadow_opacity

    def create_rounded_rectangle(self, background_size, foreground_size, x_offset, y_offset):
        width, height = background_size
        rectangle_width, rectangle_height = foreground_size
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(surface)

        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()

        ctx.set_source_rgb(1, 1, 1)

        x = x_offset
        y = y_offset

        corner_radius = self.radius
        ctx.new_sub_path()
        ctx.arc(x + rectangle_width - corner_radius, y + corner_radius, corner_radius, -np.pi/2, 0)
        ctx.arc(x + rectangle_width - corner_radius, y + rectangle_height - corner_radius, corner_radius, 0, np.pi/2)
        ctx.arc(x + corner_radius, y + rectangle_height - corner_radius, corner_radius, np.pi/2, np.pi)
        ctx.arc(x + corner_radius, y + corner_radius, corner_radius, np.pi, 3*np.pi/2)
        ctx.close_path()

        ctx.fill()

        buf = surface.get_data()

        arr = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=buf)

        return arr

    @lru_cache(maxsize=100)
    def create_rounded_mask(self, size):
        rect = self.create_rounded_rectangle(size, size, 0, 0)
        mask = rect[:, :, [2, 1, 0]]
        return mask

    @lru_cache(maxsize=100)
    def create_shadow(self, background_size, foreground_size, x_offset, y_offset):
        shadow = Image.new('L', background_size, 0)
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle([(x_offset, y_offset),
                                       (x_offset + foreground_size[0], y_offset + foreground_size[1])],
                                      self.radius, fill=int(255 * self.shadow_opacity))
        shadow = np.array(shadow.filter(ImageFilter.GaussianBlur(self.shadow_blur)))
        shadow = cv2.cvtColor(shadow, cv2.COLOR_GRAY2BGR)
        shadow = shadow.astype(np.float32) / 255.0
        shadow = 1 - shadow
        return shadow

    def apply_border_radius_with_shadow(
        self,
        background,
        foreground,
        x_offset,
        y_offset,
    ):
        # import time
        foreground_size = foreground.shape[1], foreground.shape[0]
        background_size = background.shape[1], background.shape[0]

        # Create mask
        # tt = time.time()
        # t0 = time.time()
        mask_float = self.create_rounded_mask(foreground_size).astype(np.float32) / 255.0
        # print('mask', time.time() - t0)

        # Create shadow
        # t0 = time.time()
        shadow = self.create_shadow(background_size, foreground_size, x_offset, y_offset)
        background = background.astype(np.float32) / 255.0
        # print('shadow', time.time() - t0)

        # Vectorized shadow overlay
        # t0 = time.time()
        result = np.multiply(shadow, background)
        # print('overlay', time.time() - t0)

        # Optimized blending
        # t0 = time.time()
        roi = result[y_offset:y_offset+foreground_size[1], x_offset:x_offset+foreground_size[0]]

        foreground_float = foreground.astype(np.float32) / 255.0

        # Blend roi and foreground based on mask
        inv_mask = 1.0 - mask_float

        pad = self.radius // 3

        blended_roi_top = np.multiply(foreground_float[:pad, ...], mask_float[:pad, ...]) + np.multiply(roi[:pad, ...], inv_mask[:pad, ...])
        blended_roi_left = np.multiply(foreground_float[pad:-pad, :pad], mask_float[pad:-pad, :pad]) + np.multiply(roi[pad:-pad, :pad], inv_mask[pad:-pad, :pad])
        blended_roi_bottom= np.multiply(foreground_float[-pad:, ...], mask_float[-pad:, ...]) + np.multiply(roi[-pad:, ...], inv_mask[-pad:, ...])
        blended_roi_right = np.multiply(foreground_float[pad:-pad, -pad:], mask_float[pad:-pad, -pad:]) + np.multiply(roi[pad:-pad, -pad:], inv_mask[pad:-pad, -pad:])

        roi[:pad, ...] = blended_roi_top
        roi[pad:-pad, :pad] = blended_roi_left
        roi[-pad:, ...] = blended_roi_bottom
        roi[pad:-pad, -pad:] = blended_roi_right
        roi[pad:-pad, pad:-pad] = foreground_float[pad:-pad, pad:-pad]

        result[y_offset:y_offset+foreground_size[1], x_offset:x_offset+foreground_size[0]] = roi
        # print('final', time.time() - t0)

        # print('total', time.time() - tt)
        return (result * 255).astype(np.uint8)

    def __call__(self, **kwargs):
        kwargs["radius"] = self.radius
        kwargs["border_shadow"] = self
        return kwargs

class Background(BaseTransform):
    def __init__(self, background):
        super().__init__()

        if getattr(sys, 'frozen', False):
            # Run from executable
            base_path = Path(sys._MEIPASS)
        else:
            # Run from source
            base_path = Path(__file__).parents[0]

        self.background_dir = os.path.join(base_path, "resources/images/wallpapers/hires")
        self.background = background
        self.background_image = None

    def _get_background_image(self, background, width, height):
        if background['type'] == 'wallpaper':
            index = background['value']
            background_path = os.path.join(self.background_dir, f'gradient-wallpaper-{index:04d}.jpg')
            background_image = cv2.imread(background_path)
            background_image = cv2.resize(background_image, (width, height))
        elif background['type'] == 'gradient':
            value = background['value']
            first_color, second_color = value['colors']
            angle = value['angle']
            background_image = create_gradient_image(width, height, first_color, second_color, angle)
        elif background['type'] == 'color':
            hex_color = background['value']
            r, g, b = hex_to_rgb(hex_color)
            background_image = np.full(shape=(height, width, 3), fill_value=(b, g, r), dtype=np.uint8)
        elif background['type'] == 'image':
            background_path = background['value'].toLocalFile()
            if not os.path.exists(background_path):
                raise Exception()

            background_image = cv2.imread(background_path)
            background_image = cv2.resize(background_image, (width, height))
        else:
            background_image = np.full((height, width, 3), fill_value=0, dtype=np.uint8)

        return background_image

    def __call__(self, **kwargs):
        input = kwargs['input']
        video_width = kwargs['video_width']
        video_height = kwargs['video_height']
        frame_width = kwargs['frame_width']
        frame_height = kwargs['frame_height']
        x_offset = kwargs.get('x_offset', 0)
        y_offset = kwargs.get('y_offset', 0)

        if input.shape[0] != frame_height or input.shape[1] != frame_width:
            input = cv2.resize(input, (frame_width, frame_height))

        if self.background_image is None or self.background_image.shape[0] != video_height or self.background_image.shape[1] != video_width:
            self.background_image = self._get_background_image(self.background, video_width, video_height)

        output = self.background_image.copy()

        x1 = x_offset
        y1 = y_offset
        x2 = x1 + frame_width
        y2 = y1 + frame_height

        if 'border_shadow' in kwargs:
            border_shadow = kwargs['border_shadow']

            output = border_shadow.apply_border_radius_with_shadow(
                self.background_image,
                input,
                x_offset,
                y_offset,
            )
        else:
            output[y1:y2, x1:x2, :] = input

        kwargs['input'] = output
        return kwargs


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
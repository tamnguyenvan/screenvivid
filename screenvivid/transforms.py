import io
import json
import glob
import os
import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageDraw, ImageFilter
from PySide6.QtCore import QFile, QIODevice

from screenvivid.utils.general import hex_to_rgb, create_gradient_image, get_os_name

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
    def __init__(self, move_data, cursors_map, offsets, size=32, scale=1.0):
        super().__init__()

        self.size = size
        self.scale = scale
        self.offsets = offsets
        self.move_data = move_data
        self.cursor_states = {
            "windows": [
                "arrow", "ibeam", "wait", "cross", "uparrow", "sizenwse", "sizenesw",
                "sizewe", "sizens", "sizeall", "no", "hand", "appstarting", "help"
            ],
            "linux": [
                "arrow", "ibeam", "wait", "progress", "watch", "crosshair", "text", "vertical-text",
                "alias", "copy", "move", "no-drop", "not-allowed", "grab",
                "grabbing", "all-scroll", "col-resize", "row-resize", "n-resize",
                "e-resize", "s-resize", "w-resize", "nw-resize", "se-resize",
                "sw-resize", "ew-resize", "ns-resize", "nsew-resize", "nwse-resize",
                "top_left_corner", "top_right_corner", "bottom_left_corner", "bottom_right_corner",
                "zoom-in", "zoom-out", "pointer-move", "xterm"
            ],
            "macos": [
                "arrow", "ibeam", "crosshair", "closedHand", "openHand", "pointingHand",
                "resizeLeft", "resizeRight", "resizeLeftRight", "resizeUp", "resizeDown",
                "resizeUpDown", "operationNotAllowed"
            ],
        }
        self.default_cursor = self._load_default_cursor()
        self.os_name = get_os_name()
        if self.os_name in "linux":
            self.cursors_map = cursors_map
        else:
            self.cursors_map = self._load()

    def _load(self):
        # Load offsets data from json file
        if getattr(sys, 'frozen', False):
            # If running in a PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # If running in a regular Python environment
            base_path = Path(__file__).resolve().parent

        offset_file = os.path.join(base_path, f"resources/images/cursor/{self.os_name}/offsets.json")
        with open(offset_file, "r") as f:
            offsets = json.load(f)

        cursors_map = {}
        scales = ["1x", "1.5x", "2x", "3x"]
        for cursor_state in self.cursor_states[self.os_name]:
            cursors_map[cursor_state] = {}
            for scale in scales:
                if scale not in cursors_map[cursor_state]:
                    cursors_map[cursor_state][scale] = []
                pattern = os.path.join(base_path, f"resources/images/cursor/{self.os_name}/{scale}/{cursor_state}*.png")
                paths = sorted(glob.glob(pattern))
                for i, path in enumerate(paths):
                    cursor_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    # cursor_image = self._load_image(path)
                    # cursor_image = cv2.cvtColor(cursor_image, cv2.COLOR_RGBA2BGRA)

                    offset = offsets.get(cursor_state, {}).get(scale, (0, 0))
                    cursors_map[cursor_state][scale].append({"image": cursor_image, "offset": offset})
        return cursors_map

    # def _load_image(self, resource: str):
    #     file = QFile(resource)
    #     if not file.open(QIODevice.ReadOnly):  # Ensure the file is opened in read-only mode
    #         raise IOError(f"Cannot open resource: {resource}")

    #     byte_data = file.readAll().data()
    #     file.close()

    #     bytes_io = io.BytesIO(byte_data)
    #     image_arr = np.frombuffer(bytes_io.getvalue(), np.uint8)
    #     return cv2.imdecode(image_arr, cv2.IMREAD_UNCHANGED)

    def _load_default_cursor(self):
        if getattr(sys, 'frozen', False):
            # If running in a PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # If running in a regular Python environment
            base_path = Path(__file__).resolve().parent

        default_cursor_dir = os.path.join(base_path, f"resources/images/cursor/default")
        default_cursor = {}
        for scale in os.listdir(default_cursor_dir):
            scale_path = os.path.join(default_cursor_dir, scale)
            for filename in os.listdir(scale_path):
                cursor_state = filename.split(".")[0]
                cursor_path = os.path.join(scale_path, filename)
                cursor_image = cv2.imread(cursor_path, cv2.IMREAD_UNCHANGED)
                default_cursor[cursor_state] = {scale: [{"image": cursor_image, "offset": (0, 0)}]}
        return default_cursor

    def blend(self, image, x, y, cursor_state, anim_step):
        # Get cursor image
        scale_str = f"{int(self.scale)}x" if self.scale.is_integer() else f"{self.scale:.1f}"
        if (
            self.cursors_map.get(cursor_state)
            and self.cursors_map[cursor_state].get(scale_str)
        ):
            cursor_info = self.cursors_map[cursor_state][scale_str][anim_step]
            cursor_image = cursor_info["image"]
            cursor_offset = cursor_info["offset"]
        else:
            # Check if arrow cursor is available and the scale_str is available
            if (
                self.cursors_map.get("arrow")
                and self.cursors_map["arrow"].get(scale_str)
            ):
                cursor_image = self.cursors_map["arrow"][scale_str][0]["image"]
                cursor_offset = self.cursors_map["arrow"][scale_str][0]["offset"]
            else:
                if scale_str in self.default_cursor["arrow"]:
                    cursor_image = self.default_cursor["arrow"][scale_str][0]["image"]
                    cursor_offset = self.default_cursor["arrow"][scale_str][0]["offset"]
                else:
                    cursor_image = self.default_cursor["arrow"]["1x"][0]["image"]
                    cursor_offset = self.default_cursor["arrow"]["1x"][0]["offset"]

        cursor_height, cursor_width = cursor_image.shape[:2]
        image_height, image_width = image.shape[:2]

        # Calculate the position of the cursor on the image
        x1, y1 = int(image_width * x) - cursor_offset[0], int(image_height * y) - cursor_offset[1]
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

        mask_float = mask.astype(np.float32) / 255.0
        fg_cursor = cropped_cursor_rgb * mask_float[:, :, np.newaxis]
        fg = fg_roi * (1 - mask_float[:, :, np.newaxis])
        blended = fg_cursor + fg
        image[y1:y2, x1:x2] = blended.astype(np.uint8)
        return image

    def __call__(self, **kwargs):
        if "start_frame" in kwargs and kwargs["start_frame"] in self.move_data:
            start_frame = kwargs["start_frame"]
            input = kwargs["input"]
            x, y, _, cursor_state, anim_step = self.move_data[start_frame]
            kwargs["input"] = self.blend(input, x, y, cursor_state, anim_step)

        return kwargs

class BorderShadow(BaseTransform):
    def __init__(self, radius, shadow_blur: int = 10, shadow_opacity: float = 0.5) -> None:
        self.radius = radius
        self.shadow_blur = shadow_blur
        self.shadow_opacity = shadow_opacity

    def create_rounded_rectangle(self, background_size, foreground_size, x_offset, y_offset):
        width, height = background_size
        rectangle_width, rectangle_height = foreground_size
        radius = self.radius

        image = np.zeros((height, width, 3), dtype=np.uint8)

        x = x_offset
        y = y_offset

        cv2.rectangle(image, (x + radius, y), (x + rectangle_width - radius, y + rectangle_height), (255, 255, 255), -1, cv2.LINE_AA)
        cv2.rectangle(image, (x, y + radius), (x + rectangle_width, y + rectangle_height - radius), (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(image, (x + radius, y + radius), radius, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(image, (x + rectangle_width - radius, y + radius), radius, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(image, (x + radius, y + rectangle_height - radius), radius, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(image, (x + rectangle_width - radius, y + rectangle_height - radius), radius, (255, 255, 255), -1, cv2.LINE_AA)

        return image

    @lru_cache(maxsize=100)
    def create_rounded_mask(self, size, return_float=False):
        rect = self.create_rounded_rectangle(size, size, 0, 0)
        mask = rect[:, :, [2, 1, 0]]
        if return_float:
            mask = mask.astype(np.float32) / 255.0
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

        # Create mask and shadow
        # tt = time.time()
        # t0 = time.time()
        mask_float = self.create_rounded_mask(foreground_size, return_float=True)
        # print('mask', time.time() - t0)

        # t0 = time.time()
        shadow = self.create_shadow(background_size, foreground_size, x_offset, y_offset)
        background_float = background.astype(np.float32) / 255.0
        # print('mask and shadow', time.time() - tt)

        # Vectorized shadow overlay
        # t0 = time.time()
        result = shadow * background_float
        # print('overlay', time.time() - t0)

        # Optimized blending
        # t0 = time.time()
        roi = result[y_offset:y_offset + foreground_size[1], x_offset:x_offset + foreground_size[0]]
        foreground_float = foreground.astype(np.float32) / 255.0

        # Blend roi and foreground based on mask
        inv_mask = 1.0 - mask_float
        pad = self.radius // 3

        blended_roi_top = foreground_float[:pad, ...] * mask_float[:pad, ...] + roi[:pad, ...] * inv_mask[:pad, ...]
        blended_roi_left = foreground_float[pad:-pad, :pad] * mask_float[pad:-pad, :pad] + roi[pad:-pad, :pad] * inv_mask[pad:-pad, :pad]
        blended_roi_bottom = foreground_float[-pad:, ...] * mask_float[-pad:, ...] + roi[-pad:, ...] * inv_mask[-pad:, ...]
        blended_roi_right = foreground_float[pad:-pad, -pad:] * mask_float[pad:-pad, -pad:] + roi[pad:-pad, -pad:] * inv_mask[pad:-pad, -pad:]

        roi[:pad, ...] = blended_roi_top
        roi[pad:-pad, :pad] = blended_roi_left
        roi[-pad:, ...] = blended_roi_bottom
        roi[pad:-pad, -pad:] = blended_roi_right
        roi[pad:-pad, pad:-pad] = foreground_float[pad:-pad, pad:-pad]

        result[y_offset:y_offset + foreground_size[1], x_offset:x_offset + foreground_size[0]] = roi
        # print('blending', time.time() - t0)
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

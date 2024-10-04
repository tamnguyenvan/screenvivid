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

    def get(self, key, default=None):
        return self.transforms.get(key, default)

class AspectRatio(BaseTransform):
    def __init__(self, aspect_ratio: str, screen_size: tuple):
        super().__init__()
        self.aspect_ratio = aspect_ratio
        self.aspect_ratio_float = 16 /  9
        self.screen_size = screen_size
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
            return screen_width, screen_height, input_width, input_height, input_width / input_height

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

        return output_width, output_height, input_width, input_height, input_width / input_height

    def __call__(self, **kwargs):
        input = kwargs['input']
        input_height, input_width = input.shape[:2]

        width, height, input_width, input_height, self.aspect_ratio_float = self.calculate_output_resolution(
            self.aspect_ratio, input_width, input_height)

        kwargs.update({
            "background_width": width,
            "background_height": height,
            "foreground_width": input_width,
            "foreground_height": input_height,
            "aspect_ratio_float": self.aspect_ratio_float
        })
        return kwargs

class Padding(BaseTransform):
    def __init__(self, padding: float):
        super().__init__()

        self.padding = padding

    def __call__(self, **kwargs):
        foreground_width = kwargs['foreground_width']
        foreground_height = kwargs['foreground_height']
        background_width = kwargs['background_width']
        background_height = kwargs['background_height']

        pad_x = int(foreground_width * self.padding * 0.5) if isinstance(self.padding, float) and (0 <= self.padding <= 1.) else self.padding
        new_width = max(50, foreground_width - 2 * pad_x)
        new_height = int(new_width * foreground_height / foreground_width)

        x_offset = (background_width - new_width) // 2
        y_offset = (background_height - new_height) // 2

        kwargs['foreground_width'] = new_width
        kwargs['foreground_height'] = new_height
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
                "arrow", "ibeam", "wait", "progress", "watch", "pointing_hand", "closedhand",
                "openhand", "help", "forbidden", "crosshair", "text", "vertical-text",
                "alias", "copy", "move", "no-drop", "not-allowed",
                "all-scroll", "col-resize", "row-resize", "n-resize",
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
        self.available_scales = ["1x", "1.5x", "2x", "3x"]
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
        for cursor_state in self.cursor_states[self.os_name]:
            cursors_map[cursor_state] = {}
            for scale in self.available_scales:
                if scale not in cursors_map[cursor_state]:
                    cursors_map[cursor_state][scale] = []
                pattern = os.path.join(base_path, f"resources/images/cursor/{self.os_name}/{scale}/{cursor_state}*.png")
                paths = sorted(glob.glob(pattern))
                for i, path in enumerate(paths):
                    cursor_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

                    offset = offsets.get(cursor_state, {}).get(scale, (0, 0))
                    cursors_map[cursor_state][scale].append({"image": cursor_image, "offset": offset})
        return cursors_map

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
                if cursor_state not in default_cursor:
                    default_cursor[cursor_state] = {}

                if scale not in default_cursor[cursor_state]:
                    default_cursor[cursor_state][scale] = []
                default_cursor[cursor_state][scale].append({"image": cursor_image, "offset": (0, 0)})

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
    def __init__(self, border_radius, shadow_blur: int = 10, shadow_opacity: float = 0.5) -> None:
        self.border_radius = border_radius
        self.shadow_blur = shadow_blur
        self.shadow_opacity = shadow_opacity
        self.scale_factor = 4  # For anti-aliasing corner

    @lru_cache(maxsize=1)
    def create_rounded_rectangle(self, background_size, foreground_size, x_offset, y_offset):
        def draw_rounded_corner(radius):
            size = 2 * radius + 10
            scaled_size = int(size * self.scale_factor)
            scaled_radius = int(radius * self.scale_factor)

            corner = Image.new("L", (scaled_size, scaled_size), 0)
            draw = ImageDraw.Draw(corner)

            draw.rounded_rectangle(
                [0, 0, scaled_size, scaled_size],
                radius=scaled_radius,
                fill=255
            )

            corner = corner.resize((size, size), Image.LANCZOS)
            corner = corner.crop((0, 0, radius, radius))
            return corner

        width, height = background_size
        fg_width, fg_height = foreground_size
        radius = self.border_radius

        if radius > 0:
            img = Image.new("L", background_size, 0)
            draw = ImageDraw.Draw(img)

            draw.rectangle(
                [x_offset + radius, y_offset,
                x_offset + fg_width - radius, y_offset + fg_height],
                fill=255
            )
            draw.rectangle(
                [x_offset, y_offset + radius,
                x_offset + fg_width, y_offset + fg_height - radius],
                fill=255
            )

            top_left = np.array(draw_rounded_corner(radius))
            top_right = np.fliplr(top_left)
            bottom_left = np.flipud(top_left)
            bottom_right = np.fliplr(bottom_left)

            rect = np.array(img)

            rect[y_offset:y_offset+radius, x_offset:x_offset+radius] = top_left
            rect[y_offset:y_offset+radius, x_offset+fg_width-radius:x_offset+fg_width] = top_right
            rect[y_offset+fg_height-radius:y_offset+fg_height, x_offset:x_offset+radius] = bottom_left
            rect[y_offset+fg_height-radius:y_offset+fg_height, x_offset+fg_width-radius:x_offset+fg_width] = bottom_right

            rect = rect[y_offset:y_offset+fg_height, x_offset:x_offset+fg_width]

            rect = rect / 255.
        else:
            rect = np.ones((background_size[1], background_size[0]), dtype=np.float32)

        return rect

    @lru_cache(maxsize=1)
    def create_shadow(self, background_size, foreground_size, x_offset, y_offset, border=None):
        shadow = Image.new('L', background_size, 0)
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle([(x_offset, y_offset),
                                       (x_offset + foreground_size[0], y_offset + foreground_size[1])],
                                      self.border_radius, fill=int(255 * self.shadow_opacity))
        shadow = np.array(shadow.filter(ImageFilter.GaussianBlur(self.shadow_blur)))
        shadow = shadow.astype(np.float32) / 255.0
        if border is not None:
            shadow = cv2.copyMakeBorder(shadow, border, border, border, border, cv2.BORDER_CONSTANT, None, 0)
        return shadow

    def render_drop_shadow(self, background, foreground, shadow_alpha, foreground_alpha, offset):
        bg_height, bg_width = background.shape[:2]
        x_offset, y_offset = offset
        fg_size = foreground.shape[1], foreground.shape[0]

        shadow_alpha = np.expand_dims(shadow_alpha, axis=-1)
        fg_alpha = np.expand_dims(foreground_alpha, axis=-1)

        outer_pad = 2 * self.shadow_blur
        inner_pad = self.border_radius if self.border_radius > 0 else 10
        corner_pad = outer_pad + inner_pad
        x1, y1 = max(0, x_offset - outer_pad), max(0, y_offset - outer_pad)
        x2, y2 = min(x_offset + fg_size[0] + outer_pad, bg_width), min(y_offset + fg_size[1] + outer_pad, bg_height)

        # Top-left corner
        shadow_alpha_roi = shadow_alpha[y1:y1+corner_pad, x1:x1+corner_pad]
        bg_roi = background[y1:y1+corner_pad, x1:x1+corner_pad]
        patch = (1 - shadow_alpha_roi) * bg_roi
        patch_roi = patch[outer_pad:, outer_pad:]
        alpha_roi = fg_alpha[:inner_pad, :inner_pad]
        foreground_roi = foreground[:inner_pad, :inner_pad]
        patch[outer_pad:, outer_pad:] = (1 - alpha_roi) * patch_roi + alpha_roi * foreground_roi
        background[y1:y1+corner_pad, x1:x1+corner_pad] = patch

        # Bottom left corner
        shadow_alpha_roi = shadow_alpha[y2-corner_pad:y2, x1:x1+corner_pad]
        bg_roi = background[y2-corner_pad:y2, x1:x1+corner_pad]
        patch = (1 - shadow_alpha_roi) * bg_roi
        patch_roi = patch[:inner_pad, outer_pad:]
        alpha_roi = fg_alpha[-inner_pad:, :inner_pad]
        foreground_roi = foreground[-inner_pad:, :inner_pad]
        patch[:inner_pad, outer_pad:] = (1 - alpha_roi) * patch_roi + alpha_roi * foreground_roi
        background[y2-corner_pad:y2, x1:x1+corner_pad] = patch

        # Bottom right corner
        shadow_alpha_roi = shadow_alpha[y2-corner_pad:y2, x2-corner_pad:x2]
        bg_roi = background[y2-corner_pad:y2, x2-corner_pad:x2]
        patch = (1 - shadow_alpha_roi) * bg_roi
        patch_roi = patch[:inner_pad, :inner_pad]
        alpha_roi = fg_alpha[-inner_pad:, -inner_pad:]
        foreground_roi = foreground[-inner_pad:, -inner_pad:]
        patch[:inner_pad, :inner_pad] = (1 - alpha_roi) * patch_roi + alpha_roi * foreground_roi
        background[y2-corner_pad:y2, x2-corner_pad:x2] = patch

        # Top right corner
        shadow_alpha_roi = shadow_alpha[y1:y1+corner_pad, x2-corner_pad:x2]
        bg_roi = background[y1:y1+corner_pad, x2-corner_pad:x2]
        patch = (1 - shadow_alpha_roi) * bg_roi
        patch_roi = patch[outer_pad:, :inner_pad]
        alpha_roi = fg_alpha[:inner_pad, -inner_pad:]
        foreground_roi = foreground[:inner_pad, -inner_pad:]
        patch[outer_pad:, :inner_pad] = (1 - alpha_roi) * patch_roi + alpha_roi * foreground_roi
        background[y1:y1+corner_pad, x2-corner_pad:x2] = patch

        # Left side
        shadow_alpha_roi = shadow_alpha[y1+corner_pad:y2-corner_pad, x1:x1+outer_pad]
        bg_roi = background[y1+corner_pad:y2-corner_pad, x1:x1+outer_pad]
        patch = (1 - shadow_alpha_roi) * bg_roi
        background[y1+corner_pad:y2-corner_pad, x1:x1+outer_pad] = patch


        # Bottom
        shadow_alpha_roi = shadow_alpha[y2-outer_pad:y2, x1+corner_pad:x2-corner_pad]
        bg_roi = background[y2-outer_pad:y2, x1+corner_pad:x2-corner_pad]
        patch = (1 - shadow_alpha_roi) * bg_roi
        background[y2-outer_pad:y2, x1+corner_pad:x2-corner_pad] = patch

        # Right side
        shadow_alpha_roi = shadow_alpha[y1+corner_pad:y2-corner_pad, x2-outer_pad:x2]
        bg_roi = background[y1+corner_pad:y2-corner_pad, x2-outer_pad:x2]
        patch = (1 - shadow_alpha_roi) * bg_roi
        background[y1+corner_pad:y2-corner_pad, x2-outer_pad:x2] = patch

        # Top
        shadow_alpha_roi = shadow_alpha[y1:y1+outer_pad, x1+corner_pad:x2-corner_pad]
        bg_roi = background[y1:y1+outer_pad, x1+corner_pad:x2-corner_pad]
        patch = (1 - shadow_alpha_roi) * bg_roi
        background[y1:y1+outer_pad, x1+corner_pad:x2-corner_pad] = patch

        # Center 1
        background[y1+corner_pad:y2-corner_pad, x1+outer_pad:x2-outer_pad] = foreground[inner_pad:fg_size[1]-inner_pad, :]

        # Center 2
        background[y1+outer_pad:y1+corner_pad, x1+corner_pad:x2-corner_pad] = foreground[:inner_pad, inner_pad:fg_size[0]-inner_pad]

        # Center 3
        background[y2-corner_pad:y2-outer_pad, x1+corner_pad:x2-corner_pad] = foreground[fg_size[1]-inner_pad:, inner_pad:fg_size[0]-inner_pad]
        return background[outer_pad:-outer_pad, outer_pad:-outer_pad]

    def apply_border_radius_with_shadow(
        self,
        background,
        foreground,
        x_offset,
        y_offset,
    ):
        background_size = background.shape[1], background.shape[0]
        foreground_size = foreground.shape[1], foreground.shape[0]

        foreground_alpha = self.create_rounded_rectangle(
            foreground_size,
            foreground_size,
            0, 0
        )

        outer_pad = 2 * self.shadow_blur
        shadow_alpha = self.create_shadow(background_size, foreground_size, x_offset, y_offset, border=outer_pad)

        background = cv2.copyMakeBorder(background, outer_pad, outer_pad, outer_pad, outer_pad, cv2.BORDER_CONSTANT, None, 0)

        offset = (x_offset + outer_pad, y_offset + outer_pad)
        result = self.render_drop_shadow(background, foreground, shadow_alpha, foreground_alpha, offset)
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    def __call__(self, **kwargs):
        kwargs["border_radius"] = self.border_radius
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

    def _crop_and_resize(self, image, target_size):
        width, height = target_size
        img_height, img_width = image.shape[:2]
        scale = max(width / img_width, height / img_height)
        if width / img_width > height / img_height:
            new_width = width
            new_height = int(img_height * scale)
        else:
            new_width = int(img_width * scale)
            new_height = height
        image = cv2.resize(image, (new_width, new_height), cv2.INTER_LANCZOS4)

        # Crop center
        start_x = (new_width - width) // 2
        start_y = (new_height - height) // 2
        image = image[start_y:start_y+height, start_x:start_x+width]
        return image

    def _get_background_image(self, background, width, height):
        if background['type'] == 'wallpaper':
            index = background['value']
            background_path = os.path.join(self.background_dir, f'gradient-wallpaper-{index:04d}.jpg')
            background_image = cv2.imread(background_path)
        elif background['type'] == 'gradient':
            value = background['value']
            first_color, second_color = value['colors']
            angle = value['angle']
            background_image = create_gradient_image(width, height, first_color, second_color, angle)
            return background_image  # No need to resize or crop for gradient
        elif background['type'] == 'color':
            hex_color = background['value']
            r, g, b = hex_to_rgb(hex_color)
            background_image = np.full(shape=(height, width, 3), fill_value=(b, g, r), dtype=np.uint8)
            return background_image  # No need to resize or crop for solid color
        elif background['type'] == 'image':
            background_path = background['value'].toLocalFile()
            if not os.path.exists(background_path):
                raise Exception("Background image file does not exist")
            background_image = cv2.imread(background_path)
        else:
            background_image = np.full((height, width, 3), fill_value=0, dtype=np.uint8)
            return background_image  # No need to resize or crop for default black background

        # Resize to contain (width, height)
        background_image = self._crop_and_resize(background_image, (width, height))

        return background_image

    def __call__(self, **kwargs):
        input = kwargs['input']
        background_width = kwargs['background_width']
        background_height = kwargs['background_height']
        foreground_width = kwargs['foreground_width']
        foreground_height = kwargs['foreground_height']
        x_offset = kwargs.get('x_offset', 0)
        y_offset = kwargs.get('y_offset', 0)

        if self.background_image is None or self.background_image.shape[:2] != (background_height, background_width):
            self.background_image = self._get_background_image(self.background, background_width, background_height)

        background_image = self.background_image.copy()

        foreground = self._crop_and_resize(input.copy(), (foreground_width, foreground_height))
        # foreground = cv2.cvtColor(foreground, cv2.COLOR_BGR2RGB)

        x1 = x_offset
        y1 = y_offset
        x2 = x1 + foreground_width
        y2 = y1 + foreground_height

        if 'border_shadow' in kwargs:
            border_shadow = kwargs['border_shadow']

            output = border_shadow.apply_border_radius_with_shadow(
                background_image,
                foreground,
                x_offset,
                y_offset,
            )
        else:
            output = background_image
            output[y1:y2, x1:x2, :] = input

        return output
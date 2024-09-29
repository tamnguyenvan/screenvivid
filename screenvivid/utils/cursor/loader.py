import os
import struct
import subprocess
from abc import ABCMeta, abstractmethod
from typing import Tuple, Any, List

import numpy as np

from screenvivid.utils.general import get_os_name
from screenvivid.utils.logs import logger

class CursorLoader:
    def __init__(self):
        self.os_name = get_os_name()
        self._loader = None

    def load_cursor_theme(self):
        if self.os_name == "macos":
            self._loader = MacOSCursorLoader()
            return self._loader.load_cursor_theme()
        elif self.os_name == "linux":
            self._loader = LinuxCursorLoader()
            return self._loader.load_cursor_theme()
        else:
            return None

    def get_cursor(self, name):
        if self.os_name == "macos":
            return self._loader.get_cursor(name)
        elif self.os_name == "linux":
            return self._loader.get_cursor(name)
        else:
            return None

    @property
    def cursor_theme(self):
        if self.os_name == "macos":
            return self._loader.cursor_theme
        elif self.os_name == "linux":
            return self._loader.cursor_theme
        else:
            return None

class MacOSCursorLoader:
    def __init__(self):
        self.cursor_theme = {}
        self.states = [
            "arrow", "IBeam", "crosshair", "closedHand", "openHand", "pointingHand",
            "resizeLeft", "resizeRight", "resizeLeftRight", "resizeUp", "resizeDown",
            "resizeUpDown", "disappearingItem", "contextualMenu", "dragCopy",
            "dragLink", "operationNotAllowed"
        ]

    def load_cursor_theme(self):
        import AppKit
        from Cocoa import NSBitmapImageRep, NSPNGFileType
        import io
        from PIL import Image
        import numpy as np

        for state in self.states:
            try:
                cursor_method = getattr(AppKit.NSCursor, f"{state}Cursor")
                cursor = cursor_method()
                image = cursor.image()
                size = image.size()
                width, height = int(size.width), int(size.height)

                bitmap_rep = NSBitmapImageRep.imageRepWithData_(image.TIFFRepresentation())

                png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)

                buffer = io.BytesIO(png_data)
                img_array = Image.open(buffer)
                img_array = np.array(img_array)
                bgra = img_array[..., ::-1]
                self.cursor_theme.setdefault(width, {}).setdefault(state, []).append({
                    "image": bgra,
                    "offset": cursor.hotSpot()
                })
            except Exception as e:
                logger.error(f"Failed to load cursor state '{state}': {e}")

        return self.cursor_theme

class LinuxCursorLoader:
    def __init__(self):
        self.cursor_theme = {}
        self.base_size = 32
        self.sizes = [24, 32, 48, 64, 96]
        self.states = [
            "arrow", "ibeam", "wait", "progress", "watch", "crosshair", "text", "vertical-text",
            "alias", "copy", "move", "no-drop", "not-allowed", "grab",
            "grabbing", "all-scroll", "col-resize", "row-resize", "n-resize",
            "e-resize", "s-resize", "w-resize", "nw-resize", "se-resize",
            "sw-resize", "ew-resize", "ns-resize", "nsew-resize", "nwse-resize",
            "top_left_corner", "top_right_corner", "bottom_left_corner", "bottom_right_corner",
            "zoom-in", "zoom-out", "pointer-move", "xterm"
        ]

    def _get_active_cursor_theme(self):
        de = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if not de:
            de = os.environ.get('DESKTOP_SESSION', '').lower()

        cursor_theme = None
        cursor_theme_dir = None

        if 'gnome' in de or 'cinnamon' in de:
            # GNOME and Cinnamon
            try:
                cursor_theme = subprocess.check_output(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'cursor-theme']
                ).decode().strip().strip("'")
            except subprocess.CalledProcessError:
                pass
        elif 'kde' in de:
            # KDE Plasma
            try:
                cursor_theme = subprocess.check_output(
                    ['kreadconfig5', '--file', 'kcminputrc', '--group', 'Mouse', '--key', 'cursorTheme']
                ).decode().strip()
            except subprocess.CalledProcessError:
                pass
        elif 'xfce' in de:
            # Xfce
            try:
                cursor_theme = subprocess.check_output(
                    ['xfconf-query', '-c', 'xsettings', '-p', '/Gtk/CursorThemeName']
                ).decode().strip()
            except subprocess.CalledProcessError:
                pass
        elif 'mate' in de:
            # MATE
            try:
                cursor_theme = subprocess.check_output(
                    ['gsettings', 'get', 'org.mate.peripherals-mouse', 'cursor-theme']
                ).decode().strip().strip("'")
            except subprocess.CalledProcessError:
                pass

        if cursor_theme:
            # Find cursor theme directory
            possible_dirs = [
                f"{os.path.expanduser('~')}/.icons/{cursor_theme}",
                f"/usr/share/icons/{cursor_theme}",
                f"/usr/share/cursors/xorg-x11/{cursor_theme}",
                f"{os.path.expanduser('~')}/.local/share/icons/{cursor_theme}"
            ]

            for dir in possible_dirs:
                if os.path.isdir(dir):
                    cursor_theme_dir = dir
                    break

        return cursor_theme, cursor_theme_dir

    def load_cursor_theme(self):
        cursor_theme, cursor_theme_dir = self._get_active_cursor_theme()
        logger.debug(f"Cursor theme: {cursor_theme}, directory: {cursor_theme_dir}")

        if cursor_theme_dir:
            for state in self.states:
                cursor_path = os.path.join(cursor_theme_dir, "cursors", state)
                if not os.path.exists(cursor_path):
                    continue

                cursors = load_xcursor(cursor_path)
                if not cursors:
                    continue

                for cursor_image, cursor_size, cursor_offset, _ in cursors:
                    width = cursor_size[0]
                    if width not in self.sizes:
                        continue

                    logger.debug(f"Cursor: {cursor_path}, size: {width}, state: {state}")
                    self.cursor_theme.setdefault(width, {}).setdefault(state, []).append({
                        "image": cursor_image,
                        "offset": cursor_offset
                    })

        return self.cursor_theme

    def get_cursor(self, state):
        """Return a dictionary with the scale as the key and the cursor images
          as the value.
        """
        cursor_theme = dict()
        for size in self.sizes:
            cursor_theme_size = self.cursor_theme.get(size, {})
            if state in cursor_theme_size:
                scale = size / self.base_size
                scale_str = f"{int(scale)}x" if scale.is_integer() else f"{scale:.1f}"
                cursor_theme[scale_str] = self.cursor_theme.get(size, {}).get(state, [])
        return cursor_theme

class BaseParser(metaclass=ABCMeta):
    blob: bytes

    @abstractmethod
    def __init__(self, blob: bytes) -> None:
        self.blob = blob

    @classmethod
    @abstractmethod
    def can_parse(cls, blob: bytes) -> bool:
        raise NotImplementedError()

class XCursorParser(BaseParser):
    MAGIC = b'Xcur'
    VERSION = 0x1_0000
    FILE_HEADER = struct.Struct('<4sIII')
    TOC_CHUNK = struct.Struct('<III')
    CHUNK_IMAGE = 0xFFFD0002
    IMAGE_HEADER = struct.Struct('<IIIIIIIII')

    def __init__(self, blob: bytes) -> None:
        super().__init__(blob)

    @classmethod
    def can_parse(cls, blob: bytes) -> bool:
        return blob[:len(cls.MAGIC)] == cls.MAGIC

    def _unpack(self, struct_cls: struct.Struct, offset: int) -> Tuple[Any, ...]:
        return struct_cls.unpack(self.blob[offset:offset + struct_cls.size])

    def parse(self):
        magic, header_size, version, toc_size = self._unpack(self.FILE_HEADER, 0)
        assert magic == self.MAGIC

        if version != self.VERSION:
            raise ValueError(f'Unsupported Xcursor version 0x{version:08x}')

        offset = self.FILE_HEADER.size
        chunks: List[Tuple[int, int, int]] = []
        for i in range(toc_size):
            chunk_type, chunk_subtype, position = self._unpack(self.TOC_CHUNK, offset)
            chunks.append((chunk_type, chunk_subtype, position))
            offset += self.TOC_CHUNK.size

        cursors = []
        available_sizes = set([24, 32, 48, 64, 96])
        for chunk_type, chunk_subtype, position in chunks:
            if chunk_type != self.CHUNK_IMAGE:
                continue

            size, actual_type, nominal_size, version, width, height, x_offset, y_offset, delay = \
                self._unpack(self.IMAGE_HEADER, position)
            delay /= 1000

            if size != self.IMAGE_HEADER.size:
                raise ValueError(f'Unexpected size: {size}, expected {self.IMAGE_HEADER.size}')

            if actual_type != chunk_type:
                raise ValueError(f'Unexpected chunk type: {actual_type}, expected {chunk_type}')

            if nominal_size != chunk_subtype:
                raise ValueError(f'Unexpected nominal size: {nominal_size}, expected {chunk_subtype}')

            if width > 0x7FFF:
                raise ValueError(f'Image width too large: {width}')

            if height > 0x7FFF:
                raise ValueError(f'Image height too large: {height}')

            if x_offset > width:
                raise ValueError(f'Hotspot x-coordinate too large: {x_offset}')

            if y_offset > height:
                raise ValueError(f'Hotspot x-coordinate too large: {y_offset}')

            if width not in available_sizes:
                continue

            image_start = position + self.IMAGE_HEADER.size
            image_size = width * height * 4
            blob = self.blob[image_start:image_start + image_size]
            if len(blob) != image_size:
                raise ValueError(f'Invalid image at {image_start}: expected {image_size} bytes, got {len(blob)} bytes')

            image = np.frombuffer(blob, dtype=np.uint8, count=image_size).reshape((height, width, 4))
            cursors.append((image, (width, height), (x_offset, y_offset), nominal_size))

        return cursors

def load_xcursor(cursor_path):
    with open(cursor_path, "rb") as f:
        data = f.read()
    if XCursorParser.can_parse(data):
        parser = XCursorParser(data)
        return parser.parse()
    return None





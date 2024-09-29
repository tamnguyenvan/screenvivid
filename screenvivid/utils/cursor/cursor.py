import platform
from screenvivid.utils.logging import logger

def get_cursor_state_windows():
    import win32gui
    import win32con
    cursor_info = win32gui.GetCursorInfo()
    cursor_handle = cursor_info[1]

    # Define a dictionary mapping cursor handles to their states
    cursor_states = {
        win32gui.LoadCursor(0, win32con.IDC_ARROW): "arrow",
        win32gui.LoadCursor(0, win32con.IDC_IBEAM): "ibeam",
        win32gui.LoadCursor(0, win32con.IDC_WAIT): "wait",
        win32gui.LoadCursor(0, win32con.IDC_CROSS): "cross",
        win32gui.LoadCursor(0, win32con.IDC_UPARROW): "uparrow",
        win32gui.LoadCursor(0, win32con.IDC_SIZENWSE): "sizenwse",
        win32gui.LoadCursor(0, win32con.IDC_SIZENESW): "sizenesw",
        win32gui.LoadCursor(0, win32con.IDC_SIZEWE): "sizewe",
        win32gui.LoadCursor(0, win32con.IDC_SIZENS): "sizens",
        win32gui.LoadCursor(0, win32con.IDC_SIZEALL): "sizeall",
        win32gui.LoadCursor(0, win32con.IDC_NO): "no",
        win32gui.LoadCursor(0, win32con.IDC_HAND): "hand",
        win32gui.LoadCursor(0, win32con.IDC_APPSTARTING): "appstarting",
        win32gui.LoadCursor(0, win32con.IDC_HELP): "help",
    }

    # Get the cursor state
    anim_info = {
        "is_anim": False,
        "n_steps": 1,
    }
    AVAILABLE_ANIM_CURSORS = ["appstarting", "wait"]
    state = cursor_states.get(cursor_handle, "arrow")
    if state in AVAILABLE_ANIM_CURSORS:
        anim_info["is_anim"] = True
        anim_info["n_steps"] = 18
        logger.debug(f"{state} cursor is an animation cursor.")
    logger.debug(f"{state} cursor found.")
    return state, anim_info

def get_cursor_state_linux(cursor_theme):
    from Xlib import display
    import numpy as np
    from Xlib.ext import xfixes

    d = display.Display()
    if not d.has_extension('XFIXES'):
        logger.error('XFIXES extension not supported.')
        return

    xfixes_version = d.xfixes_query_version()

    root = d.screen().root

    image = d.xfixes_get_cursor_image(root)
    cursor_image = image.cursor_image
    width, height = image.width, image.height

    cursor_data = np.array(cursor_image, dtype=np.uint32).reshape(height, width)

    bgra = np.zeros((height, width, 4), dtype=np.uint8)
    bgra[..., 0] = cursor_data & 0xFF          # Blue
    bgra[..., 1] = (cursor_data >> 8) & 0xFF   # Green
    bgra[..., 2] = (cursor_data >> 16) & 0xFF  # Red
    bgra[..., 3] = (cursor_data >> 24) & 0xFF  # Alpha

    anim_info = {
        "is_anim": False,
        "n_steps": 1,
    }

    # Match the rgba image with the 24x24 image in the cursor theme
    AVAILABLE_ANIM_CURSORS = ["wait", "progress", "watch"]
    if width in cursor_theme:
        for cursor_state, cursors  in cursor_theme[width].items():
            total_cursors = len(cursors)
            for cursor_info in cursors:
                if np.array_equal(bgra, cursor_info["image"]):
                    logger.debug(f"{cursor_state} cursor found.")
                    if cursor_state in AVAILABLE_ANIM_CURSORS:
                        logger.debug(f"{cursor_state} cursor is an animation cursor.")
                        anim_info["is_anim"] = True
                        anim_info["n_steps"] = total_cursors
                    return cursor_state, anim_info

    logger.debug(f"No cursor found fallback to arrow.")
    return "arrow", anim_info

def get_cursor_state_macos(cursor_theme):
    import AppKit
    import Quartz
    from Cocoa import NSBitmapImageRep, NSPNGFileType
    import io
    from PIL import Image
    import numpy as np

    # Get current cursor
    cursor = Quartz.NSCursor.currentSystemCursor()
    image = cursor.image()
    size = image.size()
    width, height = int(size.width), int(size.height)
    bitmap_rep = NSBitmapImageRep.imageRepWithData_(image.TIFFRepresentation())

    png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)

    buffer = io.BytesIO(png_data)
    img_array = Image.open(buffer)
    rgba = np.array(img_array)
    bgra = rgba[..., ::-1]

    anim_info = {
        "is_anim": False,
        "n_steps": 1,
    }

    AVAILABLE_ANIM_CURSORS = ["wait", "progress", "busy"]

    if width in cursor_theme:
        for cursor_state, cursors  in cursor_theme[width].items():
            total_cursors = len(cursors)
            for cursor_info in cursors:
                if np.array_equal(bgra, cursor_info["image"]):
                    logger.debug(f"{cursor_state} cursor found.")
                    if cursor_state in AVAILABLE_ANIM_CURSORS:
                        logger.debug(f"{cursor_state} cursor is an animation cursor.")
                        anim_info["is_anim"] = True
                        anim_info["n_steps"] = total_cursors
                    return cursor_state, anim_info

    logger.debug(f"No cursor found fallback to arrow.")
    return "arrow", anim_info

def get_cursor_state(cursor_theme):
    current_platform = platform.system()
    if current_platform == "Windows":
        return get_cursor_state_windows()
    elif current_platform == "Linux":
        return get_cursor_state_linux(cursor_theme)
    elif current_platform == "Darwin":
        return get_cursor_state_macos(cursor_theme)
    else:
        raise NotImplementedError(f"Cursor image capture is not implemented for {current_platform}.")
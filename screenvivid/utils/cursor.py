import platform

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
        win32gui.LoadCursor(0, win32con.IDC_NO): "no",
        win32gui.LoadCursor(0, win32con.IDC_HAND): "hand",
        win32gui.LoadCursor(0, win32con.IDC_APPSTARTING): "appstarting",
        win32gui.LoadCursor(0, win32con.IDC_HELP): "help",
    }

    # Get the cursor state
    for handle, state in cursor_states.items():
        if cursor_handle == handle:
            return state

    # If the cursor is not recognized, return "unknown"
    return "arrow"

# def get_cursor_image_linux():
#     from Xlib import display
#     from Xlib.ext import xfixes

#     d = display.Display()
#     if not d.has_extension('XFIXES'):
#         print('XFIXES extension not supported')
#         return

#     xfixes_version = d.xfixes_query_version()

#     root = d.screen().root

#     image = d.xfixes_get_cursor_image(root)
#     cursor_image = image.cursor_image
#     width, height = image.width, image.height

#     cursor_data = np.array(cursor_image, dtype=np.uint32).reshape(height, width)

#     rgba = np.zeros((height, width, 4), dtype=np.uint8)
#     rgba[..., 0] = (cursor_data >> 16) & 0xFF  # Red
#     rgba[..., 1] = (cursor_data >> 8) & 0xFF   # Green
#     rgba[..., 2] = cursor_data & 0xFF          # Blue
#     rgba[..., 3] = (cursor_data >> 24) & 0xFF  # Alpha

#     return rgba
def get_cursor_state_linux():
    return "arrow"

def get_cursor_state_macos():
    import Quartz

    # Get current cursor
    cursor = Quartz.NSCursor.currentSystemCursor()

    # Define a mapping of cursor names to states
    cursor_states = {
        "arrowCursor": "arrow",
        "IBeamCursor": "ibeam",
        "crosshairCursor": "cross",
        "closedHandCursor": "closed_hand",
        "openHandCursor": "open_hand",
        "pointingHandCursor": "pointing_hand",
        "resizeLeftCursor": "resize_left",
        "resizeRightCursor": "resize_right",
        "resizeLeftRightCursor": "resize_left_right",
        "resizeUpCursor": "resize_up",
        "resizeDownCursor": "resize_down",
        "resizeUpDownCursor": "resize_up_down",
        "disappearingItemCursor": "disappearing_item",
        "contextualMenuCursor": "contextual_menu",
        "dragCopyCursor": "drag_copy",
        "dragLinkCursor": "drag_link",
        "operationNotAllowedCursor": "operation_not_allowed"
    }

    # Get the cursor name
    cursor_name = cursor.name()

    # Return the corresponding state or "arrow" if not recognized
    return cursor_states.get(cursor_name, "arrow")

def get_cursor_state():
    current_platform = platform.system()
    if current_platform == "Windows":
        return get_cursor_state_windows()
    elif current_platform == "Linux":
        return get_cursor_state_linux()
    elif current_platform == "Darwin":
        return get_cursor_state_macos()
    else:
        raise NotImplementedError(f"Cursor image capture is not implemented for {current_platform}")
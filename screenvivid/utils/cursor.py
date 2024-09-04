import platform
import numpy as np

def get_cursor_image_windows():
    import win32gui
    import win32ui
    from ctypes import windll, Structure, c_long, byref

    class POINT(Structure):
        _fields_ = [("x", c_long), ("y", c_long)]

    # Get cursor position
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))

    # Get the cursor bitmap
    hcursor = win32gui.GetCursorInfo()[1]
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 32, 32)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    windll.user32.DrawIconEx(hdc.GetHandleOutput(), 0, 0, hcursor, 32, 32, 0, None, 0x0003)

    # Convert to numpy array
    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype=np.uint8).reshape(bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

    # Clean up
    win32gui.DeleteObject(hbmp.GetHandle())
    hdc.DeleteDC()

    return img

def get_cursor_image_linux():
    from Xlib import display
    from Xlib.ext import xfixes

    d = display.Display()
    if not d.has_extension('XFIXES'):
        print('XFIXES extension not supported')
        return

    xfixes_version = d.xfixes_query_version()
    # print('Found XFIXES version {}.{}'.format(
    #     xfixes_version.major_version,
    #     xfixes_version.minor_version
    # ))

    root = d.screen().root

    image = d.xfixes_get_cursor_image(root)
    cursor_image = image.cursor_image
    width, height = image.width, image.height

    cursor_data = np.array(cursor_image, dtype=np.uint32).reshape(height, width)

    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    rgba[..., 0] = (cursor_data >> 16) & 0xFF  # Red
    rgba[..., 1] = (cursor_data >> 8) & 0xFF   # Green
    rgba[..., 2] = cursor_data & 0xFF          # Blue
    rgba[..., 3] = (cursor_data >> 24) & 0xFF  # Alpha

    return rgba

def get_cursor_image_macos():
    import Quartz
    import CoreGraphics

    # Get cursor image
    cursor = Quartz.NSCursor.currentSystemCursor()
    image = cursor.image()

    # Get image dimensions
    width = int(image.size().width)
    height = int(image.size().height)

    # Create a bitmap context to draw the cursor image
    color_space = CoreGraphics.CGColorSpaceCreateDeviceRGB()
    context = CoreGraphics.CGBitmapContextCreate(
        None, width, height, 8, width * 4, color_space,
        CoreGraphics.kCGImageAlphaPremultipliedLast
    )

    # Draw the cursor image into the context
    CoreGraphics.CGContextDrawImage(
        context, CoreGraphics.CGRectMake(0, 0, width, height), image.CGImage()
    )

    # Get the raw image data
    data = CoreGraphics.CGBitmapContextGetData(context)

    # Convert to numpy array
    buffer = data.tobytes()
    img_array = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

    return img_array

def get_cursor_image():
    current_platform = platform.system()
    if current_platform == "Windows":
        return get_cursor_image_windows()
    elif current_platform == "Linux":
        return get_cursor_image_linux()
    elif current_platform == "Darwin":
        return get_cursor_image_macos()
    else:
        raise NotImplementedError(f"Cursor image capture is not implemented for {current_platform}")
from screenvivid.utils.general import get_os_name

class BaseScreenCapture:
    def __init__(self, region=None):
        self._region = region

    def __enter__(self):
        """
        Called when entering the context.
        Prepares resources if necessary.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when exiting the context.
        Cleans up resources if necessary.
        """
        self.cleanup()

    def capture(self):
        """
        Capture the screen or region. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the 'capture' method.")

    def cleanup(self):
        """
        Clean up resources. Subclasses can override this method.
        """
        pass


class MSSScreenCapture(BaseScreenCapture):
    def __init__(self, region=None):
        super().__init__(region)
        import mss
        self._sct = mss.mss()
        self._region = self._get_mss_region(region)

    def _get_mss_region(self, region):
        """
        Get the monitor (screen) details based on the region.
        If region is None, capture the entire screen. Otherwise, capture the specified region.
        """
        if region:
            return {"top": int(region[1]), "left": int(region[0]), "width": int(region[2]), "height": int(region[3])}
        else:
            return self._sct.monitors[0]

    def capture(self):
        """
        Capture the screen or a specified region using mss.
        :return: Raw image bytes in RGB format.
        """
        screenshot = self._sct.grab(self._region)
        bgra = screenshot.bgra

        return bgra, "bgra"

    def cleanup(self):
        """
        Cleanup resources specific to mss.
        """
        if hasattr(self, '_sct'):
            self._sct.close()

class QuartzScreenCapture(BaseScreenCapture):
    def capture(self):
        """
        Capture the screen or region using Quartz on macOS.
        :return: Image bytes of the captured screen.
        """
        import objc
        import Foundation
        import Quartz
        import UniformTypeIdentifiers

        with objc.autorelease_pool():
            if self._region:
                rect = Quartz.CGRectMake(self._region[0], self._region[1], self._region[2], self._region[3])
                screenshot = Quartz.CGDisplayCreateImage(Quartz.CGMainDisplayID())
                screenshot_region = Quartz.CGImageCreateWithImageInRect(screenshot, rect)
            else:
                screenshot_region = Quartz.CGDisplayCreateImage(Quartz.CGMainDisplayID())

            data = Foundation.NSMutableData.data()
            dest = Quartz.CGImageDestinationCreateWithData(
                data,
                UniformTypeIdentifiers.UTTypeJPEG.identifier(),
                1,
                None
            )
            Quartz.CGImageDestinationAddImage(dest, screenshot_region, None)
            Quartz.CGImageDestinationFinalize(dest)
            return bytes(data), "jpeg"


def get_screen_capture_class(region=None):
    """
    Factory method to return the appropriate ScreenCapture class based on OS.
    """
    if get_os_name() == "macos":  # macOS
        return QuartzScreenCapture
    else:  # Linux, Windows
        return MSSScreenCapture
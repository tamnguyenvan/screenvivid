from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage

class FrameImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        self.frame = QImage()

    def requestImage(self, id, size, requestedSize):
        return self.frame

    def updateFrame(self, frame):
        self.frame = frame

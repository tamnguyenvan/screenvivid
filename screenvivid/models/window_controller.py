from PySide6.QtCore import (
    QObject, Property, Slot, Signal, QPoint
)
from PySide6.QtGui import QGuiApplication

class WindowControllerModel(QObject):

    topChanged = Signal(int)
    leftChanged = Signal(int)
    widthChanged = Signal()
    heightChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._window_geometry = None

    @Property(int, notify=topChanged)
    def top(self):
        return self._window_geometry.top()

    @Property(int, notify=leftChanged)
    def left(self):
        return self._window_geometry.left()

    @Property(int, notify=widthChanged)
    def width(self):
        return self._window_geometry.width()

    @Property(int, notify=heightChanged)
    def height(self):
        return self._window_geometry.height()

    @Slot(result="QPoint")
    def get_window_position(self):
        screen = QGuiApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        self._window_geometry = available_geometry
        return QPoint(available_geometry.x(), available_geometry.y())

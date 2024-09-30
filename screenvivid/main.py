import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from screenvivid import rc_main
from screenvivid import rc_icons
from screenvivid import rc_images
from screenvivid.model import (
    ClipTrackModel, WindowController, VideoController, VideoRecorder, Logger
)
from screenvivid.image_provider import FrameImageProvider
from screenvivid.utils.logging import logger

def main():
    logger.info("Starting ScreenVivid")
    app = QGuiApplication(sys.argv)

    # Determine the path to the icon
    if getattr(sys, 'frozen', False):
        # If running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # If running in a regular Python environment
        base_path = Path(__file__).resolve().parent

    icon_path = base_path / "resources/icons/screenvivid.ico"
    logger.debug(f"Setting icon to {icon_path}")
    app.setWindowIcon(QIcon(str(icon_path)))
    engine = QQmlApplicationEngine()
    logger.debug("Created QQmlApplicationEngine")

    # Image provider
    frame_provider = FrameImageProvider()
    engine.addImageProvider("frames", frame_provider)
    logger.debug("Added image provider")

    # Models
    clip_track_model = ClipTrackModel()
    window_controller = WindowController()

    video_controller = VideoController(frame_provider=frame_provider)
    video_recorder = VideoRecorder()
    logger_model = Logger()

    engine.rootContext().setContextProperty("clipTrackModel", clip_track_model)
    engine.rootContext().setContextProperty("windowController", window_controller)
    engine.rootContext().setContextProperty("videoController", video_controller)
    engine.rootContext().setContextProperty("videoRecorder", video_recorder)
    engine.rootContext().setContextProperty("logger", logger_model)
    logger.debug("Set context properties")

    qml_file = "qrc:/qml/entry/main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        logger.error("Failed to load QML file")
        sys.exit(-1)
    logger.debug("Loaded QML file")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
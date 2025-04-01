import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from screenvivid import rc_main
from screenvivid import rc_icons
from screenvivid import rc_images
from screenvivid.models import (
    ClipTrackModel, WindowControllerModel, VideoControllerModel, ScreenRecorderModel, LoggerModel
)
from screenvivid.image_provider import FrameImageProvider
from screenvivid.models.logger import logger

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
    
    # Add import paths for QML components
    qml_base_path = base_path / "qml"
    engine.addImportPath(str(qml_base_path))
    logger.debug(f"Added QML import path: {qml_base_path}")
    
    # Add specific component paths
    studio_path = qml_base_path / "studio"
    engine.addImportPath(str(studio_path))
    logger.debug(f"Added QML import path: {studio_path}")

    # Image provider
    frame_provider = FrameImageProvider()
    engine.addImageProvider("frames", frame_provider)
    logger.debug("Added image provider")

    # Models
    clip_track_model = ClipTrackModel()
    window_controller = WindowControllerModel()

    video_controller = VideoControllerModel(frame_provider=frame_provider)
    screen_recorder = ScreenRecorderModel()
    logger_model = LoggerModel()

    engine.rootContext().setContextProperty("clipTrackModel", clip_track_model)
    engine.rootContext().setContextProperty("windowController", window_controller)
    engine.rootContext().setContextProperty("videoController", video_controller)
    engine.rootContext().setContextProperty("screenRecorder", screen_recorder)
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
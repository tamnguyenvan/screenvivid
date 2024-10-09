from PySide6.QtCore import QObject, Slot
from screenvivid.utils.logging import logger

class LoggerModel(QObject):
    def __init__(self):
        super().__init__()

    @Slot(str)
    def info(self, message):
        logger.info(message)

    @Slot(str)
    def debug(self, message):
        logger.debug(message)

    @Slot(str)
    def warning(self, message):
        logger.warning(message)

    @Slot(str)
    def error(self, message):
        logger.error(message)

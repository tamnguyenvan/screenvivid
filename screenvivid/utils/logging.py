import os
import sys
import tempfile
from loguru import logger

logger.remove()

log_level = os.getenv("SCREENVIVID_LOG_LEVEL", "INFO")
if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
    log_level = "INFO"

# Check if sys.stderr is not None before adding it as a handler
if sys.stderr is not None:
    logger.add(sys.stderr, level=log_level)

logger.add(
    os.path.join(tempfile.gettempdir(), "screenvivid.log"),
    rotation="5 MB",
    level=log_level
)
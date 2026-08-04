"""
Loguru Logging Setup for OGSM Portal.
"""

import sys
from loguru import logger

# Clear standard handlers
logger.remove()

# Add structured console logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<=8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

def get_logger():
    return logger

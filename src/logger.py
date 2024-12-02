import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
filename = os.path.join(log_dir, "main.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(filename, maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

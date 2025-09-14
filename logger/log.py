import logging
import os
from datetime import datetime
from colorlog import ColoredFormatter

def setup_logger(name: str = "app_logger", level=logging.INFO) -> logging.Logger:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # File formatter (no colors)
    file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

    # Colored console formatter
    color_formatter = ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
        }
    )

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(file_formatter)

    # Console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger





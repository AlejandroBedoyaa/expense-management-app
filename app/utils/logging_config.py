"""
Logging configuration for the application.
"""

import logging
import sys
import os

def setup_logging():
    """Setup logging configuration for the application."""
    # Clean any handler created before
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

    # Principal handler
    LOG_BOT_FILE = os.getenv('LOG_BOT_FILE', os.path.join('logs', 'bot.log'))
    file_handler = logging.FileHandler(LOG_BOT_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

    # External libraries handler
    EXTERNAL_LOG_FILE = os.getenv('LOG_BOT_EXTERNAL_LIBS_FILE', os.path.join('logs', 'external_libs.log'))
    external_handler = logging.FileHandler(EXTERNAL_LOG_FILE, encoding='utf-8')
    external_handler.setLevel(logging.INFO)
    external_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

    # Config loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    for lib in ["telegram", "httpx", "requests", "paddleocr", "paddle", "paddlex"]:
        lib_logger = logging.getLogger(lib)
        lib_logger.handlers = []
        lib_logger.propagate = False
        lib_logger.addHandler(external_handler)

    os.environ["GLOG_minloglevel"] = "2"
    os.environ["FLAGS_log_level"] = "3"
    os.environ["PADDLE_LOG_LEVEL"] = "ERROR"
    os.environ["KMP_WARNINGS"] = "FALSE"

    logging.info("Logger initialized.")
    logging.info("Bot log folder set to: %s", LOG_BOT_FILE)
    logging.info("External libraries log folder set to: %s", EXTERNAL_LOG_FILE)


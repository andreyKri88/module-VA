import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logs:
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # File handler
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_dir / f"{self.name.lower()}.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

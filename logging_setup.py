import logging
import logging.config
from pathlib import Path


def get_logger(logger_name):
    Path("backup-system-logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=[
            logging.FileHandler("backup-system-logs/file.log", mode="a"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(logger_name)

import logging
import sys
from pathlib import Path


log_dir = Path("log").absolute()
if log_dir.exists():
    if not log_dir.is_dir():
        raise OSError(f"'{log_dir} exists but not a dir.'")
else:
    log_dir.mkdir()


class DeepSeekLogger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name, logging.DEBUG)
        self.formatter = logging.Formatter(
            "[%(asctime)s %(levelname)s:%(name)s] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        self.file_handler = logging.FileHandler(log_dir / "deepseek.log")
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

        self.addHandler(self.file_handler)
        self.addHandler(self.console_handler)
        return


dummy_logger = logging.Logger("dummy")
dummy_logger.addHandler(logging.StreamHandler())

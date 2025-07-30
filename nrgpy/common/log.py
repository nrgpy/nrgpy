import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from typing import Optional

TOKEN_FILE = ".cloud_token"
LOGFILE_NAME = "nrgpy.log"


class NrgPythonLog(logging.Logger):
    """
    Logging utility for nrgpy with environment variable support.

    Environment Variables:
        NRGPY_LOG_DIRECTORY: Override log directory.
        NRGPY_LOG_LEVEL: Override log level (e.g., DEBUG, INFO).
        NRGPY_NO_LOG_FILES: If "1", disables file logging.
    """

    def __init__(self, name: str = "nrgpy", level: Optional[int] = None) -> None:
        self.token_file_name: str = ".cloud_token"
        self.logfile_name: str = f"{name}.log"
        self.log_directory: str = self._get_log_directory()
        self.logfile: str = os.path.join(self.log_directory, self.logfile_name)
        self.token_file: str = os.path.join(self.log_directory, self.token_file_name)
        self.no_log_files: bool = self._get_no_log_files()
        self._log_level: int = self._get_log_level() if level is None else level
        super().__init__(name, self._log_level)
        self._configure_logger()

    def _get_log_directory(self) -> str:
        env_dir = os.environ.get("NRGPY_LOG_DIRECTORY")
        if env_dir:
            try:
                os.makedirs(env_dir, exist_ok=True)
            except Exception:
                print(traceback.format_exc())
                return "."
            return env_dir
        try:
            home_dir = os.path.expanduser("~/")
            default_dir = os.path.join(home_dir, ".nrgpy")
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            print(traceback.format_exc())
            return "."

    def _get_log_level(self) -> int:
        env_level = os.environ.get("NRGPY_LOG_LEVEL")
        if env_level:
            return getattr(logging, env_level.upper(), logging.INFO)
        return logging.INFO

    def _get_no_log_files(self) -> bool:
        return os.environ.get("NRGPY_NO_LOG_FILES", "0") == "1"

    def _configure_logger(self) -> None:
        self.setLevel(self._log_level)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | [%(module)s:%(lineno)d] | %(message)s"
        )
        if not self.no_log_files:
            try:
                handler = RotatingFileHandler(
                    self.logfile, maxBytes=1024 * 1000, backupCount=4
                )
                handler.setFormatter(formatter)
                self.addHandler(handler)
            except Exception:
                print(traceback.format_exc())
        # Always add a stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)

    def set_log_directory(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        self.log_directory = directory
        self.logfile = os.path.join(directory, self.logfile_name)
        self.token_file = os.path.join(directory, self.token_file_name)
        self._reset_handlers()

    def set_log_level(self, level: str) -> None:
        self._log_level = getattr(logging, level.upper(), logging.INFO)
        self.setLevel(self._log_level)

    def set_no_log_files(self, no_log_files: bool) -> None:
        self.no_log_files = no_log_files
        self._reset_handlers()

    def _reset_handlers(self) -> None:
        for handler in self.handlers[:]:
            self.removeHandler(handler)
        self._configure_logger()

    def get_token_file(self) -> str:
        return self.token_file


# Register the custom logger class so logging.getLogger() can use it if desired
logging.setLoggerClass(NrgPythonLog)

# Provide a backward-compatible log object for legacy code
_log: NrgPythonLog = NrgPythonLog()
log: logging.Logger = logging.getLogger("nrgpy")
TOKEN_FILE: str = _log.get_token_file()

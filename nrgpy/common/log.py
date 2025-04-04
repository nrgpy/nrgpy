import getpass
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback


token_file_name = ".cloud_token"
logfile_name = "nrgpy.log"

try:
    username = getpass.getuser()
    home_dir = os.path.expanduser("~/")

    os.makedirs(os.path.join(home_dir, ".nrgpy"), exist_ok=True)

    logfile = os.path.join(home_dir, ".nrgpy", logfile_name)
    token_file = os.path.join(home_dir, ".nrgpy", token_file_name)

except Exception:
    print(traceback.format_exc())
    logfile = logfile_name
    token_file = token_file_name

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(module)s:%(lineno)d] | %(message)s"
)

size_handler = RotatingFileHandler(logfile, maxBytes=1024 * 1000, backupCount=4)
size_handler.setFormatter(formatter)

log.addHandler(size_handler)
log.debug("nrgpy initialized")

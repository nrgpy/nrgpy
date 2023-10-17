import getpass
import logging
from logging.handlers import RotatingFileHandler
import os
from sys import platform
import traceback


token_file_name = ".cloud_token"
logfile_name = "nrgpy.log"

try:
    username = getpass.getuser()

    if platform == "win32":
        home_dir = f"C:/Users/{username}"
    else:
        home_dir = f"/home/{username}"

    os.makedirs(os.path.join(home_dir, ".nrgpy"), exist_ok=True)

    logfile = os.path.join(home_dir, ".nrgpy", logfile_name)
    token_file = os.path.join(home_dir, ".nrgpy", token_file_name)

except Exception:
    print(traceback.format_exc())
    logfile = logfile_name
    token_file = token_file_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(module)s:%(lineno)d] | %(message)s"
)

size_handler = RotatingFileHandler(logfile, maxBytes=1024 * 1000, backupCount=4)
size_handler.setFormatter(formatter)

logger.addHandler(size_handler)
logger.debug("nrgpy initialized")


from .read.channel_info_arrays import return_array  # noqa: E402, F401
from .convert.convert_rld import local as local_rld, nrg_convert_api  # noqa: E402, F401
from .convert.convert_rwd import local as local_rwd  # noqa: E402, F401
from .api.auth import nrg_api  # noqa: E402, F401
from .api.catalog import nrg_api_catalog  # noqa: E402, F401
from .api.convert import nrg_api_convert  # noqa: E402, F401
from .api.export import nrg_api_export  # noqa: E402, F401
from .api.upload import nrg_api_upload  # noqa: E402, F401
from .cloud_api.auth import cloud_api, CloudApi  # noqa: E402, F401
from .cloud_api.convert import cloud_convert, CloudConvert # noqa: E402, F401
from .cloud_api.export import cloud_export, CloudExport  # noqa: E402, F401
from .cloud_api.jobs import export_job, CloudExportJob  # noqa: E402, F401
from .cloud_api.sites import cloud_sites, CloudSites  # noqa: E402, F401
from .cloud_api.upload import cloud_import, CloudImport  # noqa: E402, F401
from .quality.quality import check_intervals, select_interval_length  # noqa: E402, F401
from .read.logr import LogrRead, logr_read  # noqa: E402, F401
from .read.spidar_txt import SpidarRead, spidar_data_read  # noqa: E402, F401
from .read.sympro_txt import SymProTextRead, sympro_txt_read, shift_timestamps  # noqa: E402, F401, E501
from .read.txt_utils import read_text_data  # noqa: E402, F401
from .utils.encodings import convert_utf16le_to_utf8  # noqa: E402, F401
from .utils.ipk2lgr import ipk2lgr  # noqa: E402, F401
from .utils.utilities import (  # noqa: E402
    check_platform,  # noqa: F401
    windows_folder_path,  # noqa: F401
    linux_folder_path,  # noqa: F401
    save,  # noqa: F401
    load,  # noqa: F401
    data_months,  # noqa: F401
    string_date_check,  # noqa: F401
    create_spd_filename_from_cloud_export,  # noqa: F401
    rename_cloud_export_like_spd,  # noqa: F401
    set_start_stop,  # noqa: F401
)

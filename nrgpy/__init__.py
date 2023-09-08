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


from .read.channel_info_arrays import return_array
from .convert.convert_rld import local as local_rld, nrg_convert_api
from .convert.convert_rwd import local as local_rwd
from .api.auth import nrg_api
from .api.catalog import nrg_api_catalog
from .api.convert import nrg_api_convert
from .api.export import nrg_api_export
from .api.upload import nrg_api_upload
from .cloud_api.auth import cloud_api, CloudApi
from .cloud_api.convert import cloud_convert, CloudConvert
from .cloud_api.export import cloud_export, CloudExport
from .cloud_api.jobs import export_job, CloudExportJob
from .cloud_api.sites import cloud_sites, CloudSites
from .cloud_api.upload import cloud_import, CloudImport
from .quality.quality import check_intervals, select_interval_length
from .read.logr import LogrRead, logr_read
from .read.spidar_txt import SpidarRead, spidar_data_read
from .read.sympro_txt import SymProTextRead, sympro_txt_read, shift_timestamps
from .read.txt_utils import read_text_data
from .utils.encodings import convert_utf16le_to_utf8
from .utils.ipk2lgr import ipk2lgr
from .utils.utilities import (
    check_platform,
    windows_folder_path,
    linux_folder_path,
    save,
    load,
    data_months,
    string_date_check,
    create_spd_filename_from_cloud_export,
    rename_cloud_export_like_spd,
    set_start_stop,
)

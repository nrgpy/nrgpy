try:
    from nrgpy import logger
except ImportError:
    pass
from datetime import datetime
import json
from nrgpy.utils.utilities import (
    draw_progress_bar,
)
from .auth import create_export_job_url, export_job_url, is_authorized
from .export import cloud_export
import os
import requests
import sys
import time
import traceback
import zipfile


class export_job(cloud_export):
    """Uses NRG hosted web-based API to download data in text format as an export job
    To sign up for the service, go to https://cloud.nrgsystems.com

    Note that the site must exist in the NRG Cloud platform, and you must have
    Contributor or Administrator level access to the site to use these features.

    Use for creating exports of any size. Extends nrgpy.cloud_export class

    Parameters
    ----------
    out_dir : str (path-like)
        path to save exported data
    site_id : int
        NRG Cloud site identifier (NOT the site number)
    site_number : int
        site number
    logger_sn : str or int
        serial number of data logger (like, 820612345)
    start_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    end_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    client_id : str
        available in the NRG Cloud portal
    client_secret : str
        available in the NRG Cloud portal
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : str
        ['measurements'], 'diagnostic', 'events', 'communication'
    file_format : str
        ['txt'], 'rld', 'zx' - whether tab-delimited text or binary output
    interval : str, optional
        'oneMinute', 'twoMinute', 'fiveMinute', 'tenMinute', 'fifteenMinute',
        'thirtyMinute', 'Hour', 'Day'
        must be a multiple of the logger's statistical interval. if not specified, will use
        "native" interval (usually oneMinute for solar, tenMinute for wind)
    separate_txt_files : bool
            (False) set to True to return original CSV files in export (ZX only)
    unzip : bool
        (True) whether to extract the .txt data file from the .zip file

    Returns
    -------
    object
        export object, including API response

    Examples
    --------
    Download one year of data with an NEC file applied, and read data

    >>> import nrgpy
    >>>
    >>> client_id = "go to https://cloud.nrgsystems.com for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com for access"
    >>> save_dir = '/path/to/exported/data'
    >>>
    >>> exporter = nrgpy.export_job(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=save_dir,
            nec_file='12vbat.nec',
            site_number=3456,
            start_date="2021-04-01",
            end_date="2022-03-31",
            file_format="txt",     # <--- can be "rld" for raw SymPRO data files, or "zx" for ZX 300
            unzip=True,
        )
    >>>
    >>> exporter.create_export_job()
    >>> exporter.monitor_export_job(download=True)
    >>> # read resulting files
    >>> reader = nrgpy.sympro_txt_read(exporter.export_filepath)
    >>> reader.format_site_data()
    >>> if reader:
    >>>     print(f"Site number               : {reader.site_number}")
    >>>     print(f"Site description          : {reader.site_description}")
    >>>     reader.interval_check = nrgpy.check_intervals(reader.data)
    >>> else:
    >>>     print("unable to get reader")


    Download 15 days of data files from ZX 300 lidar site

    >>> import nrgpy
    >>>
    >>> client_id = "go to https://cloud.nrgsystems.com for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com for access"
    >>> save_dir = '/path/to/exported/data'
    >>>
    >>> exporter = nrgpy.export_job(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=save_dir,
            site_number=567,
            start_date="2022-09-01",
            end_date="2022-09-15",
            file_format="zx",
            separate_txt_files=False,
            unzip=True,
        )
    >>>
    >>> exporter.create_export_job()
    >>> exporter.monitor_export_job(download=True)
    """

    def __init__(
        self,
        out_dir="",
        site_id="",
        site_number="",
        logger_sn="",
        start_date="2014-01-01",
        end_date="2023-12-31",
        file_format="txt",
        client_id="",
        client_secret="",
        nec_file="",
        export_type="measurements",
        separate_txt_files=False,
        interval="",
        unzip=True,
        **kwargs,
    ):

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=out_dir,
            site_id=site_id,
            site_number=site_number,
            logger_sn=logger_sn,
            start_date=start_date,
            end_date=end_date,
            file_format=file_format,
            nec_file=nec_file,
            export_type=export_type,
            interval=interval,
            separate_txt_files=separate_txt_files,
            unzip=unzip,
        )
        pass

    def create_export_job(self):
        """Create export job"""
        try:
            self.headers = {"Authorization": "Bearer " + self.session_token}
        except TypeError:
            return False

        self.data = {
            "siteid": self.site_id,
            "fromdate": self.start_date,
            "todate": self.end_date,
            "fileFormat": self.file_format,
            "NecFileBytes": self.encoded_nec_string,
            "exporttype": self.export_type,
            "isOldZxExport": self.separate_txt_files,
        }

        if self.interval:
            self.data["interval"] = self.interval

        self.request_time = datetime.now()
        self.export_request_time = datetime.now()
        logger.debug(f"creating export job for site {self.site_id}")
        self.resp = requests.post(
            json=self.data, url=create_export_job_url, headers=self.headers
        )
        self.request_duration = datetime.now() - self.request_time
        if not is_authorized(self.resp):
            return False

        try:
            self.json_response = json.loads(self.resp.content)
            self.job_id = self.json_response["jobId"]
            logger.info(f"created export job {self.job_id} for site {self.site_id}")
            print(f"created export job {self.job_id} for site {self.site_id}")
        except:
            logger.error(
                f"unable to create export job for {self.site_id}, {self.start_date}, {self.end_date}"
            )
            logger.debug(traceback.format_exc())
            return False

    def check_export_job(self):
        """Checks the status of an export job

        Uses self.job_id as reference
        """
        try:
            self.headers = {"Authorization": "Bearer " + self.session_token}
        except TypeError:
            return False
        self.request_time = datetime.now()
        self.resp = requests.get(
            url=f"{export_job_url}?jobId={self.job_id}&download=false",
            headers=self.headers,
        )
        if self.resp.status_code == 200:
            self.json_response = json.loads(self.resp.content)
            self.status = self.json_response["status"]

        elif not is_authorized(self.resp):
            return False
        else:
            logger.error(f"could not get status for {self.job_id}")
            logger.debug(f"{self.resp.status_code} | {self.resp.reason}")
            logger.debug(self.resp.text.split(":")[1].split('"')[1])
            print(str(self.resp.status_code) + " | " + self.resp.reason)
            print(self.resp.text.split(":")[1].split('"')[1])
            return False

    def monitor_export_job(self, download=False):
        """Monitor the status of an export job

        Uses self.job_id as reference
        """
        stop = False
        start = datetime.now()
        i = 0

        try:
            while not stop:
                i += 1
                self.check_export_job()
                if (
                    self.json_response["status"].lower() == "error"
                    or self.json_response["status"].lower() == "completed"
                ):
                    stop = True

                sys.stdout.write("\r")
                sys.stdout.write(
                    f"job ID {self.job_id} | time elapsed: {(datetime.now() - start).seconds} s | status: {self.json_response['status'].lower()}                           "
                )
                time.sleep(0.5)
            if download:
                if self.json_response["status"].lower() == "completed":
                    print(f"\nDownloading export job {self.job_id}")
                    logger.info(f"\nDownloading export job {self.job_id}")
                    self.download_export()
                else:
                    print(f"Unable to download export job")
                    logger.error(f"Unable to download export job")
        except KeyboardInterrupt:
            print("Keyboard Interrupt detected: stopping monitoring")
            logger.info("Keyboard Interrupt detected: stopping monitoring")

    def download_export(self):
        try:
            self.headers = {"Authorization": "Bearer " + self.session_token}
        except TypeError:
            return False
        self.request_time = datetime.now()
        self.resp = requests.get(
            url=f"{export_job_url}?jobId={self.job_id}&download=true",
            headers=self.headers,
            stream=True,
        )
        if self.resp.status_code == 200:
            total = int(self.resp.headers.get("content-length", 0))
            dl = 0
            with open(self.filepath, "wb") as f:
                for chunk in self.resp.iter_content(chunk_size=10248):
                    if chunk:
                        f.write(chunk)
                    dl += int(len(chunk))
                    draw_progress_bar(
                        int(dl / 1024), int(total / 1024), self.request_time, label="kB"
                    )

            self.request_duration = datetime.now() - self.request_time

            if self.unzip:
                with zipfile.ZipFile(self.filepath, "r") as z:
                    self.export_filename = z.namelist()[0]
                    z.extractall(self.out_dir)
                os.remove(self.filepath)
                self.export_filepath = os.path.normpath(
                    os.path.join(self.out_dir, self.export_filename)
                )

            else:
                self.export_filepath = os.path.normpath(self.filepath)
                self.export_filename = self.zip_file

            logger.info(f"job_id {self.job_id} for site_id {self.site_id}")
            logger.info(
                f"export took {self.request_duration} for {os.path.getsize(self.export_filepath)} bytes"
            )
        elif not is_authorized(self.resp):
            return False
        else:
            logger.error(f"could not get status for {self.job_id}")
            logger.debug(f"{self.resp.status_code} | {self.resp.reason}")
            logger.debug(self.resp.text.split(":")[1].split('"')[1])
            print(str(self.resp.status_code) + " | " + self.resp.reason)
            print(self.resp.text.split(":")[1].split('"')[1])
            return False

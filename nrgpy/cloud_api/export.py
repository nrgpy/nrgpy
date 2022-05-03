try:
    from nrgpy import logger
except ImportError:
    pass
from datetime import datetime
from nrgpy.utils.utilities import (
    affirm_directory,
)
from .auth import cloud_api, export_url
from .sites import cloud_sites
import os
import requests
import zipfile


class cloud_export(cloud_api):
    """Uses NRG hosted web-based API to download data in text format
    To sign up for the service, go to https://cloud.nrgsystems.com

    Note that the site must exist in the NRG Cloud platform, and you must have
    Contributor or Administrator level access to the site to use these features.

    Use the Site Number or NRG Cloud Site ID to choose the site.

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
    file_format : str
        ['txt'], 'rld' - whether tab-delimited text or binary output
    client_id : str
        available in the NRG Cloud portal
    client_secret : str
        available in the NRG Cloud portal
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : str
        ['measurements'], 'diagnostic', 'events', 'communication'
    interval : str, optional
        'oneMinute', 'twoMinute', 'fiveMinute', 'tenMinute', 'fifteenMinute',
        'thirtyMinute', 'Hour', 'Day'
        must be a multiple of the logger's statistical interval
    unzip : bool
        (True) whether to extract the .txt data file from the .zip file

    Returns
    -------
    object
        export object, including API response

    Examples
    --------
    Download 15 days of data with an NEC file applied, and read data

    >>> import nrgpy
    >>>
    >>> client_id = "go to https://cloud.nrgsystems.com for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com for access"
    >>> save_dir = '/path/to/exported/data'
    >>>
    >>> exporter = nrgpy.cloud_export(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=save_dir,
            nec_file='12vbat.nec',
            site_id=245,
            start_date="2021-05-01",
            end_date="2021-05-15",
        )
    >>> exporter.export()
    >>> # read result
    >>> reader = nrgpy.sympro_txt_read(exporter.export_filepath)
    >>> reader.format_site_data()
    >>> if reader:
    >>>     print(f"Site number               : {reader.site_number}")
    >>>     print(f"Site description          : {reader.site_description}")
    >>>     reader.interval_check = nrgpy.check_intervals(reader.data)
    >>> else:
    >>>     print("unable to get reader")
    """

    def __init__(
        self,
        out_dir="",
        site_id="",
        site_number="",
        logger_sn="",
        start_date="2014-01-01",
        end_date="2030-12-31",
        file_format="txt",
        client_id="",
        client_secret="",
        nec_file="",
        export_type="measurements",
        interval="",
        unzip=True,
        **kwargs,
    ):

        super().__init__(client_id, client_secret)

        self.zip_file = (
            f"siteid{site_id}_{start_date}_{end_date}_{export_type}.zip".replace(
                ":", "-"
            ).replace(" ", "_")
        )

        self.filepath = os.path.join(out_dir, self.zip_file)
        self.out_dir = out_dir
        affirm_directory(self.out_dir)

        if site_id:
            self.site_id = site_id
        else:
            client_sites = cloud_sites(client_id=client_id, client_secret=client_secret)
            self.site_id = client_sites.get_siteid(
                site_number=site_number, logger_sn=logger_sn
            )

        self.start_date = start_date
        self.end_date = end_date
        self.file_format = file_format
        self.nec_file = nec_file
        self.export_type = export_type
        self.interval = interval
        self.unzip = unzip

        if self.nec_file:
            self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
            self.encoded_nec_string = self.encoded_nec_bytes.decode("utf-8")
        else:
            self.encoded_nec_bytes = ""
            self.encoded_nec_string = ""

    def export(self):

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
        }

        if self.interval:
            self.data["interval"] = self.interval

        self.request_time = datetime.now()
        self.resp = requests.post(json=self.data, url=export_url, headers=self.headers)
        self.request_duration = datetime.now() - self.request_time

        if self.resp.status_code == 200:
            with open(self.filepath, "wb") as f:
                f.write(self.resp.content)

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

            logger.info(f"export created for site_id {self.site_id}")
            logger.info(
                f"export took {self.request_duration} for {os.path.getsize(self.export_filepath)} bytes"
            )

        else:
            logger.error(f"export not created")
            logger.debug(f"{self.resp.status_code} | {self.resp.reason}")
            try:
                logger.debug(self.resp.text.split(":")[1].split('"')[1])
            except:
                pass
            print(str(self.resp.status_code) + " | " + self.resp.reason)
            print(self.resp.text.split(":")[1].split('"')[1])
            return False

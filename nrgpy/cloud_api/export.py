from nrgpy.common.log import log
from datetime import datetime
from nrgpy.utils.utilities import (
    affirm_directory,
)
from nrgpy.cloud_api.auth import CloudApi, cloud_url_base
from nrgpy.cloud_api.sites import cloud_sites
import os
import requests
from typing import Union
import zipfile


class CloudExport(CloudApi):
    """Uses NRG hosted web-based API to download data in text format
    To sign up for the service, go to https://cloud.nrgsystems.com

    Note that the site must exist in the NRG Cloud platform, and you must have
    Contributor or Administrator level access to the site to use these features.

    Use the Site Number or NRG Cloud Site ID to choose the site.

    Attributes
    ----------
    out_dir : str (path-like)
        path to save exported data
    site_id : int
        NRG Cloud site identifier (NOT the site number)
    site_number : int
        site number
    logger_sn : int
        serial number of data logger
    start_date : str ('{YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}')
        start date/time of data export
    end_date : str ('{YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}')
        end date/time of data export
    file_format : {'txt', 'rld', 'zx'}
        whether SymPRO tab-delimited text or binary output or ZX
    client_id : str
        available in the NRG Cloud portal
    client_secret : str
        available in the NRG Cloud portal
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : {'measurements', 'diagnostic', 'events', 'communication', 'samples', 'allTypes'}
        which type of data to export
    interval : {'oneMinute', 'twoMinute', 'fiveMinute', 'tenMinute', 'fifteenMinute',
        'thirtyMinute', 'Hour', 'Day'}, optional
        averaging interval of exported data; must be a multiple of the logger's
        statistical interval
    unzip : bool
        whether to extract the .txt data file from the .zip file
    session_token : str
    headers : str
        headers passed in API call
    data : str
        data passed in API call
    resp : str
        API response
    export_filepath : str (path-like)
        path of export file


    Examples
    --------
    Download 15 days of data with an NEC file applied, and read data

    >>> import nrgpy
    >>>
    >>> client_id = "go to https://cloud.nrgsystems.com for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com for access"
    >>> save_dir = '/path/to/exported/data'
    >>>
    >>> exporter = nrgpy.CloudExport(
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

    Download 15 days of data files from ZX 300 site

    >>> import nrgpy
    >>>
    >>> client_id = "go to https://cloud.nrgsystems.com for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com for access"
    >>> save_dir = '/path/to/exported/data'
    >>> file_format = 'zx'
    >>>
    >>> exporter = nrgpy.CloudExport(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=save_dir,
            file_format='zx',
            site_id=57,
            start_date="2022-05-01",
            end_date="2022-05-15",
        )
    >>> exporter.export()
    """

    def __init__(
        self,
        site_id: int = 0,
        site_number: Union[int, str] = 0,
        out_dir: str = "",
        logger_sn: Union[int, str] = "",
        start_date: str = "2014-01-01",
        end_date: str = "2030-12-31",
        file_format: str = "singleFile",
        client_id: str = "",
        client_secret: str = "",
        url_base: str = cloud_url_base,
        nec_file: str = "",
        export_type: str = "measurements",
        interval: str = "",
        concatenate: bool = True,
        unzip: bool = True,
        **kwargs,
    ):
        """Initialize a cloud_export object.

        Parameters
        ----------
        out_dir : str (path-like)
            path to save exported data
        site_id : int
            NRG Cloud site identifier (NOT the site number)
            must pass site_id OR [site_number and/or logger_sn]
        site_number : int
            site number
            must pass site_id OR [site_number and/or logger_sn]
        logger_sn : int
            serial number of data logger (like, 820612345)
            must pass site_id OR [site_number and/or logger_sn]
        start_date : str ('YYYY-MM-DD HH:MM:SS'), default'2014-01-01'
            start date/time of data export
            if just date, it will return the whole day
            times are in logger local time
        end_date : str ('YYYY-MM-DD HH:MM:SS'), default '2030-12-31'
            start date/time of data export
            if just date, it will return the whole day
            times are in logger local time
        file_format : {'singleFile', 'multipleFiles'},
            whether tab-delimited text or binary output; use 'multipleFiles' for RLD
        client_id : str
            available in the NRG Cloud portal
        client_secret : str
            available in the NRG Cloud portal
        nec_file : str, optional
            path to NEC file for custom export formatting
        export_type : {'measurements', 'diagnostic', 'events', 'communication'},
            default 'measurements';  which type of data to export
        interval : {'oneMinute', 'twoMinute', 'fiveMinute', 'tenMinute',
            'fifteenMinute', 'thirtyMinute', 'Hour', 'Day'}, optional
            averaging interval of exported data; must be a multiple of the logger's
            statistical interval
        concatenate : bool
            [DEPRECATED] (True) set to False to return original CSV files in export
        unzip : bool, default True
            whether to extract the .txt data file from the .zip file
        """

        super().__init__(client_id, client_secret, url_base)

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
        self.concatenate = concatenate
        self.unzip = unzip

        if self.nec_file:
            self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
            self.encoded_nec_string = self.encoded_nec_bytes.decode("utf-8")
        else:
            self.encoded_nec_bytes = ""
            self.encoded_nec_string = ""

    def export(self) -> Union[None, bool]:
        """Export data using the NRG Cloud API."""

        self.prepare_post_data()

        self.request_time = datetime.now()
        self.resp = requests.post(
            json=self.data, url=self.export_url, headers=self.headers
        )
        self.request_duration = datetime.now() - self.request_time

        if self.resp.status_code == 200:
            with open(self.filepath, "wb") as f:
                f.write(self.resp.content)

            self.process_zip()

            log.info(f"export created for site_id {self.site_id}")
            log.info(
                f"export took {self.request_duration} for {os.path.getsize(self.export_filepath)} bytes"  # noqa E501
            )

        else:
            log.error("export not created")
            log.debug(f"{self.resp.status_code} | {self.resp.reason}")
            try:
                log.debug(self.resp.text.split(":")[1].split('"')[1])
            except Exception:
                pass
            print(str(self.resp.status_code) + " | " + self.resp.reason)
            print(self.resp.text.split(":")[1].split('"')[1])
            return False

    def prepare_post_data(self) -> None:
        self.data = {
            "siteid": self.site_id,
            "fromdate": self.start_date,
            "todate": self.end_date,
            "fileFormat": self.file_format,
            "necFileBytes": self.encoded_nec_string,
            "exportType": self.export_type,
        }

        self.format_data_for_api_versions()

        if self.interval:
            self.data["interval"] = self.interval

    def format_data_for_api_versions(self) -> None:
        if self.data["fileFormat"] == "rld":
            self.data["fileFormat"] = "multipleFiles"
        if self.data["fileFormat"] == "txt":
            self.data["fileFormat"] = "singleFile"

    def process_zip(self) -> None:
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


CloudExport = CloudExport

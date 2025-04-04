from datetime import datetime
import json
from nrgpy.common.log import log
from nrgpy.cloud_api.auth import CloudApi, cloud_url_base, is_authorized
from nrgpy.utils.utilities import string_date_check, draw_progress_bar
import os
import requests


class CloudImport(CloudApi):
    """Uses NRG hosted web-based API to import RLD and CSV/CSV.zip files to
    existing sites in NRG Cloud.
    To sign up for the service, go to https://cloud.nrgsystems.com/.

    Note that the site must exist in the NRG Cloud platform, and you must have
    Contributor or Administrator level access to the site to use these features.

    Attributes
    ----------
    in_dir : str (path-like)
        path to data file directory
    filename : str
        provide for single file import
    site_filter : str, optional
        text filter for limiting file set
    filter2 : str, optional
        another text filter...
    start_date : str, optional
        text start date to filter on "YYYY-mm-dd"
    end_date : str, optional
        text end date to filter on "YYYY-mm-dd"
    client_id : str
        provided by NRG Systems
    client_secret : str
        provided by NRG Systems
    session_token : str
    headers : str
        headers passed in API call
    data : str
        data passed in API call
    resp : str
        API response
    job_ids : dict
        dictionary of filenames and job ids

    Examples
    --------
    Import a single raw data file with NRG Import API

    >>> import nrgpy
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.filename
    >>> client_id = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> importer = nrgpy.CloudImport(
            filename=filename,
            client_id=client_id,
            client_secret=client_secret,
        )

    Import a folder of data files with NRG Import API

    >>> import nrgpy
    >>> file_filter = "000175"
    >>> in_directory = "filenames"
    >>> client_id = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> importer = nrgpy.CloudImport(
            file_filter=file_filter,
            in_dir=in_directory,
            client_id=client_id,
            client_secret=client_secret,
            start_date="2020-01-01",
            end_date="2020-01-31",
        )
    >>> importer.process()

    """

    def __init__(
        self,
        in_dir: str = "",
        filename: str = "",
        site_filter: str = "",
        filter2: str = "",
        start_date: str = "1970-01-01",
        end_date: str = "2150-12-31",
        client_id: str = "",
        client_secret: str = "",
        url_base: str = cloud_url_base,
        progress_bar: bool = True,
        **kwargs,
    ):
        """Initialize a cloud_export object.

        Parameters
        ----------
        in_dir : str (path-like)
            path to data file directory
        filename : str
            provide for single file import
        site_filter : str, optional
            text filter for limiting file set
        filter2 : str, optional
            another text filter...
        start_date : str, optional
            text start date to filter on "YYYY-mm-dd"
        end_date : str, optional
            text end date to filter on "YYYY-mm-dd"
        client_id : str
            available in the NRG Cloud portal
        client_secret : str
            available in the NRG Cloud portal
        progress_bar : bool, default True
            whether to display the progress bar
        """

        super().__init__(client_id, client_secret, url_base)

        self.site_filter = site_filter

        if "file_filter" in kwargs and site_filter == "":
            self.file_filter = kwargs.get("file_filter")
            self.site_filter = self.file_filter

        self.filter2 = filter2
        self.in_dir = in_dir
        self.start_date = start_date
        self.end_date = end_date
        self.progress_bar = progress_bar
        self.job_ids = {}

        if filename:
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar = False
            self.start_time = datetime.now()
            self.single_file(filename)

        if in_dir:
            self.process()

    def process(self):
        self.start_time = datetime.now()
        self.files = self.get_valid_files_from_in_dir()

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1

        if len(self.files) == 0:
            log.debug(f"no files to process in {self.in_dir}")
            raise FileNotFoundError(f"no files to process in {self.in_dir}")

        for filename in self.files:
            try:
                self.single_file(os.path.join(self.in_dir, filename))
                self.counter += 1
                if not is_authorized(self.resp):
                    break
            except Exception:
                pass

    def get_valid_files_from_in_dir(self) -> list:
        return [
            f
            for f in sorted(os.listdir(self.in_dir))
            if self.site_filter in f
            and self.filter2 in f
            and f.lower().endswith(
                tuple(["rld", "csv", "csv.zip", "diag", "statistical.dat"])
            )
            and string_date_check(self.start_date, self.end_date, f)
        ]

    def single_file(self, filename: str = ""):
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print(
                    "Processing {0}/{1} ... {2} ... ".format(
                        str(self.counter).rjust(self.pad),
                        str(self.raw_count).ljust(self.pad),
                        os.path.basename(filename),
                    ),
                    end="",
                    flush=True,
                )

            self.encoded_filename_bytes = self.prepare_file_bytes(filename)
            self.encoded_filename_string = self.encoded_filename_bytes.decode("utf-8")

            self.maintain_session_token()

            self.data = {
                "FileBytes64BitEncoded": self.encoded_filename_string,
                "FileName": os.path.basename(filename),
            }

            self.resp = requests.post(
                json=self.data, url=self.import_url, headers=self.headers
            )

            if self.resp.status_code == 200:
                if self.progress_bar is False:
                    print("[DONE]")

                self.job_ids[os.path.basename(filename)] = json.loads(self.resp.text)[
                    "jobId"
                ]
                log.info(f"imported {os.path.basename(filename)} OK")
                log.debug(f"{self.resp.status_code} {self.resp.text}")

            elif self.resp.status_code == 401 or self.resp.status_code == 400:
                if (
                    "has already been imported"
                    in json.loads(self.resp.text)["apiResponseMessage"]
                ):
                    log.info(self.resp.text)
                    if self.progress_bar is False:
                        print("[ALREADY IMPORTED]")
                else:
                    log.info(f"{os.path.basename(filename)}: {self.resp.text} ")
                    if self.progress_bar is False:
                        print("[PASSED]")
                pass

            else:
                log.error(f"unable to import {os.path.basename(filename)}: FAILED")
                print(f"\nunable to process file: {filename}")
                print(f"{str(self.resp.status_code)} | {self.resp.reason}")
                print(self.resp.text.split(":")[1].split('"')[1])

        except Exception as e:
            if self.progress_bar is False:
                print("[FAILED]")

            log.error(f"unable to import {os.path.basename(filename)}: FAILED")
            log.debug(e)
            print(f"unable to process file: {filename}")


cloud_import = CloudImport

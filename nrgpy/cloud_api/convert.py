from nrgpy.common.log import log
from datetime import datetime
from nrgpy.utils.utilities import affirm_directory, string_date_check, draw_progress_bar
from .auth import CloudApi, cloud_url_base, is_authorized
import os
import requests
import zipfile


class CloudConvert(CloudApi):
    """Uses NRG hosted web-based API to convert RLD and RWD files to text format
    To sign up for the service, go to https://cloud.nrgsystems.com/.

    Note that the site must exist in the NRG Cloud platform, and you must have
    Contributor or Administrator level access to the site to use these features.

    Attributes
    ----------
    rld_dir : str (path-like)
        path to rld file directory
    out_dir : str (path-like)
        path to save text export files
    filename : str
        provide for single file conversion
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
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : str
        [measurements], diagnostic, events, communication
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
    Convert a single raw data file to Text with NRG Convert API

    >>> import nrgpy
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
    >>> client_id = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> converter = nrgpy.CloudConvert(
            file_filter=file_filter,
            filename=filename,
            client_id=client_id,
            client_secret=client_secret,
        )

    Convert a folder of raw data files to Text with NRG Convert API

    >>> import nrgpy
    >>> file_filter = "000175"
    >>> rld_directory = "rlds"
    >>> txt_dir = "/home/user/data/sympro/000123/txt/"
    >>> client_id = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> converter = nrgpy.CloudConvert(
            file_filter=file_filter,
            rld_dir=rld_directory,
            out_dir=txt_dir,
            client_id=client_id,
            client_secret=client_secret,
            start_date="2020-01-01",
            end_date="2020-01-31",
        )
    >>> converter.process()

    """

    def __init__(
        self,
        rld_dir: str = "",
        out_dir: str = "",
        filename: str = "",
        site_filter: str = "",
        filter2: str = "",
        start_date: str = "1970-01-01",
        end_date: str = "2150-12-31",
        client_id: str = "",
        client_secret: str = "",
        url_base: str = cloud_url_base,
        export_type: str = "measurements",
        nec_file: str = "",
        unzip: bool = True,
        progress_bar: bool = True,
        **kwargs,
    ):
        """Initialize a cloud_export object.

        Parameters
        ----------
        rld_dir : str (path-like)
            path to rld file directory
        out_dir : str (path-like)
            path to save text export files
        filename : str
            provide for single file conversion
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
        nec_file : str, optional
            path to NEC file for custom export formatting
        export_type : {'measurements', 'diagnostic', 'events', 'communication'}, default 'measurements'
            which type of data to export
        unzip : bool, default True
            whether to extract the .txt data file from the .zip file
        progress_bar : bool, default True
            whether to dispaly the progress bar
        """

        super().__init__(client_id, client_secret, url_base)

        self.export_type = export_type
        self.site_filter = site_filter

        if "file_filter" in kwargs and site_filter == "":
            self.file_filter = kwargs.get("file_filter")
            self.site_filter = self.file_filter

        self.filter2 = filter2
        self.start_date = start_date
        self.end_date = end_date
        self.nec_file = nec_file
        self.out_dir = out_dir
        self.rld_dir = rld_dir
        self.progress_bar = progress_bar
        self.unzip = unzip

        affirm_directory(self.out_dir)

        if filename:
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar = False
            self.start_time = datetime.now()
            self.single_file(filename)

        if rld_dir:
            self.process()

    def process(self) -> None:
        self.start_time = datetime.now()

        self.files = [
            f
            for f in sorted(os.listdir(self.rld_dir))
            if self.site_filter in f and self.filter2 in f and f.lower().endswith("rld")
            # and f.lower().endswith(('rwd', 'rld'))    ## Uncomment when RWD convert is supported
            and string_date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1

        for rld in self.files:
            self.single_file(os.path.join(self.rld_dir, rld))
            self.counter += 1
            if not is_authorized(self.resp):
                break

        print("\n")

    def single_file(self, rld) -> None:
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print(
                    "Processing {0}/{1} ... {2} ... ".format(
                        str(self.counter).rjust(self.pad),
                        str(self.raw_count).ljust(self.pad),
                        os.path.basename(rld),
                    ),
                    end="",
                    flush=True,
                )

            self.encoded_rld_bytes = self.prepare_file_bytes(rld)
            self.encoded_rld_string = self.encoded_rld_bytes.decode("utf-8")

            if self.nec_file:
                self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
                self.encoded_nec_string = self.encoded_nec_bytes.decode("utf-8")
            else:
                self.encoded_nec_bytes = ""
                self.encoded_nec_string = ""

            self.maintain_session_token()

            self.data = {
                "FileBytes64BitEncoded": self.encoded_rld_string,
                "NecFile64BitEncoded": self.encoded_nec_string,
                "exportType": self.export_type,  # measurements (default) | samples
            }

            self.resp = requests.post(
                json=self.data, url=self.convert_url, headers=self.headers
            )

            self.zip_file = os.path.basename(rld)[:-3] + "zip"
            self.filepath = os.path.join(self.out_dir, self.zip_file)

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

                if self.progress_bar is False:
                    print("[DONE]")

                log.info(f"converted {os.path.basename(self.export_filepath)} OK")

            elif self.resp.status_code == 401:
                pass

            else:
                log.error(
                    f"unable to convert {os.path.basename(self.export_filepath)}: FAILED"
                )
                print("\nunable to process file: {0}".format(rld))
                print(str(self.resp.status_code) + " | " + self.resp.reason)
                print(self.resp.text.split(":")[1].split('"')[1])

        except Exception as e:
            if self.progress_bar is False:
                print("[FAILED]")

            log.exception(
                f"unable to convert {os.path.basename(self.export_filepath)}: FAILED"
            )
            print("unable to process file: {0}".format(rld))
            print(e)
            pass


cloud_convert = CloudConvert

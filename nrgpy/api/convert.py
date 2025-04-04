from nrgpy.common.log import log
from datetime import datetime
import io
from nrgpy.utils.utilities import affirm_directory, string_date_check, draw_progress_bar
from .auth import nrg_api, convert_url
import os
import requests
import zipfile


class nrg_api_convert(nrg_api):
    """Uses NRG hosted web-based API to convert RLD and RWD files to text format
    To sign up for the service, go to https://services.nrgsystems.com/

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
        provided by NRG Systems
    client_secret : str
        provided by NRG Systems
    token : str
        deprecated, for beta conversion service users
    encryption_pass : str, optional
        password for rld files (set in logger)
    header_type : str
        [standard], columnonly, or none
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : str
        [meas], samples, diag, comm

    Examples
    --------
    Convert a single raw data file to Text with NRG Convert API

    >>> import nrgpy
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrgpy.nrg_api_convert(
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
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrgpy.nrg_api_convert(
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
        rld_dir="",
        out_dir="",
        filename="",
        site_filter="",
        filter2="",
        start_date="1970-01-01",
        end_date="2150-12-31",
        client_id="",
        client_secret="",
        encryption_pass="",
        header_type="standard",
        nec_file="",
        export_type="meas",
        export_format="csv_zipped",
        progress_bar=True,
        **kwargs,
    ):

        super().__init__(client_id, client_secret)

        self.encryption_pass = encryption_pass
        self.export_format = export_format
        self.export_type = export_type
        self.site_filter = site_filter

        if "file_filter" in kwargs and site_filter == "":
            self.file_filter = kwargs.get("file_filter")
            self.site_filter = self.file_filter

        self.filter2 = filter2
        self.start_date = start_date
        self.end_date = end_date
        self.header_type = header_type
        self.nec_file = nec_file
        self.out_dir = out_dir
        self.rld_dir = rld_dir
        self.progress_bar = progress_bar

        affirm_directory(self.out_dir)

        if filename:
            self.filename = filename
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar = False
            self.start_time = datetime.now()
            self.single_file(filename)

        if rld_dir:
            self.process()

    def process(self):
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

        print("\n")

    def single_file(self, rld):
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

            if self.nec_file:
                self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
            else:
                self.encoded_nec_bytes = ""

            if not self.token_valid():
                (
                    self.session_token,
                    self.session_start_time,
                ) = self.request_session_token()

            headers = {"Authorization": "Bearer {}".format(self.session_token)}

            self.data = {
                "type": rld[-3:].upper(),
                "filebytes": self.encoded_rld_bytes,
                "necfilebytes": self.encoded_nec_bytes,
                "headertype": self.header_type,  # standard | columnonly  | none
                "exporttype": self.export_type,  # measurements (default) | samples
                "exportformat": self.export_format,  # csv_zipped (default)   | parquet
                "encryptionkey": self.encryption_pass,
                "columnheaderformat": "",  # not implemented yet
            }

            self.resp = requests.post(data=self.data, url=convert_url, headers=headers)

            zipped_data_file = zipfile.ZipFile(io.BytesIO(self.resp.content))
            name = zipped_data_file.infolist().pop()
            out_filename = os.path.basename(rld)[:-3] + "txt"

            with open(os.path.join(self.out_dir, out_filename), "wb") as outputfile:
                outputfile.write(zipped_data_file.read(name))

            try:
                filename = os.path.join(self.out_dir, out_filename)
                file_contents = open(filename, "r").read()
                f = open(filename, "w", newline="\r\n")
                f.write(file_contents)
                f.close()

            except Exception:
                print(
                    "Could not convert Windows newline characters properly; file may be unstable"
                )

            log.info(f"converted {os.path.basename(out_filename)} OK")

            if self.progress_bar is False:
                print("[DONE]")

        except Exception as e:
            if self.progress_bar is False:
                print("[FAILED]")

            log.exception(f"unable to convert {os.path.basename(self.filename)}")
            print("unable to process file: {0}".format(rld))
            print(e)
            print(str(self.resp.status_code) + " " + self.resp.reason + "\n")

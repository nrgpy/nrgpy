from datetime import datetime
import io
from nrgpy.utils.utilities import affirm_directory, date_check, draw_progress_bar
from .auth import cloud_api, convert_url
import os
import requests
import zipfile


class cloud_convert(cloud_api):
    """Uses NRG hosted web-based API to convert RLD and RWD files to text format
    To sign up for the service, go to https://cloud.nrgsystems.com/. 
    
    Note that the site must exist in the NRG Cloud platform, and you must have 
    Contributor or Administrator level access to the site to use these features.

    Parameters
    ----------
    rld_dir : str
        path to rld file directory
    out_dir : str
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

    Examples
    --------
    Convert a single raw data file to Text with NRG Convert API

    >>> import nrgpy
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
    >>> client_id = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> client_secret = "go to https://cloud.nrgsystems.com/data-manager/api-setup for access"
    >>> converter = nrgpy.cloud_convert(
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
    >>> converter = nrgpy.cloud_convert(
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
    def __init__(self, rld_dir='', out_dir='', filename='',
                 site_filter='', filter2='',
                 start_date='1970-01-01', end_date='2150-12-31',
                 client_id='', client_secret='',
                 export_type='measurements', nec_file='', unzip=True,
                 progress_bar=True, **kwargs):

        super().__init__(client_id, client_secret)

        self.export_type = export_type
        self.site_filter = site_filter

        if 'file_filter' in kwargs and site_filter == '':
            self.file_filter = kwargs.get('file_filter')
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

    def process(self):
        self.start_time = datetime.now()

        self.files = [
            f for f in sorted(os.listdir(self.rld_dir))
            if self.site_filter in f and self.filter2 in f
            and f.lower().endswith('rld')
            # and f.lower().endswith(('rwd', 'rld'))    ## Uncomment when RWD convert is supported
            and date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1

        for rld in self.files:
            self.single_file(os.path.join(self.rld_dir, rld))
            self.counter += 1
            if self.resp.status_code == 401:
                print("\nAccess to site at Coordinator or Administrator level is required for data functions")
                break

        print('\n')

    def single_file(self, rld):
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print("Processing {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad), str(self.raw_count).ljust(self.pad), os.path.basename(rld)), end="", flush=True)

            self.encoded_rld_bytes = self.prepare_file_bytes(rld)
            self.encoded_rld_string = self.encoded_rld_bytes.decode('utf-8')

            if self.nec_file:
                self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
                self.encoded_nec_string = self.encoded_nec_bytes.decode('utf-8')
            else:
                self.encoded_nec_bytes = ''
                self.encoded_nec_string = ''

            if not self.token_valid():
                self.session_token, self.session_start_time = self.request_session_token()

            headers = {"Authorization": "Bearer {}".format(self.session_token)}

            self.data = {
                        'FileBytes64BitEncoded': self.encoded_rld_string,
                        'NecFile64BitEncoded': self.encoded_nec_string,
                        'exportType': self.export_type,      # measurements (default) | samples
                    }

            self.resp = requests.post(json=self.data, url=convert_url, headers=headers)

            self.zip_file = os.path.basename(rld)[:-3] + 'zip'
            self.filepath = os.path.join(self.out_dir, self.zip_file)

            if self.resp.status_code == 200:
                with open(self.filepath, 'wb') as f:
                    f.write(self.resp.content)

                if self.unzip:
                    with zipfile.ZipFile(self.filepath, 'r') as z:
                        self.export_filename = z.namelist()[0]
                        z.extractall(self.out_dir)
                    os.remove(self.filepath)
                    self.export_filepath = os.path.normpath(
                        os.path.join(self.out_dir, self.export_filename))
                
                else:
                    self.export_filepath = os.path.normpath(self.filepath)
                    self.export_filename = self.zip_file
                
                if self.progress_bar is False:
                    print("[DONE]")
            
            elif self.resp.status_code == 401:
                pass

            else:
                print('\nunable to process file: {0}'.format(rld))
                print(str(self.resp.status_code) + ' | ' + self.resp.reason)
                print(self.resp.text.split(':')[1].split('"')[1])    
           

        except Exception as e:
            if self.progress_bar is False:
                print("[FAILED]")

            print('unable to process file: {0}'.format(rld))
            print(e)
            pass

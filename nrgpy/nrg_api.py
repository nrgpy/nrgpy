import base64
from datetime import datetime, timedelta
import glob
import io
import json
from nrgpy.utilities import affirm_directory, date_check, draw_progress_bar
import os
import pickle
import requests
import traceback
import zipfile

# 2020 convert service
request_token_url = 'https://dataservicesconvert.azurewebsites.net/api/ConvertToken?code=WUO2Dkq5He5Zp9XHddTGuQuNkoF09YWceIVphPhxIFn7hLGH6fvKSA=='
convert_service_url = 'https://dataservicesconvert.azurewebsites.net/api/Convert?code=rWNCyVxJAtaaMD/cr5otcCiQs8pVUuVlikEG684eibKcBhK/hLju6g=='
token_file = '.nrgpy_token'


class nrg_api(object):
    """
    Parent class for NRG API functionality
    """

    def __init__(self, client_id='', client_secret=''):
        self.client_id = client_id
        self.client_secret = client_secret
        
        if self.client_id and self.client_secret:
            self.maintain_session_token()
        else:
            print('[Access error] Valid credentials are required.\nPlease contact support@nrgsystems.com or visit \nhttps://services.nrgsystems.com for API access')
        
    
    def request_session_token(self):
        """generates a new session token for convert service api

        requires an active account with NRG Systems. to sign
        up for an account, go to:
        https://services.nrgsystems.com

        Parameters
        ----------
        client_id : str
            obtained from NRG Systems
        client_secret : str

        Returns
        -------
        session_token : str
            valid for 24 hour
        session_start_time : datetime
            start time of 24 hour countdown
        """
        print("{} | Requesting session token ... ".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), end="", flush=True)

        request_token_header = { 'content-type' : 'application/json' }
        request_payload = { 'client_id' : '{}'.format(self.client_id), 'client_secret' : '{}'.format(self.client_secret)}

        resp = requests.post(data=json.dumps(request_payload), headers=request_token_header, url=request_token_url)
        self.session_start_time = datetime.now()

        if resp.status_code == 200:
            print("[OK]")
            self.session_token = json.loads(resp.text)['access_token']
        else:
            print("[FAILED] | unable to get session token.")
            self.session_token = False


    def token_valid(self):
        """check if token is still valid

        Parameters
        ----------
        session_start_time : datetime
            generated at time of token request

        Returns
        -------
        status : bool
            true if still valid, false if expired
        """
        if datetime.now() < self.session_start_time + timedelta(hours=18):
            return True
        return False


    def save_token(self, filename=token_file):
        """save session token in token pickle file"""
        with open(filename, 'wb') as f:
            pickle.dump([self.session_token, self.session_start_time], f)


    def load_token(self, filename=token_file):
        """read session token from pickle file"""
        with open(filename, 'rb') as f:
            self.session_token, self.session_start_time = pickle.load(f)


    def maintain_session_token(self, filename=token_file):
        """maintain a current/valid session token for data service api"""
        try:
            self.load_token(filename=token_file)
            if not self.token_valid():
                self.request_session_token()
                self.save_token()
        except:
            self.request_session_token()
            self.save_token()
    
    
    def prepare_file_bytes(self, filename=''):
        file_bytes = base64.encodebytes(open(filename, 'rb').read())
        return file_bytes

class nrg_api_upload(nrg_api):

    def __init__(self, client_id='', client_secret='', filename='', rld_dir='', site_filter='', site_filter2='', 
                start_date='1970-01-01', end_date='2150-12-31'):
        
        super().__init__(client_id, client_secret)
        
        self.filename = filename
        self.rld_dir = rld_dir
        self.site_filter = site_filter
        self.site_filter2 = site_filter2
        self.start_date = start_date
        self.end_date = end_date
        self.headers = {"Authorization": "Bearer {}".format(self.session_token)}
        self.upload_url = "https://dataservicesconvert.azurewebsites.net/api/Upload?code=CFl2iIboQvHv7O4kftiUTIaqAaPyjl8k1XR4i6PfPraofqOgBWac9Q=="
 
        if filename:
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar=False
            self.start_time = datetime.now()
            self.upload_file(filename)
        
        if rld_dir:
            self.upload_directory()
    
    def upload_file(self):
        if self.progress_bar:
            draw_progress_bar(self.counter, self.raw_count, self.start_time)
        else:
            print("Processing {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad),str(self.raw_count).ljust(self.pad),os.path.basename(rld)), end="", flush=True)
                
        self.encoded_rld_bytes = self.prepare_file_bytes(self.filename)
        
        data = {
            'filebytes': self.encoded_rld_bytes
        }

        self.response = requests.request("POST", self.upload_url, headers=self.headers, data=data)

    
    def upload_directory(self, progress_bar=True):
        self.progress_bar = progress_bar
        self.start_time = datetime.now()
        
        self.files = [
            f for f in sorted(glob.glob(self.rld_dir + '*.rld'))\
            if self.site_filter in f and self.site_filter2 in f\
            and date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        
        for rld in self.files:
            self.filename = rld
            self.upload_file()
            self.counter += 1


class nrg_api_convert(nrg_api):
    """Uses NRG hosted web-based API to convert RLD files text format
    To sign up for the service, go to https://services.nrgsystems.com/
    
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
    Convert a single RLD file to Text with NRG Convert API
    >>> from nrgpy.convert_rld import nrg_convert_api
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
    >>> txt_dir = "/home/user/data/sympro/000123/txt/"
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrg_convert_api(
            file_filter=file_filter, 
            filename=filename, 
            client_id=client_id,
            client_secret=client_secret,
        ) 
    Convert a folder of RLD files to Text with NRG Convert API
    >>> from nrgpy.convert_rld import nrg_convert_api
    >>> file_filter = "000175"
    >>> rld_directory = "rlds"
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrg_convert_api(
            file_filter=file_filter, 
            rld_dir=rld_directory, 
            client_id=client_id,
            client_secret=client_secret,
            start_date="2020-01-01",
            end_date="2020-01-31",
        )
    >>> converter.process()    
    
    """
    def __init__(self, rld_dir='', out_dir='', filename='', 
                 site_filter='', filter2 = '', 
                 start_date='1970-01-01', end_date='2150-12-31',
                 client_id='', client_secret='', 
                 encryption_pass='', header_type='standard', nec_file='',
                 export_type='meas', export_format='csv_zipped',
                 progress_bar=True, **kwargs): 
        
        super().__init__(client_id, client_secret)
        
        self.encryption_pass = encryption_pass
        self.export_format = export_format
        self.export_type = export_type
        self.site_filter = site_filter
        
        if 'file_filter' in kwargs and site_filter == '':
            self.file_filter = kwargs.get('file_filter')
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
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar=False
            self.start_time = datetime.now()
            self.single_file(filename)
        
        if rld_dir:
            self.process()


    def process(self):
        self.start_time = datetime.now()
        
        self.files = [
            f for f in sorted(glob.glob(self.rld_dir + '*.rld'))\
            if self.site_filter in f and self.filter2 in f\
            and date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        
        for rld in self.files:
            self.single_file(rld)
            self.counter += 1

        print('\n')


    def single_file(self, rld):
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print("Processing {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad),str(self.raw_count).ljust(self.pad),os.path.basename(rld)), end="", flush=True)
        
            self.encoded_rld_bytes = self.prepare_file_bytes(rld)

            if self.nec_file:
                self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
            else:
                self.encoded_nec_bytes = ''

            if not self.token_valid(): self.session_token, self.session_start_time = self.request_session_token()
            
            headers = {"Authorization": "Bearer {}".format(self.session_token)}

            self.data = {
                        'filebytes': self.encoded_rld_bytes,
                        'necfilebytes': self.encoded_nec_bytes,
                        'headertype': self.header_type,     # standard | columnonly  | none
                        'exporttype': self.export_type,     # measurements (default) | samples
                        'exportformat': self.export_format, # csv_zipped (default)   | parquet
                        'encryptionkey': self.encryption_pass,
                        'columnheaderformat': '',           # not implemented yet
                    }             
            self.resp=requests.post(data=self.data, url=convert_service_url, headers=headers)


            zipped_data_file = zipfile.ZipFile(io.BytesIO(self.resp.content))
            reg_data_file = self.resp.content
            name = zipped_data_file.infolist().pop()
            out_filename =  os.path.basename(rld).split('.rld')[0] + '.txt'

            with open(os.path.join(self.out_dir, out_filename),'wb') as outputfile:
                outputfile.write(zipped_data_file.read(name))

            try:
                filename = os.path.join(self.out_dir, out_filename)
                file_contents = open(filename,"r").read()
                f = open(filename,"w", newline="\r\n")
                f.write(file_contents)
                f.close()
            except:
                print("Could not convert Windows newline characters properly; file may be unstable")

            if self.progress_bar == False: print("[DONE]")

        except Exception as e:
            if self.progress_bar == False: print("[FAILED]")
            print('unable to process file: {0}'.format(rld))
            print(e)
            print(str(self.resp.status_code) + " " + self.resp.reason + "\n")
            pass

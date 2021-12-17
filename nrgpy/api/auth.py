try:
    from nrgpy import logger
except ImportError:
    pass
import base64
from datetime import datetime, timedelta
import json
import pickle
import requests


retrieve_token_url = 'https://api.nrgsystems.com/api/RetrieveToken?code=y2/bWG4hRNf1E00lWICOp7nqLvpNPOtaiFf9Wq2bi1iUpdyQdjwicQ=='

data_catalog_url = 'https://api.nrgsystems.com/api/DataCatalog'
convert_url = 'https://api.nrgsystems.com/api/Convert?code=Z6czLero6fQthaM9TZ2DavSN9i7sIeESG/xxGr88JYYoIwypjL/7Uw=='
export_url = 'https://api.nrgsystems.com/api/Export?code=2ZGPXDO8dmHF5IZdm3Qaqrlkf9Gs8930oFeN/MCwX8vcnazvCDkRdg=='
upload_url = "https://api.nrgsystems.com/api/Upload?code=YSy3yEeC6aYMNG9setSKvWe9tZAJJYQtXam1tGT7ADg9FTTCaNqFCw=="

token_file = '.nrgpy_token'


class nrg_api(object):
    """
    Parent class for NRG API functionality
    """

    def __init__(self, client_id='', client_secret=''):
        logger.debug(f"nrg legacy api init ")
        self.client_id = client_id
        self.client_secret = client_secret

        if self.client_id and self.client_secret:
            self.maintain_session_token()
        else:
            print('[Access error] Valid credentials are required.\nPlease contact support@nrgsystems.com or visit \nhttps://services.nrgsystems.com for API access')
            logger.error('[Access error] Valid credentials are required. Please  API credentials')

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
        logger.debug("session token requested")
        print("{} | Requesting session token ... ".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), end="", flush=True)

        request_token_header = {'content-type': 'application/json'}
        request_payload = {'client_id': '{}'.format(self.client_id), 'client_secret': '{}'.format(self.client_secret)}

        self.resp = requests.post(data=json.dumps(request_payload), headers=request_token_header, url=retrieve_token_url)
        self.session_start_time = datetime.now()

        if self.resp.status_code == 200:
            logger.error("unable to get session token")
            logger.debug(f"{self.resp.text}")
            print("[OK]")
            logger.info("new session token OK")
            self.session_token = json.loads(self.resp.text)['access_token']
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
            if self.session_token is not False:
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

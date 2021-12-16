try:
    from nrgpy import logger
except ImportError:
    pass
from nrgpy import token_file
import base64
from datetime import datetime, timedelta
import json
import pickle
import requests

url_base = 'https://cloud-api.nrgsystems.com/nrgcloudcustomerapi/'

token_url = url_base + 'token'
convert_url = url_base + 'data/convert'
export_url = url_base + 'data/export'
sites_url = url_base + "sites"



class cloud_api(object):
    """
    Parent class for NRG Cloud API functionality
    """

    def __init__(self, client_id='', client_secret=''):
        logger.debug(f"cloud base: {url_base}")
        self.client_id = client_id
        self.client_secret = client_secret

        if self.client_id and self.client_secret:
            self.maintain_session_token()
        else:
            print('[Access error] Valid credentials are required.\n\nPlease visit https://cloud.nrgsystems.com/data-manager/api-setup\nto access your API credentials')
            logger.error('[Access error] Valid credentials are required. Please visit https://cloud.nrgsystems.com/data-manager/api-setup to access your API credentials')

    def request_session_token(self):
        """generates a new session token for convert service api

        requires an active account with NRG Systems. to sign
        up for an account, go to:
        https://cloud.nrgsystems.com

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
        request_payload = {'clientId': '{}'.format(self.client_id), 'clientSecret': '{}'.format(self.client_secret)}

        self.resp = requests.post(data=json.dumps(request_payload), headers=request_token_header, url=token_url)
        self.session_start_time = datetime.now()

        if self.resp.status_code == 200:
            print("[OK]")
            logger.info("new session token OK")
            self.session_token = json.loads(self.resp.text)['apiToken']
        else:
            logger.error("unable to get session token")
            logger.debug(f"{self.resp.text}")
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
        if datetime.now() < self.session_start_time + timedelta(hours=22):
            if self.session_token is not False:
                # logger.debug(f"session token reused: expires {self.session_start_time + timedelta(hours=24)}")
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

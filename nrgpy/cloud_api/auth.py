try:
    from nrgpy import logger
except ImportError:
    pass
import base64
from datetime import datetime, timedelta
import importlib
from importlib.metadata import version
import json
from nrgpy import token_file
from packaging.version import parse as parse_version
import pickle
import re
import requests
import sys
import traceback

cloud_url_base = "https://cloud-api.nrgsystems.com/nrgcloudcustomerapi/"
token_url = "token"
convert_url = "data/convert"
export_url = "data/export"
create_export_job_url = "data/createexportjob"
export_job_url = "data/exportjob"
import_url = "data/import"
sites_url = "sites"


class CloudApi(object):
    """
    Parent class for NRG Cloud API functionality

    nrgpy simplifies usage of the NRG Cloud APIs. See the documentation for the
    cloud_api.sites, .export, and .convert modules for more information.

    For non-nrgpy implementations, the following Usage information may be
    helpful.

    The base url for the NRG Cloud APIs is

    https://cloud-api.nrgsystems.com/nrgcloudcustomerapi/

    Use client ID and secret to obtain a bearer token at the /token endpoint.
    This token is good for 24 hours.

    You will be limited to creating 10 tokens per day, though normally one
    token should suffice, so please cache. nrgpy's cloud_api modules will
    automatically manage bearer tokens, refreshing only when necessary.

    Endpoints:

    base
        https://cloud-api.nrgsystems.com/nrgcloudcustomerapi/
    /token
        for accessing bearer token. Client ID and Secret required.
    /sites
        Get list of sites. Bearer token required
    /convert
        Convert RLD file to TXT. Bearer token required
    /export
        Export TXT or RLD files for a given date range. NEC files may be used
        to format TXT outputs. Bearer  token required.
    """

    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        url_base: str = cloud_url_base,
    ):
        logger.debug(f"cloud base: {url_base}")
        self.client_id = client_id
        self.client_secret = client_secret
        try:
            self.user_agent = f"nrgpy-{version('nrgpy')}"
        except importlib.metadata.PackageNotFoundError:
            self.user_agent = "nrgpy"
        self.python_version = re.split(r"[ \n\t]", sys.version)[0]
        self.token_file_name = token_file + "_" + self.client_id[:10]
        self.url_base = url_base
        self.token_url = url_base + token_url
        self.convert_url = url_base + convert_url
        self.export_url = url_base + export_url
        self.create_export_job_url = url_base + create_export_job_url
        self.export_job_url = url_base + export_job_url
        self.import_url = url_base + import_url
        self.sites_url = url_base + sites_url

        if self.client_id and self.client_secret:
            self.maintain_session_token()
        else:
            print(
                "[Access error] Valid credentials are required.\n\nPlease visit https://cloud.nrgsystems.com/data-manager/api-setup\nto access your API credentials"  # noqa: E501
            )
            logger.error(
                "[Access error] Valid credentials are required. Please visit https://cloud.nrgsystems.com/data-manager/api-setup to access your API credentials"  # noqa: E501
            )

    def request_session_token(self) -> None:
        """Generates a new session token for convert service api

        Requires an active account with NRG Cloud. To sign
        up for a free account, go to:

        https://cloud.nrgsystems.com

        Client ID and Secret can be accessed here:

        https://cloud.nrgsystems.com/data-manager/api-setup


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
        print(
            "{} | Requesting session token ... ".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            end="",
            flush=True,
        )

        request_token_header = {
            "content-type": "application/json",
            "user-agent": self.user_agent,
            "python-version": self.python_version,
        }
        request_payload = {
            "clientId": "{}".format(self.client_id),
            "clientSecret": "{}".format(self.client_secret),
        }

        self.resp = requests.post(
            data=json.dumps(request_payload),
            headers=request_token_header,
            url=self.token_url,
        )
        self.session_start_time = datetime.now()
        try:
            self.api_version = parse_version(self.resp.headers["customerapi-version"])
        except Exception:
            self.api_version = parse_version("1.8.0.0")
        logger.info(f"customer api version {self.api_version}")

        if self.resp.status_code == 200:
            print("[OK]")
            logger.info("new session token OK")
            self.session_token = json.loads(self.resp.text)["apiToken"]
        else:
            logger.error("unable to get session token")
            logger.debug(f"{self.resp.text}")
            print("[FAILED] | unable to get session token.")
            self.session_token = False

    def token_valid(self) -> bool:
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
                return True

        return False

    def save_token(self) -> None:
        """save session token in token pickle file"""
        with open(self.token_file_name, "wb") as f:
            pickle.dump(
                [self.session_token, self.session_start_time, self.api_version], f
            )

    def load_token(self) -> None:
        """read session token from pickle file"""
        with open(self.token_file_name, "rb") as f:
            self.session_token, self.session_start_time, self.api_version = pickle.load(
                f
            )

    def maintain_session_token(self) -> None:
        """maintain a current/valid session token for data service api"""
        try:
            self.load_token()
            if not self.token_valid():
                self.request_session_token()
                self.save_token()
        except (FileNotFoundError, ValueError):
            self.request_session_token()
            self.save_token()
        self.headers = {
            "Authorization": "Bearer {}".format(self.session_token),
            "user-agent": self.user_agent,
        }

    def prepare_file_bytes(self, filename: str = "") -> bytes:
        file_bytes = base64.encodebytes(open(filename, "rb").read())
        return file_bytes


def is_authorized(resp) -> bool:
    if (
        resp.status_code == 401
        or resp.status_code == 400
        and "has already been imported" not in resp.text
    ):
        try:
            logger.error(json.loads(resp.text)["apiResponseMessage"])
            print(json.loads(resp.text)["apiResponseMessage"])
        except Exception:
            logger.error("Unable to process request")
            logger.debug(traceback.format_exc())
            print("Unable to complete request.  Check nrgpy log file for details")
        return False

    return True


cloud_api = CloudApi

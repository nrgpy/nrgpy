from datetime import datetime
import json
from .auth import nrg_api, data_catalog_url
import requests


class nrg_api_catalog(nrg_api):
    """Uses NRG hosted web-based API to catalog of available data in text format
    To sign up for the service, go to https://services.nrgsystems.com/

    Parameters
    ----------
    serial_number : str or int
        serial number of data logger (like, 820612345)
    site_number : str or int
        up to 6-digit site number
    start_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    end_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    client_id : str
        provided by NRG Systems
    client_secret : str
        provided by NRG Systems

    Returns
    -------
    object
        export object

    Examples
    --------
    Check for available data files for site number 6

    >>> import nrgpy
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> catalog = nrgpy.nrg_api_catalog(
            client_id=client_id,
            client_secret=client_secret,
            site_number=6,
            serial_number=820600019,
            start_date="2020-05-01",
            end_date="2020-05-03",
            save_file=False
        )

    """

    def __init__(
        self,
        serial_number="",
        site_number="",
        start_date="2014-01-01",
        end_date="2023-12-31",
        client_id="",
        client_secret="",
        **kwargs
    ):
        super().__init__(client_id, client_secret)
        self.site_number = str(site_number).zfill(6)
        self.serial_number = str(serial_number)[-5:]
        self.site_number = str(site_number)
        self.start_date = start_date
        self.end_date = end_date
        self.data_catalog()

    def data_catalog(self):
        import pandas as pd

        self.headers = {"Authorization": "Bearer " + self.session_token}

        self.data = {
            "loggerserialnumber": self.serial_number,
            "sitenumber": self.site_number,
            "startdate": self.start_date,
            "enddate": self.end_date,
        }

        self.request_time = datetime.now()
        self.resp = requests.post(
            data=self.data, url=data_catalog_url, headers=self.headers
        )
        self.request_duration = datetime.now() - self.request_time

        if self.resp.status_code == 200:
            self.f = json.loads(self.resp.content)
            self.json = json.dumps(self.f, indent=2, sort_keys=True)
            self.df = pd.read_json(self.json)

        else:
            print(self.resp.status_code)
            print(self.resp.reason)
            return False

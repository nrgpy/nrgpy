try:
    from nrgpy import logger
except ImportError:
    pass
from .auth import cloud_api, cloud_url_base
import json
import pandas as pd
import requests


class cloud_sites(cloud_api):
    """Find NRG Cloud sites associated with a user.

    Attributes
    ----------
    client_id : str
        available in the NRG Cloud portal
    client_secret : str
        available in the NRG Cloud portal
    sites_list : list of dict
    sites_df : pandas dataframe


    Examples
    --------
    >>> import nrgpy
    >>> client_id = 'go to https://cloud.nrgsystems.com for access'
    >>> client_secret = 'go to https://cloud.nrgsystems.com for access'
    >>> sites = nrgpy.cloud_sites(client_id=client_id, client_secret=client_secret)
    >>> sites.sites_df
    siteId  siteNumber    siteDescription               project  loggerSerialNumber
    0      33        6716           SunnyDog              SunnyDog           820606716
    1     213        1234    Suntastic South             Suntastic           820601234
    >>> sites.get_siteid(site_number=6716)
    33

    """

    def __init__(self, client_id, client_secret, url_base=cloud_url_base):
        """Initialize a cloud_sites object.

        Parameters
        ----------
        client_id : str
            available in the NRG Cloud portal
        client_secret : str
            available in the NRG Cloud portal
        """

        super().__init__(client_id, client_secret, url_base)

        self.get_sites()

    def get_sites(self):
        """Retrieve list of sites user has access to."""

        self.headers = {
            "Authorization": "Bearer " + self.session_token,
        }

        self.resp = requests.get(url=self.sites_url, headers=self.headers)

        self.sites_list = self.resp.json()["sites"]
        logger.info(f"{len(self.sites_list)} sites found")
        self.sites_df = pd.DataFrame(self.sites_list)

    def get_siteid(self, site_number="", logger_sn=""):
        """Get NRG Cloud site ID that corresponds to site number and/or logger SN

        Parameters
        ----------
        site_number : int
            site number
        logger_sn : int
            serial number of logger (beginning with 8206)

        Returns
        -------
        int
            corresponding site ID
        """
        if site_number and logger_sn:
            matching_sites = [
                site_dict
                for site_dict in self.sites_list
                if site_dict["siteNumber"] == site_number
                and site_dict["loggerSerialNumber"] == logger_sn
            ]

            if len(matching_sites) == 1:
                return matching_sites[0]["siteId"]

            else:
                logger.error(
                    f"unable to get site matching site number {site_number} or logger serial {logger_sn}"
                )
                print(
                    "No site matches this site number and logger serial number. "
                    + "Confirm that you have entered the values correctly "
                    + "and that you have access to this site."
                )

        elif site_number:
            matching_sites = [
                site_dict
                for site_dict in self.sites_list
                if site_dict["siteNumber"] == site_number
            ]

            if len(matching_sites) > 1:
                logger.error(f"more than 1 site matching site number {site_number}")
                print(
                    "There is more than one site with that site number. "
                    + "Please use the logger serial number."
                )
                return None

            elif len(matching_sites) == 1:
                logger.info(
                    f"found match for site number {site_number}: siteId {matching_sites[0]['siteId']}"
                )
                return matching_sites[0]["siteId"]

            else:
                logger.error(f"no site matches site number {site_number}")
                print(
                    "No site matches this site number. "
                    + "Confirm that you have entered the value correctly "
                    + "and that you have access to this site."
                )

        elif logger_sn:
            matching_sites = [
                site_dict
                for site_dict in self.sites_list
                if site_dict["loggerSerialNumber"] == logger_sn
            ]

            if len(matching_sites) > 1:
                logger.error(f"more than 1 site matching serial number {logger_sn}")
                print(
                    "There is more than one site with that logger serial number. "
                    + "Please use the site number."
                )
                return None

            elif len(matching_sites) == 1:
                logger.info(
                    f"found match for serial number {logger_sn}: siteId {matching_sites[0]['siteId']}"
                )
                return matching_sites[0]["siteId"]

            else:
                logger.error(f"no site matches serial number {logger_sn}")
                print(
                    "No site matches this logger serial number. "
                    + "Confirm that you have entered the value correctly "
                    + "and that you have access to this site."
                )

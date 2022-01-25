import requests
from nrgpy import logger
from nrgpy.cloud_api.auth import url_base, token_url, export_url, convert_url, sites_url
import traceback


def test_endpoints():
    """check that NRG Cloud API endpoints resolve properly

    Returns
    -------
        Boolean

            True if passed, False it will also print and log the failure
    """

    for url in [url_base, token_url, export_url, convert_url, sites_url]:

        try:

            resp = requests.get(url)

            if resp.status_code > 404 or resp.status_code < 400:

                print(f"Could not resolve {url}")
                logger.error(f"test failed: could not resolve {url}")
                logger.debug(f"resp.status_code = {resp.status_code}")
                logger.debug(f"resp.text = {resp.text}")
                return False

        except:

            logger.error(f"test failed: {traceback.format_exc()}")

    
    logger.info(f"test passed: test_endpoints")
    return True


if __name__ == "__main__":

    test_endpoints()
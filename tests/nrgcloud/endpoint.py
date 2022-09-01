import requests
from nrgpy import logger
from nrgpy.api.auth import (
    retrieve_token_url,
    data_catalog_url,
    convert_url as api_convert_url,
    export_url as api_export_url,
    upload_url as api_upload_url,
)
from nrgpy.cloud_api.auth import (
    url_base,
    token_url,
    export_url,
    convert_url,
    sites_url,
    create_export_job_url,
    export_job_url,
    import_url,
)
import traceback


def test_endpoints():
    """check that NRG Cloud API endpoints resolve properly

    Returns
    -------
        Boolean

            True if passed, False it will also print and log the failure
    """

    for url in [
        url_base,
        token_url,
        export_url,
        convert_url,
        sites_url,
        api_convert_url,
        api_export_url,
        api_upload_url,
        retrieve_token_url,
        data_catalog_url,
        create_export_job_url,
        export_job_url,
        # import_url,
    ]:

        try:

            resp = requests.get(url)

            if (
                resp.status_code > 404 or resp.status_code < 400
            ) and resp.status_code != 500:

                print(f"Could not resolve {url}")
                logger.error(f"test failed: could not resolve {url}")
                logger.debug(f"resp.status_code = {resp.status_code}")
                logger.debug(f"resp.text = {resp.text}")
                return False

            else:

                logger.debug(f"{url} resolved ok")

        except:

            print(f"test failed: {traceback.format_exc()}")
            logger.error(f"test failed: {traceback.format_exc()}")
            return False

    logger.info(f"test passed: test_endpoints")
    return True


if __name__ == "__main__":

    assert test_endpoints()

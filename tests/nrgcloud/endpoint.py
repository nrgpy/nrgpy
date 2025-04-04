import requests
from nrgpy.api.auth import (
    retrieve_token_url,
    data_catalog_url,
    convert_url as api_convert_url,
    export_url as api_export_url,
    upload_url as api_upload_url,
)
from nrgpy.cloud_api.auth import (
    cloud_url_base,
    token_url,
    export_url,
    convert_url,
    sites_url,
    create_export_job_url,
    export_job_url,
    import_url,
)
from nrgpy.common.log import log


def test_endpoints():
    """check that NRG Cloud API endpoints resolve properly

    Returns
    -------
        Boolean

            True if passed, False it will also print and log the failure
    """

    for url in [
        cloud_url_base,
        cloud_url_base + token_url,
        cloud_url_base + export_url,
        cloud_url_base + convert_url,
        cloud_url_base + sites_url,
        cloud_url_base + api_convert_url,
        cloud_url_base + api_export_url,
        cloud_url_base + api_upload_url,
        cloud_url_base + retrieve_token_url,
        cloud_url_base + data_catalog_url,
        cloud_url_base + create_export_job_url,
        cloud_url_base + export_job_url,
        cloud_url_base + import_url,
    ]:

        try:

            resp = requests.get(url)

            if (
                resp.status_code > 404 or resp.status_code < 400
            ) and resp.status_code != 500:

                print(f"Could not resolve {url}")
                log.error(f"test failed: could not resolve {url}")
                log.debug(f"resp.status_code = {resp.status_code}")
                log.debug(f"resp.text = {resp.text}")
                return False

            else:

                log.debug(f"{url} resolved ok")

        except Exception as e:

            print(f"test failed: {e}")
            log.exception("test failed")
            return False

    log.info("test passed: test_endpoints")
    return True


if __name__ == "__main__":

    assert test_endpoints()

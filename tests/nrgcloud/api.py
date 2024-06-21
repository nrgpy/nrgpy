try:
    from nrgpy import logger
except ImportError:
    pass
import nrgpy
import pytest
import traceback


site_id = 175
logger_sn = 820600087
site_number = 353002
start_date = "2021-01-01"
end_date = "2021-01-05"
unauth_site_id = 956


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_sites_api(client_id: str, client_secret: str):
    """Ensure NRG Cloud Sites API is working properly with test account

    Test account has access to site 353002, associated with logger 820600087
    """
    try:
        sites = nrgpy.cloud_sites(client_id, client_secret)

        if (
            sites.sites_df["siteId"]
            .loc[sites.sites_df["loggerSerialNumber"] == logger_sn]
            .values[0]
            != site_id
        ):
            print(f"Site ID != {site_id}: SiteIds = {sites.sites_df['siteId']}")
            logger.error(f"Site ID != {site_id}: SiteIds = {sites.sites_df['siteId']}")
            return False

    except Exception:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        try:
            print(sites.sites_df)
        except Exception:
            print("no sites_df exists")

        return False

    print("Site API test passed!")
    logger.info("Site API test passed!")

    return True


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_api(client_id: str, client_secret: str):
    """"""
    try:
        exporter = nrgpy.CloudExport(
            client_id=client_id,
            client_secret=client_secret,
            site_id=site_id,
            start_date=start_date,
            end_date=end_date,
            out_dir=".",
        )

        exporter.export()

        reader = nrgpy.sympro_txt_read(filename=exporter.export_filepath)

        if int(reader.site_number) != site_number:
            print(f"Export API test failed: site number failure: {reader.site_number}")
            logger.error(
                f"Export API test failed: site number failure: {reader.site_number}"
            )
            return False

    except Exception:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return False

    print("Export API test passed!")
    logger.info("Export API test passed!")
    return True


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_jobs_api(client_id: str, client_secret: str):
    """"""
    try:
        exporter = nrgpy.CloudExportJob(
            client_id=client_id,
            client_secret=client_secret,
            site_id=site_id,
            start_date=start_date,
            end_date=end_date,
            out_dir=".",
        )
        exporter.create_export_job()
        exporter.monitor_export_job(download=True)
        reader = nrgpy.sympro_txt_read(filename=exporter.export_filepath)
        if int(reader.site_number) != site_number:
            print(f"Export API test failed: site number failure: {reader.site_number}")
            logger.error(
                f"Export API test failed: site number failure: {reader.site_number}"
            )
            return False
        return True

    except Exception:

        print(traceback.format_exc())
        logger.error(traceback.format_exc())
    return False


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_jobs_api_unauthorized(client_id: str, client_secret: str):
    """"""
    try:
        exporter = nrgpy.CloudExportJob(
            client_id=client_id,
            client_secret=client_secret,
            site_id=unauth_site_id,
            start_date="2022-01-01",
            end_date="2022-01-10",
            out_dir=".",
        )
        exporter.create_export_job()

        if exporter.resp.status_code == 401:
            return True

    except Exception:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())

    return False


if __name__ == "__main__":
    import sys

    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    assert test_sites_api(client_id, client_secret)
    assert test_export_api(client_id, client_secret)
    assert test_export_jobs_api(client_id, client_secret)
    assert test_export_jobs_api_unauthorized(client_id, client_secret)

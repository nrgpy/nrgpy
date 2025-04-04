from nrgpy.common.log import log
import nrgpy
import pytest
import traceback


SITE_ID = 175
LOGGER_SN = 820600087
SITE_NUMBER = 353002
START_DATE = "2021-01-01"
END_DATE = "2021-01-05"
UNAUTH_SITE_ID = 956


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_sites_api(client_id: str, client_secret: str):
    """Ensure NRG Cloud Sites API is working properly with test account

    Test account has access to site 353002, associated with logger 820600087
    """
    try:
        sites = nrgpy.cloud_sites(client_id, client_secret)

        if (
            sites.sites_df["siteId"]
            .loc[sites.sites_df["loggerSerialNumber"] == LOGGER_SN]
            .values[0]
            != SITE_ID
        ):
            print(f"Site ID != {SITE_ID}: SiteIds = {sites.sites_df['siteId']}")
            log.error(f"Site ID != {SITE_ID}: SiteIds = {sites.sites_df['siteId']}")
            return False

    except Exception as e:
        print(e)
        log.exception("test failed")
        try:
            print(sites.sites_df)
        except Exception:
            print("no sites_df exists")

        return False

    print("Site API test passed!")
    log.info("Site API test passed!")

    return True


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_api(client_id: str, client_secret: str):
    """"""
    try:
        exporter = nrgpy.CloudExport(
            client_id=client_id,
            client_secret=client_secret,
            site_id=SITE_ID,
            start_date=START_DATE,
            end_date=END_DATE,
            out_dir=".",
            unzip=True,
            file_format="singleFile",
        )

        exporter.export()

        reader = nrgpy.sympro_txt_read(filename=exporter.export_filepath)

        if int(reader.site_number) != SITE_NUMBER:
            print(f"Export API test failed: site number failure: {reader.site_number}")
            log.error(
                f"Export API test failed: site number failure: {reader.site_number}"
            )
            return False

    except Exception:
        print(traceback.format_exc())
        log.error(traceback.format_exc())
        return False

    print("Export API test passed!")
    log.info("Export API test passed!")
    return True


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_jobs_api(client_id: str, client_secret: str) -> bool:
    """"""
    try:
        exporter = nrgpy.CloudExportJob(
            client_id=client_id,
            client_secret=client_secret,
            site_id=SITE_ID,
            start_date=START_DATE,
            end_date=END_DATE,
            out_dir=".",
        )
        exporter.create_export_job()
        exporter.monitor_export_job(download=True)
        reader = nrgpy.sympro_txt_read(filename=exporter.export_filepath)
        if int(reader.site_number) != SITE_NUMBER:
            print(f"Export API test failed: site number failure: {reader.site_number}")
            log.error(
                f"Export API test failed: site number failure: {reader.site_number}"
            )
            return False
        return True

    except Exception as e:
        print(e)
        log.exception("test failed")
    return False


@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_export_jobs_api_unauthorized(client_id: str, client_secret: str) -> bool:
    """"""
    try:
        exporter = nrgpy.CloudExportJob(
            client_id=client_id,
            client_secret=client_secret,
            site_id=UNAUTH_SITE_ID,
            start_date="2022-01-01",
            end_date="2022-01-10",
            out_dir=".",
        )
        exporter.create_export_job()

        if exporter.resp.status_code == 401:
            return True

    except Exception as e:
        print(e)
        log.exception("test failed")

    return False


if __name__ == "__main__":
    import sys

    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    assert test_sites_api(client_id, client_secret)
    assert test_export_api(client_id, client_secret)
    assert test_export_jobs_api(client_id, client_secret)
    assert test_export_jobs_api_unauthorized(client_id, client_secret)

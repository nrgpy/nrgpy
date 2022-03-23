try:
    from nrgpy import logger
except:
    pass
import nrgpy
import traceback

def test_sites_api(client_id, client_secret):
    """Ensure NRG Cloud Sites API is working properly with test account
    
    Test account has access to site 4310, associated with logger 820604310
    """
    try:
        print(f"client_id = {client_id[:4]}...etc.")
        sites = nrgpy.cloud_sites(
            client_id,
            client_secret
        )

        if sites.sites_df['siteId'].loc[sites.sites_df['loggerSerialNumber'] == 820604310][0] != 95:
            return False

    except:
        return False

    print("Site API test passed!")
    logger.info("Site API test passed!")

    return True


def test_export_api(client_id, client_secret):
    """"""
    try:
        exporter = nrgpy.cloud_export(
            client_id=client_id,
            client_secret=client_secret,
            site_id=95,
            start_date='2022-02-22',
            end_date='2022-02-24',
            out_dir='.'
        )

        reader = nrgpy.sympro_txt_read(
            filename=exporter.export_filepath
        )

        if int(reader.site_number) != 4310:
            print(f"Export API test failed: site number failure: {reader.site_number}")
            logger.error(f"Export API test failed: site number failure: {reader.site_number}")
            return False

    except:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return False
    
    print("Export API test passed!")
    logger.info("Export API test passed!")
    return True


if __name__ == "__main__":
    import sys
    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    assert test_sites_api(client_id, client_id)
    assert test_export_api(client_id, client_secret)        
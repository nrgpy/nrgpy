from nrgpy import logger
from nrgpy import logr_read
import os
import pytest
import sys
import traceback


# TODO: convert to pytest
@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_logr_read(directory="tests/test_readers/test_files"):
    """Check that LOGR dat files are ingested by nrgpy.logr_read"""

    try:
        reader = logr_read()
        reader.concat_txt(dat_dir=directory)

    except Exception:
        print("Could not create reader from test_files")
        print(traceback.format_exc())
        logger.error("test failed: could not create reader")
        logger.debug(traceback.format_exc())
        return False

    if reader.site_description != "Crows Nest":
        logger.error(f"Site number {reader.site_description} is not 'Crows Nest'")
        print(f"Site number {reader.site_number} is not 'Crows Nest'")
        return False

    if len(reader.data) != 180:
        logger.error(f"Dataframe length {len(reader.data)} is not 180")
        print(f"Dataframe length {len(reader.data)} is not 180")
        return False

    logger.info("Tests pass")
    print("Tests pass!")

    return True


# TODO: convert to pytest
@pytest.mark.skip(reason="this is not set up as a pytest yet")
def test_logr_write(directory="tests/test_readers/test_files"):
    """Confirm output_txt working"""
    try:
        reader = logr_read()
        reader.concat_txt(dat_dir=directory)
        reader.output_txt_file(out_file="test.dat")
        reader_2 = logr_read(filename="test.dat")
        if len(reader.data) == 180:
            logger.info("logr output_txt test passed")
            print("logr output_txt test passed")
            return True
        else:
            logger.error(
                f"logr output_txt test failed, len(reader.data) is {len(reader.data)} not 180"
            )
            print("logr output_txt test failed")
            return False
    except Exception:
        print("Could not create verify write function")
        print(traceback.format_exc())
        logger.error("Could not create verify write function")
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":

    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Working directory: {os.getcwd()}")

    if len(sys.argv) > 1:
        print(f"directory is {sys.argv[1]}")
        assert test_logr_read(os.path.join(os.getcwd(), sys.argv[1]))
    else:
        print("directory is not specified")
        assert test_logr_read()

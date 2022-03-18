from nrgpy import logger
from nrgpy import sympro_txt_read
import os
import traceback


def test_sympro_txt_read(directory="tests/test_readers/test_files"):
    """Check that SymPRO TXT exports are ingested by nrgpy.sympro_txt_read"""

    try:
        reader = sympro_txt_read()
        reader.concat_txt(txt_dir=directory)

    except:
        print(f"Could not create reader from test_files")
        print(traceback.format_exc())
        logger.error("test failed: could not create reader")
        logger.debug(traceback.format_exc())
        return False

    if reader.site_number != "004310":
        logger.error(f"Site number {reader.site_number} is not '004310'")
        print(f"Site number {reader.site_number} is not '004310'")
        return False

    if len(reader.data) != 850:
        logger.error(f"Dataframe length {len(reader.data)} is not 850")
        print(f"Dataframe length {len(reader.data)} is not 850")
        return False

    return True


if __name__ == "__main__":

    directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_files")
    assert test_sympro_txt_read(directory)

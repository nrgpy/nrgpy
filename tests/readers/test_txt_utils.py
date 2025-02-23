from importlib.resources import files
from nrgpy.read.txt_utils import read_text_data

TEST_DATA = files('tests') / 'readers/files'

def test_read_text_data():
    test_file = TEST_DATA / '004310_2022-03-17_00.00_000835_meas.txt'
    reader = read_text_data(filename=test_file, data_type='symphoniepro')
    assert reader.data.shape == (370, 64)
    assert reader.site_info.shape == (217, 2)
    assert reader.ch_info.shape == (15, 12)
    assert reader.ch_info.loc[5, 'Serial Number:'] == '939600122'

#!/bin/usr/python

import pandas as pd
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path

class spidar_data_read(object):
    """

    """

    def __init__(self, filename=''):
        self.filename = filename

        if self.filename:
            # do read things
            pass

    def read_file(self, f):
        self.data = pd.read_csv(f, encoding='UTF_16_LE', parse_dates=[0], index_col=0)
        self.columns = self.data.columns
        

    def concat_txt(self, txt_dir='', output_txt=False, out_file='',
                   file_filter=''):
        """
        """
        self.txt_dir = txt_dir
        self.output_txt = output_txt
        self.out_file = out_file

        
#!/bin/usr/python

import pandas as pd
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path

class spidar_data_read(object):
    """
    reads in CSV file(s) using pandas and creates

           data : pandas dataframe of all available data
        heights : list of measurement heights
    

    parameters
    ----------
      data_file : single CSV or ZIP to be read
      directory : directory of data_files to concatenate
    file_filter : text to filter data files on

    functions
    ----------
        read_file : creates data, heights info
      get_heights : creates list of measurement heights
       concat_txt : combines multiple files together
    """

    def __init__(self, filename=''):
        self.filename = filename

        if self.filename:
            self.read_file(self.filename)
            pass

    def read_file(self, f):
        self.data = pd.read_csv(f, encoding='UTF_16_LE', parse_dates=[0], index_col=0)
        self.data.reset_index(drop=False, inplace=True)
        self.columns = self.data.columns
        self.get_heights()


    def concat_txt(self, txt_dir='', output_txt=False, out_file='',
                   file_filter=''):
        """
        """
        self.txt_dir = txt_dir
        self.output_txt = output_txt
        self.out_file = out_file

    def get_heights(self):
        self.heights = [
            col.split("_")[1]\
            for col in self.columns\
            if "horz_mean" in col\
            and "m/s" in col]
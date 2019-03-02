#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
import re
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path


class symplus3(object):
    """
    class for handling symplus3 txt exports
    """
    def __init__(self, filename='')
        self.data_type = 'symplus3'
        self.filename = filename
        if self.filename != '':
            self.get_site_info()
            self.arrange_ch_info()
            self.get_data()
        pass

    
    def arrange_ch_info(self):
        """
        generates list and dataframe of channel information
        """
        array = [
            'Channel #\t',
            'Type\t',
            'Description\t',
            'Details\t',
            'Serial Number\t',
            'Height	90\t',
            'Scale Factor\t',
            'Offset\t',
            'Units\t'
        ]

        self.ch_info = pd.DataFrame() 
        ch_data = {}
        ch_list = []
        ch_details = 0


    def concat(self, txt_dir='', output_txt=False,
                 output_file='', site_filter=''):
        self.txt_dir = txt_dir
        self.output_file = output_file
        self.site_filter = site_filter
        pass


    def get_site_info(self):
        """
        create dataframe of site info
        """
        header_len = 0
        self.site_info = pd.DataFrame()
        with open(self.filename) as txt_file:
            for line in txt_file:
                if "-----Site Information-----" in txt_file:
                    break
                header_len = header_len + 1                
        self.site_info = pd.read_csv(self.filename, skip_blank_lines=True, nrows=header_len)


    def get_data(self):
        pass
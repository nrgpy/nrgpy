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
        if check_platform() == 'win32':
            self.txt_dir = windows_folder_path(txt_dir)
        else:
            self.txt_dir = linux_folder_path(txt_dir)
        first_file = True
        files = sorted(glob(self.txt_dir + '*.txt'))
        # setup site-info, ch-info with first file
        # probably create dataframe of any channel changes
        ## presence of log file indicates sensor change? maybe?
        for f in files:
            if self.site_filter in f:
                print("Adding {0} ...\t\t".format(f), end="", flush=True)
                if first_file == True:
                    first_file = False
                    try:
                        base = single_file(f)
                        print("[OK]")
                        pass
                    except IndexError:
                        print('Only standard SymPRO headertypes accepted')
                        break
                else:
                    file_path = f
                    try:
                        s = sympro_txt_read(file_path)
                        base.data = base.data.append(s.data, sort=False)
                        print("[OK]")
                    except:
                        print("[FAILED]")
                        print("could not concat {0}".format(file_path))
                        pass
            else:
                pass
        if output_txt == True:
            if out_file == "":
                out_file = datetime.today().strftime("%Y-%m-%d") + "_SymPRO.txt"
            base.data.to_csv(txt_dir + out_file, sep=',', index=False)
            self.out_file = out_file
        try:
            self.ch_info = s.ch_info
            self.ch_list = s.ch_list
            self.data = base.data.drop_duplicates(subset=['Timestamp'], keep='first')
            self.head = s.head
            self.site_info = s.site_info
        except UnboundLocalError:
            print("No files match to contatenate.")
            return None
        self.ch_info = s.ch_info
        self.ch_list = s.ch_list
        self.data = base.data.drop_duplicates(subset=['Timestamp'], keep='first')
        self.head = s.head
        self.site_info = s.site_info        pass


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
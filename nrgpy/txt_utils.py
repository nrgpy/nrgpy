#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
import re
from nrgpy.channel_info_arrays import return_array
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path


class read_text_data(object):
    """
    class for handling known csv-style text data files with header information

    parameters -
           filename : ''; if populated, perform a single file read (takes precedence over txt_dir)
          data_type : ''; REQUIRED; specify instrument that the data file came from
                sep : '\t'; csv separator

            txt_dir : ''; specify folder of like text files to read and concatenate
        file_filter : ''; use when using txt_dir to filter on subset of files
           file_ext : ''; a secondary file filter

    """
    def __init__(self, filename='', data_type='', txt_dir='', file_filter='',
                 file_ext='', sep='\t'):
        if data_type == '':
            print("data_type parameter required.")
            print("\tSymphoniePRO   : use 'data_type='symphoniepro'")
            print("\tSymphoniePLUS3 : use 'data_type='symphonieplus3'")
            return False
        self.data_type = data_type
        self.txt_dir = txt_dir
        self.file_filter = file_filter
        self.file_ext = file_ext
        self.sep = sep
        self.ch_info_array, self.header_sections, self.skip_rows, self.data_type = return_array(self.data_type)
        self.filename = filename
        if self.filename != '':
            self.get_site_info(self.filename)
            self.arrange_ch_info()
            self.get_data(self.filename)
        elif self.txt_dir != '':
            self.concat()
            pass
        else:
            print('set filename or txt_dir parameters to proceed.')


    def __repr__(self):
        return '<class {}: {} >'.format(self.__class__.__name__,self.filename)


    def arrange_ch_info(self):
        """
        generates list and dataframe of channel information
        """
        self.ch_info = pd.DataFrame() 
        ch_data = {}
        ch_list = []
        ch_details = 0

        for row in self.site_info.iterrows(): 
            if row[1][0] == self.ch_info_array[0] and ch_details == 0: # start channel data read
                ch_details = 1
                ch_data[row[1][0]] = row[1][1]
            elif row[1][0] == self.ch_info_array[0] and ch_details == 1: # close channel, start new data read
                ch_list.append(ch_data)
                ch_data = {}
                ch_data[row[1][0]] = row[1][1]
            elif str(row[1][0]) in str(self.ch_info_array):
                ch_data[row[1][0]] = row[1][1]

        ch_list.append(ch_data) # last channel's data
        self.ch_list = ch_list
        self.ch_info = self.ch_info.append(ch_list)
        

    def concat(self, output_txt=False, out_file='', site_filter=''):
        """
        combine exported rwd files (in txt format)
        """
        self.site_filter = site_filter
        if check_platform() == 'win32':
            self.txt_dir = windows_folder_path(self.txt_dir)
        else:
            self.txt_dir = linux_folder_path(self.txt_dir)
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
                        base = read_text_data(filename=f,data_type=self.data_type, 
                                                   file_filter=self.file_filter, file_ext=self.file_ext,
                                                   sep=self.sep)
                        print("[OK]")
                        pass
                    except IndexError:
                        print('Only standard headertypes accepted')
                        break
                else:
                    file_path = f
                    try:
                        s = read_text_data(filename=f,data_type=self.data_type, 
                                           file_filter=self.file_filter, file_ext=self.file_ext,
                                           sep=self.sep)
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
            self.data = base.data.drop_duplicates(subset=[self.header_sections['data_header']], keep='first')
            #self.head = s.head
            self.site_info = s.site_info
        except UnboundLocalError:
            print("No files match to contatenate.")
            return None
        self.ch_info = s.ch_info
        self.ch_list = s.ch_list
        self.data = base.data.drop_duplicates(subset=[self.header_sections['data_header']], keep='first')
        #self.head = s.head
        self.site_info = s.site_info


    def get_site_info(self, _file):
        """
        create dataframe of site info
        """
        self.header_len = 0
        self.site_info = pd.DataFrame()
        with open(self.filename, encoding='ISO-8859-1') as txt_file:
            for line in txt_file:
                if self.header_sections['data_header'] in line:
                    break
                self.header_len += 1                
        self.site_info = pd.read_csv(_file, skiprows=self.skip_rows, skip_blank_lines=True, 
                                     sep=self.sep, nrows=self.header_len,
                                     header=[0,1], encoding='ISO-8859-1', 
                                     error_bad_lines=False, warn_bad_lines=False) #usecols=[0,1],
        if self.data_type == "symplus3":
            self.site_info.reset_index(inplace=True) # , drop=True) works, but only for spro
        #self.site_info = self.site_info.iloc[:self.site_info.iloc[self.site_info[0]==self.header_sections['data_header']].index.tolist()[0]+1]


    def get_data(self, _file):
        """
        create dataframe of tabulated data
        """
        if self.data_type == "sympro":
            self.header_len += 1 # this shouldn't be necessary; something with get_site_info?
        self.data = pd.read_csv(_file, skiprows=self.header_len, 
                                encoding='ISO-8859-1', sep=self.sep)

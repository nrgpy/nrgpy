#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
import re
from nrgpy.channel_info_arrays import return_array
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, draw_progress_bar, renamer


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
    def __init__(self, filename='', data_type='sp3', txt_dir='', file_filter='',
                 filter2='', file_ext='', sep='\t'):
        if not data_type:
            print("data_type parameter required.")
            print("\tSymphoniePRO   : use 'data_type='symphoniepro'")
            print("\tSymphoniePLUS3 : use 'data_type='symphonieplus3'")
            return False

        self.data_type = data_type
        self.txt_dir = txt_dir
        self.file_filter = file_filter
        self.filter2 = filter2
        self.file_ext = file_ext
        self.sep = sep
        self.ch_info_array, self.header_sections, self.skip_rows, self.data_type = return_array(self.data_type)
        self.filename = filename

        if self.filename:
            self.get_head(self.filename)
            self.get_site_info(self.filename)
            self.arrange_ch_info()
            self.get_data(self.filename)
            self.site_number = self.filename.split("\\")[-1][:4]

        elif self.txt_dir:
            #self.concat()
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
        

    def concat(self, output_txt=False, out_file='', file_filter='', filter2='', progress_bar=True):
        """
        combine exported rwd files (in txt format)
        """
        self.file_filter = file_filter

        if self.filter2 == '':
            self.filter2 = filter2
            
        if check_platform() == 'win32':
            self.txt_dir = windows_folder_path(self.txt_dir)
        else:
            self.txt_dir = linux_folder_path(self.txt_dir)

        first_file = True
        files = sorted(glob(self.txt_dir + '*.txt'))
        
        self.file_count = len(files)
        self.pad = len(str(self.file_count)) + 1
        # probably create dataframe of any channel changes
        ## presence of log file indicates sensor change? maybe?
        self.counter = 1
        self.start_time = datetime.now()

        for f in files:

            if self.file_filter in f and self.filter2 in f:

                if progress_bar:
                    draw_progress_bar(self.counter, self.file_count, self.start_time)
                else:
                    print("Adding  {0}/{1}  {2}  ...  ".format(str(self.counter).rjust(self.pad),str(self.file_count).ljust(self.pad),f), end="", flush=True)

                if first_file == True:
                    first_file = False

                    try:
                        base = read_text_data(filename=f,data_type=self.data_type, 
                                                   file_filter=self.file_filter, file_ext=self.file_ext,
                                                   sep=self.sep)
                        if progress_bar != True: print("[OK]")
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
                        if progress_bar != True: print("[OK]")
                    except:
                        if progress_bar != True: print("[FAILED]")
                        print("could not concat {0}".format(file_path))
                        pass
            else:
                pass
            self.counter += 1

        if output_txt == True:

            if out_file == "":
                out_file = datetime.today().strftime("%Y-%m-%d") + "_SymPRO.txt"
            base.data.to_csv(txt_dir + out_file, sep=',', index=False)
            self.out_file = out_file

        try:
            self.ch_info = s.ch_info
            self.ch_list = s.ch_list
            self.data = base.data.drop_duplicates(subset=[self.header_sections['data_header']], keep='first')
            self.head = s.head
            self.site_info = s.site_info
            self.filename = s.filename
            self.site_number = self.filename.split("\\")[-1][:4]
            self.format_rwd_site_data()

        except UnboundLocalError:
            print("No files match to contatenate.")
            return None


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
            self.format_rwd_site_data()
        #self.site_info = self.site_info.iloc[:self.site_info.iloc[self.site_info[0]==self.header_sections['data_header']].index.tolist()[0]+1]


    def get_head(self, _file):
        """
        get the first lines of the file, excluding those without tabs
        up to the self.skip_rows line
        """
        self.head = []
        i=0

        with open(_file) as head_f:
            for line in head_f:
                if i >= self.skip_rows: break
                if "\t" in line: self.head.append(line.replace("\n","").split("\t"))
                i += 1


    def get_data(self, _file):
        """
        create dataframe of tabulated data
        """
        if self.data_type == "sympro":
            self.header_len += 1 # this shouldn't be necessary; something with get_site_info?

        self.data = pd.read_csv(_file, skiprows=self.header_len, 
                                encoding='ISO-8859-1', sep=self.sep)


    def format_rwd_site_data(self):
        """
        adds formatted site dataframe to reader object
        """
        try:
            self.Site_info = self.site_info.copy()
            self._site_info = self.Site_info.T
            self._site_info.columns = self._site_info.iloc[0]
            self._site_info = self._site_info[1:]
            width = list(self._site_info.columns.values).index('-----Sensor Information-----')
            self._site_info.drop(self._site_info.iloc[:, width:len(self._site_info.columns)], axis=1, inplace=True, errors='ignore')

            self.latitude = self._site_info['Latitude'].values[0]
            self.longitude = self._site_info['Longitude'].values[0]
            self.elevation = int(self._site_info['Site Elevation'].values[0])
            self.location = self._site_info['Site Location'].values[0]
            self.site_description = self._site_info['Site Desc'].values[0]
            # self.start_date = self._site_info['Start Date'].values[0]
            self.logger_type = self.head[1][1]
            self.logger_sn = self.logger_type + self.head[2][1]
            self.ipack_sn = ''
            self.ipack_type = ''
            self.time_zone = self._site_info['Time offset (hrs)'].values[0]
            
        except Exception as e:
            self.e = e
            print("Warning: error processing site_info: {}".format(e))
        


def format_sympro_site_data(reader):
    """
    adds formatted site dataframe to reader object
    """
    try:
        reader.Site_info = reader.site_info.copy()
        reader._site_info = reader.Site_info.T
        reader._site_info.columns = reader._site_info.iloc[0]
        reader._site_info.columns = reader._site_info.iloc[0]
        reader._site_info = reader._site_info[1:]
        width = list(reader._site_info.columns.values).index('Sensor History')
        reader._site_info.rename(columns=renamer(), inplace=True)
        reader._site_info.drop(reader._site_info.iloc[:, width:len(reader._site_info.columns)], axis=1, inplace=True, errors='ignore')
        reader._site_info.columns = [str(col).replace(':','').strip() for col in reader._site_info.columns]

        reader.latitude = float(reader._site_info['Latitude'].values[0])
        reader.longitude = float(reader._site_info['Longitude'].values[0])
        reader.elevation = int(reader._site_info['Elevation'].values[0])
        reader.site_number = reader._site_info['Site Number'].values[0]
        reader.site_description = reader._site_info['Site Description'].values[0]
        reader.start_date = reader._site_info['Start Date'].values[0]
        reader.logger_sn = reader._site_info['Serial Number'].values[0]
        reader.ipack_sn = reader._site_info['Serial Number_1'].values[0]
        reader.logger_type = reader._site_info['Model'].values[0]
        reader.ipack_type = reader._site_info['Model_1'].values[0]
        reader.time_zone = reader._site_info['Time Zone'].values[0]
        
    except Exception as e:
        reader.e = e
        print("Warning: error processing site_info: {}".format(e))



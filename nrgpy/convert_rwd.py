#!/bin/usr/python

import datetime
import time
import os
import pandas as pd
import pathlib
import subprocess
import shutil
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, affirm_directory, count_files, draw_progress_bar


class local(object):
    """
    nrgpy.convert_rwd.local - use local installation of Symphonie Data Retriever (SDR)
    to convert *.RWD files to *.TXT

    parameters -
              filename : '', if populated, a single file is exported
        encryption_pin : '', four digit pin, only used for encrypted files
              sdr_path : r'"C:/NRG/SymDR/SDR.exe"', may be any path
           file_filter : '', filters files on text in filename
               rwd_dir : '', folder to check for RWD files
               out_dir : '', folder to save exported TXT files into
           wine_folder : '~/.wine/drive_c/', for linux installations
         use_site_file : False, set to True to use local site file
              raw_mode : False, set to True to convert raw counts and voltages
          progress_bar : True, set to False to see individual file conversions


    functions -
        check_sdr : checks operating system for SDR installation
          convert : process files

    """


    def __init__(self, rwd_dir='', out_dir='', filename='', encryption_pin='',
                 sdr_path=r'C:/NRG/SymDR/SDR.exe',
                 convert_type='meas', file_filter='', 
                 wine_folder='~/.wine/drive_c/', 
                 use_site_file=False, raw_mode=False, progress_bar=False, **kwargs):
        if encryption_pin != '':
            self.command_switch = '/z' # noqueue with pin
        else:
            self.command_switch = '/q' # noqueue (logger params)
        if use_site_file == True:
            self.command_switch = '/s' # silent (site file params)
        if raw_mode == True:
            self.command_switch = '/r' # silent (site file params)
        self.progress_bar = progress_bar
        self.encryption_pin = encryption_pin
        self.sdr_path = windows_folder_path(sdr_path)[:-1]
        self.root_folder = "\\".join(self.sdr_path.split('\\')[:-2])
        self.RawData = self.root_folder + '\\RawData\\'
        self.ScaledData = self.root_folder + '\\ScaledData\\'
        self.file_filter = file_filter
        if 'site_filter' in kwargs and file_filter == '':
            self.file_filter = kwargs.get('site_filter')
        self.rwd_dir = windows_folder_path(rwd_dir) # rwd_dir must be in Windows format, even if using Wine
        self.platform = check_platform()
        self.wine_folder = wine_folder
        self.check_sdr()
        if self.platform == 'win32':
            self.out_dir = windows_folder_path(out_dir)
            self.file_path_joiner = '\\'            
        else:
            self.out_dir = linux_folder_path(out_dir)
            self.file_path_joiner = '/'
        self.filename = filename
        if self.filename:
            self.counter = 1
            self.rwd_dir = os.path.dirname(self.filename)
            self.file_filter = os.path.basename(self.filename)
            self.convert()


    def check_sdr(self):
        """
        determine if SDR is installed
        """
        if self.platform == 'win32':
            # do the windows check
            try:
                os.path.exists(self.sdr_path)
                self.sdr_ok = True
                print('SDR test OK!')
            except:
                self.sdr_ok = False
                print('SDR not installed. Please install SDR or check path.\nhttps://www.nrgsystems.com/support/product-support/software/symphonie-data-retriever-software')
        else:
            # do the linux check
            try:
                subprocess.check_output(['wine','--version'])
            except NotADirectoryError:
                print('System not configured for running SDR.\n Please follow instructions in SDR_Linux_README.md to enable.')
            try:
                subprocess.check_output(['wine',self.sdr_path,'/s','test.rwd'])
                self.sdr_ok = True
                print('SDR test OK!')
                os.remove(os.path.join(self.wine_folder, "NRG/ScaledData/test.log"))
            except Exception as e:
                self.sdr_ok = False
                print('SDR unable to start')
                print(e)

    
    def convert(self):
        """
        process rwd files
            1 - create list of RWD files that match filtering
            2 - copy RWD files to RawData directory
            3 - create out_dir if necessary
            4 - iterate through files
        """
        self._list_files()
        self._copy_rwd_files()
        affirm_directory(self.out_dir)
        self.raw_count = len(self.rwd_file_list)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        self.convert_time = time.time()
        self.start_time = datetime.datetime.now()

        for f in sorted(self.rwd_file_list):
            site_num = f[:4]
            try:
                self._filename = "\\".join([self.RawData+site_num,f])
                self._single_file()
            except:
                print('file conversion failed on {}'.format(self._filename))
            self.counter += 1
        txt_count = count_files(self.out_dir, self.file_filter.split(".")[0], 'txt', start_time=self.convert_time)
        log_count, log_files = count_files(self.out_dir, self.file_filter, 'log', show_files=True, start_time=self.start_time)
        print('\nRWDs in    : {}'.format(self.raw_count))
        print('TXTs out   : {}'.format(txt_count))
        print('LOGs out   : {}'.format(log_count))
        if len(log_files) > 0:
            print('Log files created:')
            for _filename in log_files:
                print('\t{}'.format(_filename))
        print('----------------\nDifference : {}'.format(self.raw_count - (txt_count + log_count)))


    def _list_files(self):
        """
        get list of files in rwd_dir
        """
        self.dir_paths = []
        self.rwd_file_list = []
        if self.platform == 'win32':
            walk_path = self.rwd_dir
        else:
            walk_path = linux_folder_path(self.rwd_dir)
        for dirpath, subdirs, files in os.walk(walk_path):
            self.dir_paths.append(dirpath)
            for x in files:
                if x.startswith(self.file_filter) and x.lower().endswith('.rwd'):
                    self.rwd_file_list.append(x)


    def _single_file(self):
        """
        process for converting a single file
        """
        _f = self._filename
        if self.platform == 'linux':
            self.sdr_path = windows_folder_path(self.sdr_path)[:-1]
            _f = windows_folder_path(_f)[:-1]
            wine = 'wine'
        else:
            wine = ''
        self.cmd = [wine, '"'+self.sdr_path+'"', self.command_switch, self.encryption_pin, '"'+_f+'"']
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print("Converting  {0}/{1}  {2}  ...  ".format(str(self.counter).rjust(self.pad),str(self.raw_count).ljust(self.pad),_f.split("\\")[-1]), end="", flush=True)
            subprocess.check_output(" ".join(self.cmd), shell=True)
            if not self.progress_bar: print("[DONE]")
            try:
                self._copy_txt_file()
            except:
                print('unable to copy {} to text folder'.format(_f))
        except Exception as e:
            if not self.progress_bar: print("[FAILED]")
            print('unable to convert {}. check ScaledData folder for log file'.format(_f))
            print(e)

            
            
    def _copy_rwd_files(self):
        """
        copy RWD files from self.RawData to self.rwd_dir
        """
        for f in sorted(self.rwd_file_list):
            if self.file_filter in f:
                site_num = f[:4]
                site_folder = "\\".join([self.RawData,site_num])
                if self.platform == 'linux':
                    site_folder = ''.join([self.wine_folder,'NRG/RawData/',site_num])
                try:
                    affirm_directory(site_folder)
                except:
                    print("couldn't create {}".format(site_folder))
                    pass
                try:
                    shutil.copy("".join([self.dir_paths[0], f]), site_folder)                    
                except:
                    print('unable to copy file to RawData folder:  {}'.format(f))


    def _copy_txt_file(self):
        """
        copy TXT file from self.ScaledData to self.out_dir
        """
        try:
            txt_file_name = self._filename.split('\\')[-1][:-4] + '.txt'
            txt_file_path = self.file_path_joiner.join([self.ScaledData,txt_file_name])
            out_path = self.file_path_joiner.join([self.out_dir,txt_file_name])
        except:
            print("could not do the needful")
        if self.platform == 'linux':
            out_path = linux_folder_path(self.out_dir) + txt_file_name
            txt_file_path = ''.join([self.wine_folder, 'NRG/ScaledData/',txt_file_name])
        try:
            shutil.copy(txt_file_path, out_path)
            try:
                os.remove(txt_file_path)
            except:
                print("{0} remains in {1}".format(txt_file_name, self.ScaledData))
        except:
            print("Unable to copy {0} to {1}".format(txt_file_name,self.out_dir))









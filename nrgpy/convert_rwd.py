#!/bin/usr/python

import io
import glob
import os
import pandas as pd
from pathlib import Path
import requests
import subprocess
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path


class local(object):
    """
    nrgpy.convert_rwd.local - use local installation of Symphonie Data Retriever (SDR)
    to convert *.RWD files to *.TXT

    parameters -
              filename : '', if populated, a single file is exported
        encryption_pin : '', four digit pin, only used for encrypted files
              sdr_path : r'"C:/NRG/SymDR/SDR.exe"', may be any path
           site_filter : '', filters files on text in filename
               rwd_dir : '', folder to check for RWD files
               out_dir : '', folder to save exported TXT files into


    functions -
        check_sdr : checks operating system for SDR installation
          convert : process files

    """


    def __init__(self, rwd_dir='', out_dir='', filename='', encryption_pin='',
                 sdr_path=r'C:/NRG/SymDR/SDR.exe',
                 convert_type='meas', site_filter='', **kwargs):
        if encryption_pin != '':
            self.command_switch = '/z'
        else:
            self.command_switch = '/q'
        self.encryption_pin = encryption_pin
        self.sdr_path = windows_folder_path(sdr_path)
        self.root_folder = "\\".join(self.sdr_path.split('\\')[:-2])
        self.RawData = self.root_folder + '\\RawData\\'
        self.ScaledData = self.root_folder + '\\ScaledData\\'
        self.site_filter = site_filter
        self.rwd_dir = windows_folder_path(rld_dir) # rwd_dir must be in Windows format, even if using Wine
        self.platform = check_platform()
        if self.platform == 'win32':
            self.out_dir = windows_folder_path(out_dir)
            # do windows conversion
            pass
        else:
            self.out_dir = linux_folder_path(out_dir)
            # check if Wine is installed... 
            self.check_wine()
            # check if SDR is installed...
            self.check_sdr()
            # EXCEPT: print instructions for installation (maybe there's an "install_SDR_on_Linux.sh" script)
        if filename != '':
            self.filename = filename
            self.single_file()

    def check_sdr(self):
        """
        determine if SDR is installed
        """
        if self.platform == 'win32':
            # do the windows check
            try:
                os.path.exists(self.sdr_path)
            except:
                print('SDR not installed. Please install SDR or check path.\nhttps://www.nrgsystems.com/support/product-support/software/symphonie-data-retriever-software')
                break
        else:
            # do the linux check
            try:
                subprocess.check_output(['wine','--version'])
            except NotADirectoryError:
                print('System not configured for running SDR.\n Please follow instructions in SDR_Linux_README.md to enable.')
                break
            try:
                subprocess.check_output(['wine',self.sdr_path,'/s','test.rwd'])
                print('SDR test OK!')
            except:
                print('SDR unable to start')
                break

    
    def convert(self):
        """
        process rwd files
        """
        # create a list of files to export
        self.list_files()
        # copy RWD file to RawData folder, site subfolder (1234)
        self.copy_rwd_files()
        # convert the files in the list
        for f in self.rwd_file_list[0]:
            site_num = f[:4]
            self.single_file("\\".join([self.RawData,site_num,f]))


    def list_files(self):
        """
        get list of files in rwd_dir
        """
        self.dir_paths = []
        self.rwd_file_list = []
        for dirpath, subdirs, files in os.walk(self.rwd_dir):
            self.dir_paths.append(dirpath)
            for x in files:
                if self.site_filter in x:
                    self.rwd_file_list.append(x)


    def single_file(self, _f):
        """
        process for converting a single file
        """
        cmd = [self.sdr_path, self.command_switch, self.encryption_pin, _f]
        if self.platform == 'linux':
            cmd.insert(0, 'wine')
        try:
            subprocess.check_output(" ".join(cmd), shell=True)
        except:
            print('unable to convert {}. check ScaledData folder for log file'.format(_f))
            
            
    def copy_rwd_files(self):
        """
        copy RWD files from self.RawData to self.rwd_dir
        """
        for f in self.rwd_file_list:
            site_num = f[:4]
            site_folder = "\\".join([self.RawData,site_num])
            try:
                subprocess.check_output(['md',site_folder])
            except:
                pass
            try:
                cmd = ['copy',"\\".join([paths[0]), f]),"\\".join([site_folder, f])] 
                subprocess.check_output(cmd, shell=True)
            except:
                print('unable to convert {}'.format(f))


    def copy_txt_file(self, _f):
        """
        copy TXT file from self.ScaledData to self.out_dir
        """
        txt_file_name = _f[:-4],'.txt'
        txt_file_path = "\\".join([self.ScaledData,txt_file_name])
        out_path = "\\".join([self.out_dir,txt_file_name])
        cmd = ['copy',txt_file_path,out_path]
        try:
            subprocess.check_output(cmd, shell=True)
        except:
            print('unable to move {}'.format(_f))







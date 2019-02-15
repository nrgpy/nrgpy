#!/bin/usr/python

import os
import pandas as pd
import subprocess
import shutil
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, affirm_directory


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
           wine_folder : '~/.wine/drive_c/', for linux installations


    functions -
        check_sdr : checks operating system for SDR installation
          convert : process files

    """


    def __init__(self, rwd_dir='', out_dir='', filename='', encryption_pin='',
                 sdr_path=r'C:/NRG/SymDR/SDR.exe',
                 convert_type='meas', site_filter='', 
                 wine_folder='~/.wine/drive_c/', **kwargs):
        if encryption_pin != '':
            self.command_switch = '/z'
        else:
            self.command_switch = '/q'
        self.encryption_pin = encryption_pin
        self.sdr_path = windows_folder_path(sdr_path)[:-1]
        self.root_folder = "\\".join(self.sdr_path.split('\\')[:-2])
        self.RawData = self.root_folder + '\\RawData\\'
        self.ScaledData = self.root_folder + '\\ScaledData\\'
        self.site_filter = site_filter
        self.rwd_dir = windows_folder_path(rwd_dir) # rwd_dir must be in Windows format, even if using Wine
        self.platform = check_platform()
        if self.platform == 'win32':
            self.out_dir = windows_folder_path(out_dir)
            self.file_path_joiner = '\\'            
            pass
        else:
            self.out_dir = linux_folder_path(out_dir)
            self.check_sdr()
            self.file_path_joiner = '/'
        if filename != '':
            self.filename = filename
            self.single_file()
        self.wine_folder = wine_folder

    def check_sdr(self):
        """
        determine if SDR is installed
        """
        if self.platform == 'win32':
            # do the windows check
            try:
                os.path.exists(self.sdr_path)
                self.sdr_ok = True
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
                print('SDR test OK!')
                self.sdr_ok = True
            except:
                self.sdr_ok = False
                print('SDR unable to start')

    
    def convert(self):
        """
        process rwd files
            1 - create list of RWD files that match filtering
            2 - copy RWD files to RawData directory
            3 - create out_dir if necessary
            4 - iterate through files
        """
        self.list_files()
        self.copy_rwd_files()
        affirm_directory(self.out_dir)
        for f in self.rwd_file_list:
            site_num = f[:4]
            try:
                self._filename = "\\".join([self.RawData+site_num,f])
                self.single_file()
            except:
                print('file conversion failed on {}'.format(self._filename))


    def list_files(self):
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
                if x.startswith(self.site_filter) and x.lower().endswith('.rwd'):
                    self.rwd_file_list.append(x)


    def single_file(self):
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
        cmd = [wine, '"'+self.sdr_path+'"', self.command_switch, self.encryption_pin, '"'+_f+'"']
        try:
            print("Converting {}\t\t".format(_f), end="", flush=True)
            subprocess.check_output(" ".join(cmd), shell=True)
            self.copy_txt_file(_f.split(self.file_path_joiner)[-1])
            print("[DONE]")
        except:
            print("[FAILED]")
            print('unable to convert {}. check ScaledData folder for log file'.format(_f))
            
            
    def copy_rwd_files(self):
        """
        copy RWD files from self.RawData to self.rwd_dir
        """
        for f in self.rwd_file_list:
            if self.site_filter in f:
                site_num = f[:4]
                site_folder = "\\".join([self.RawData,site_num])
                copy_cmd = 'copy'
                if self.platform == 'linux':
                    site_folder = ''.join([self.wine_folder,'NRG/RawData/',site_num])
                    copy_cmd = 'cp'
                try:
                    affirm_directory(site_folder)
                except:
                    print("couldn't create {}".format(site_folder))
                    pass
                try:
                    cmd = [copy_cmd,"".join([self.dir_paths[0], f]),self.file_path_joiner.join([site_folder, f])] 
                    subprocess.check_output(" ".join(cmd), shell=True)
                except:
                    print('unable to copy file to RawData folder:  {}'.format(f))


    def copy_txt_file(self, _f):
        """
        copy TXT file from self.ScaledData to self.out_dir
        """
        txt_file_name = _f[:-4] + '.txt'
        txt_file_path = "\\".join([self.ScaledData,txt_file_name])
        out_path = file_path_joiner.join([self.out_dir,txt_file_name])
        cmd = ['copy',txt_file_path,out_path]
        if self.platform == 'linux':
            out_path = linux_folder_path(self.out_dir) + txt_file_name
            txt_file_path = ''.join([self.wine_folder, 'NRG/ScaledData/',txt_file_name])
            print(txt_file_path)
            print(out_path)
            shutil.copy(txt_file_path, out_path)
        try:
            print(" ".join(cmd))
            subprocess.check_output(" ".join(cmd), shell=True)
        except:
            print('unable to move {}'.format(_f))







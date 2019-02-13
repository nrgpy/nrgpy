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
    nrgpy.convert_rwd.local - use local installation of Symphonie Data Retriever to
    convert *.RWD files to *.TXT

    parameters -
        encryption_pin : '', four digit pin, only used for encrypted files
              sdr_path : r'"C:/NRG/SymDR/SDR.exe"', may be any path
           site_filter : '', filters files on text in filename
               rwd_dir : '', folder to check for RWD files

    """


    def __init__(self, rwd_dir='', out_dir='', encryption_pass='',
                 sdr_path=r'"C:/NRG/SymDR/SDR.exe"',
                 convert_type='meas', site_filter='', out_dir='', **kwargs):
        self.encryption_pin = encryption_pin
        self.sdr_path = sdr_path
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
                pass
            except:
                pass
        
        
    def check_wine(self):
        """
        determine if Wine is installed. Only used if self.platform == 'linux'
        """
        pass

    
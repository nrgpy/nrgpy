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
    
    """


    def __init__(self, rwd_dir='', out_dir='', encryption_pass='',
                 sdr_path=r'"C:/NRG/SymDR/SDR.exe"',
                 convert_type='meas', site_filter='', **kwargs):
        self.encryption_pin = encryption_pin
        self.sdr_path = sdr_path
        self.site_filter = site_filter
        self.rwd_dir = windows_folder_path(rld_dir) # rwd_dir must be in Windows format, even if using Wine
        if check_platform() == 'win32':
            self.out_dir = windows_folder_path(out_dir)
            # do windows conversion
            pass
        else:
            self.out_dir = linux_folder_path(out_dir)
            # check if Wine is installed... 
            # check if SDR is installed...
            # EXCEPT: print instructions for installation (maybe there's an "install_SDR_on_Linux.sh" script)

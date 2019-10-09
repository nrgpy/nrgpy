#!/bin/usr/python

import base64
from datetime import datetime
import io
import glob
import os
import pandas as pd
from pathlib import Path
import requests
import subprocess
import time
import zipfile
from nrgpy.api_connect import nrgApiUrl, token as tk
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, affirm_directory, count_files


class local(object):
    """    
    For handling NRG SymphoniePRO Data Logger raw data files in the *.rld format.
    This method uses locally installed SymphoniePRO Desktop software to convert
    *.rld files to txt format (tab-delimited-text).
    
    
    parameters:
                rld_dir: '', or specify directory. Note for unc values, you 
                          will need to escape all forward slashes, e.g.
                          rld_dir = "\\\\sol\\techsupport\\data\\" 
                          or use the r'\\path\to\dir' approach
                out_dir: '', see note for 1.
        encryption_pass: '', specify data encryption password if logger is 
                          set up for that.
            sympro_path: "C:\Program Files (x86)\Renewable NRG Systems\SymPRO Desktop\SymPRODesktop.exe"
           convert_type: 'meas', alternately specify 'comm', 'diag', 'sample', or 'events'
                    nec: '', path to nec file
            site_filter: '', or specify part or all of the file you'd like to
                          filter on. Eg. site_filter='123456_2018-09' would filter on site 123456
                          and only the month of September in 2018.
    
    functions:
         concat_txt(): combines all txt files in txt_dir (out_dir by default) that 
                       include self.site_filter into one txt file with header from first file.
                       out_file can be specified; defaults to %Y-%m-%d_SymPRO.txt in 
                       current directory.
          directory(): processes all rld files in self.rld_dir, outputs to txt files 
                       to out_dir ( aliases = convert() and process() )
         rename_rld(): for calling the site-serial renaming tool to insert the serial number
                       into the filename
        single_file(): pass single file's complete path for export.
    ------------------------------------------------------------------------------
    
    """
    def __init__(self, rld_dir='', out_dir='', encryption_pass='',
                 sympro_path=r'"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"',
                 convert_type='meas', nec='', site_filter='', **kwargs):
        self.rld_dir = windows_folder_path(rld_dir)
        self.out_dir  = windows_folder_path(out_dir)
        self.encryption_pass = encryption_pass
        self.sympro_path = sympro_path
        self.convert_type = convert_type
        self.nec = nec
        self.site_filter = site_filter
        if 'file_filter' in kwargs and site_filter == '':
            self.file_filter = kwargs.get('file_filter')
            self.site_filter = self.file_filter
        if check_platform() == 'win32':
            pass
        else:
            print("""
            convert_rld.local() method ONLY compatible with Windows OS. 
            Please use convert_rld.nrg_convert_api() method instead.
            """)
    

    def directory(self):
        """
        processes all rld files in self.rld_dir, outputs to txt files to out_dir
        """
        affirm_directory(self.out_dir)
        try:
            if self.encryption_pass != '':
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ''
        except:
            print('could not parse encryption_pass')
        try:
            if self.nec != '':
                nec = '/config "{0}"'.format(self.nec)
            else:
                nec = ''
        except:
            print('could not parse encryption_pass')            
        try:
            rld_count = count_files(self.rld_dir, self.site_filter, 'rld')
            self.start_time = time.time()
            print('\nConverting {0} files from {1}\n'.format(rld_count, self.rld_dir))
            print('Saving outputs to {0}'.format(self.out_dir))
            cmd = [self.sympro_path, 
                   "/cmd", "convert", 
                   "/file", '"'+"\\".join([self.rld_dir, self.site_filter])+'*.rld"', 
                   encryption,
                   nec,  
                   "/type", '"'+self.convert_type+'"',
                   "/outputdir", '"'+self.out_dir[:-1]+'"'
            ]
            print('\nUsing command line script:\n{}'.format(" ".join(cmd)))
            self.start = datetime.now()
            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            self.end = datetime.now()
            self.convert_time = str(self.end - self.start)
            print('\nTXT files saved in {0}\n'.format(self.out_dir))
            txt_count = count_files(self.out_dir, self.site_filter, 'txt', start_time=self.start_time)
            log_count, log_files = count_files(self.out_dir, self.site_filter, 'log', show_files=True, start_time=self.start_time)
            print('RLDs in    : {}'.format(rld_count))
            print('TXTs out   : {}'.format(txt_count))
            print('LOGs out   : {}'.format(log_count))
            if len(log_files) > 0:
                print('Log files created:')
                for _filename in log_files:
                    print('\t{}'.format(_filename))
            print('----------------\nDifference : {}'.format(rld_count - (txt_count + log_count)))
        except FileNotFoundError:
            print("""
                  No instance of SymphoniePRO Desktop Application found.

                  Please follow the link below to download and install this software:
                  https://www.nrgsystems.com/support/product-support/software/symphoniepro-desktop-application

                  """)
        except:
            print('Unable to process files in directory')


    def convert(self):
        self.directory()
    def process(self):
        self.directory()


    def rename_rlds(self, **kwargs):
        """
        uses SymPRO utility NrgRldSiteSerialRename.exe to rename files with site number
        and logger serial number. This function is only compatible with Windows>=7 AND
        a local installation of SymphoniePRO Desktop software
        """
        try:
            renamer_path = kwargs.get('renamer_path', r"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/Default Application Files/Utilities/NrgRldSiteSerialRename.exe")
        
            for f in os.listdir(self.rld_dir):
                filepath = self.rld_dir + f
                if f[-4:].lower()==".rld" and self.site_filter in f:
                    rename_cmd = [renamer_path, '"'+filepath+'"']
                    try:
                        subprocess.run(" ".join(rename_cmd), stdout=subprocess.PIPE)
                    except:
                        print("Unable to rename {0}".format(f))
                        pass
                    
                else:
                    pass
        except:
            print('Could not rename files')
            

    def single_file(self, filepath=''):
        self.filepath = filepath.replace('/','\\')
        cmd = [self.sympro_path, "/cmd", "convert", "/file", '"'+filepath+'"', "/type", '"'+self.convert_type+'"',"/outputdir", '"'+self.out_dir[:-1]+'"']
        try:
            print("{0} ... \t\t".format(filepath), end="", flush=True)
            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            print("[DONE]")
        except:
            print("\n\t processing {0} [FAILED]".format(filepath))
            pass
        

        print("\nQueue processed\n")

class nrg_convert_api(object):
    """
    Uses NRG hosted web-based API to convert RLD files to zipped CSV (text) format.
    The URL is pulled from the nrg_api_url.py file. Note that there is a token 
    placeholder in nrg_api_url.py that will be used if
    
    1. it is not blank
    2. a valid token is NOT passed as an argument
    
    """
    def __init__(self, rld_dir='', out_dir='', filename='', site_filter='', 
                 encryption_pass='', token='', header_type='standard', 
                 export_type='meas', export_format='csv_zipped', **kwargs):    
        if check_platform() == 'win32':
            self.platform = 'win32'
            self.folder_split = '\\'
            self.rld_dir = windows_folder_path(rld_dir)
            self.out_dir = windows_folder_path(out_dir)
        else:
            self.platform = 'linux'
            self.folder_split = '/'
            self.rld_dir = linux_folder_path(rld_dir)
            self.out_dir = linux_folder_path(out_dir)
        self.encryption_pass = encryption_pass
        self.export_format = export_format
        self.export_type = export_type
        self.site_filter = site_filter
        if 'file_filter' in kwargs and site_filter == '':
            self.file_filter = kwargs.get('file_filter')
            self.site_filter = self.file_filter
        self.header_type = header_type
        self.token = token
        affirm_directory(self.out_dir)

        
        #import nrgApiUrl, token as tk
        self.NrgUrl = nrgApiUrl
        if len(tk) > 10 and len(self.token) < 10:
            self.token = tk
        if self.token == '':
            print('\n\nA valid token is required to use the nrg_convert_api.\nPlease contact support@nrgsystems.com for an API token')
            return 0
        if filename != '':
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.single_file(filename)
#        self.process()

    def process(self):
        filelist = sorted(glob.glob(self.rld_dir + self.site_filter + '*.rld'))
        self.raw_count = len(filelist)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        for rld in filelist:
            self.single_file(rld)
            self.counter += 1
        print('\nQueue processed\n')


    def single_file(self, rld):
        try:
            print("Processing {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad),str(self.raw_count).ljust(self.pad),os.path.basename(rld)), end="", flush=True)
            RldFileBytes = open(rld,'rb').read()
            EncodedFileBytes = base64.encodebytes(RldFileBytes)

            Data = {'apitoken': self.token,
                    'encryptionpassword': self.encryption_pass,
                    'headertype': self.header_type, #standard | columnonly | none
                    'exportformat': self.export_format, # csv_zipped (default) | parquet
                    'filebytearray': EncodedFileBytes} 

            self.resp=requests.post(data=Data, url=self.NrgUrl)
            zippedDataFile = zipfile.ZipFile(io.BytesIO(self.resp.content))
            regDataFile = self.resp.content
            name = zippedDataFile.infolist().pop()
            outFileName =  "".join(rld.split(self.folder_split)[-1:])[:-4] + '_' + self.export_type +  '.txt'

            with open(os.path.join(self.out_dir, outFileName),'wb') as outputfile:
                outputfile.write(zippedDataFile.read(name))

            #fix windows newline garbage
            try:
                filename = os.path.join(self.out_dir, outFileName)
                fileContents = open(filename,"r").read()
                f = open(filename,"w", newline="\r\n")
                f.write(fileContents)
                f.close()
            except:
                print("Could not convert Windows newline characters properly; file may be unstable")

            print("[DONE]")

        except:
            print("[FAILED]")
            print('unable to process file: {0}'.format(rld))
            print(str(self.resp.status_code) + " " + self.resp.reason + "\n")
            pass


    def convert(self):
        self.process()

#!/bin/usr/python

import base64
from datetime import datetime, date, timedelta
import io
import glob
import os
import pandas as pd
from pathlib import Path
import requests
import subprocess
import time
import zipfile
from nrgpy.api_connect import nrgApiUrl, token as tk, ConvertServiceUrl, RequestTokenUrl, request_session_token, token_valid, maintain_session_token
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, affirm_directory, count_files, date_check, draw_progress_bar


class local(object):
    """For handling NRG SymphoniePRO Data Logger raw data files in the *.rld format.

    This method uses locally installed SymphoniePRO Desktop software to convert *.rld files to txt format (tab-delimited-text).
    
    Parameters
    ----------
    rld_dir : str, optional
        specify directory. Note for unc values, you 
        will need to escape all forward slashes, e.g.
        rld_dir = "\\\\sol\\techsupport\\data\\" 
        or use the r'\\path\to\dir' approach
    out_dir : str, optional
        see note for rld_dir.
    encryption_pass : str
        specify data encryption password if logger is set up for that.
    hex_key : str
        specify if using hex data encryption key
    sympro_path : str
        default is "C:\Program Files (x86)\Renewable NRG Systems\SymPRO Desktop\SymPRODesktop.exe"
    process_type : str
        [convert], or import
    convert_type : str
        'meas', alternately specify 'comm', 'diag', 'sample', or 'events'
    nec : str
        path to nec file
    site_filter : str
        specify part or all of the file you'd like to filter on, like site_filter='123456_2018-09' 
        would filter on site 123456 and only the month of September in 2018.
    site_file : bool or str
        set to True to use local ndb site file, or set to path to an alternate ndb site file

    Examples
    --------
    Convert a folder of RLD files to Text with SymphoniePRO Desktop Software

    >>> from nrgpy.convert_rld import local
    >>> converter = local(
            rld_dir='/path/to/rld/files', 
            out_dir=/path/to/txt/outputs, 
            file_filter='123456_2020-01', # for files from January 2020
        )
    >>> converter.convert()
    """
    def __init__(self, rld_dir='', out_dir='', encryption_pass='', hex_key='', filename='',
                 sympro_path=r'"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"',
                 process_type='convert', convert_type='meas', nec='', site_filter='', site_file='', **kwargs):
        
        self.rld_dir = windows_folder_path(rld_dir)
        self.out_dir  = windows_folder_path(out_dir)
        self.encryption_pass = encryption_pass
        self.hex_key = hex_key
        self.sympro_path = sympro_path
        self.process_type = process_type
        self.convert_type = convert_type
        self.nec = nec
        self.site_filter = site_filter
        self.site_file = site_file

        if 'file_filter' in kwargs and site_filter == '':
            self.file_filter = kwargs.get('file_filter')
            self.site_filter = self.file_filter

        if check_platform() == 'win32':
            if filename:
                affirm_directory(self.out_dir)
                self.single_file(filepath=filename)
        else:
            print("""
            convert_rld.local() method ONLY compatible with Windows OS. 
            Please use convert_rld.nrg_convert_api() method instead.
            """)
    

    def directory(self):
        """processes all rld files in self.rld_dir, outputs to txt files to out_dir"""
        affirm_directory(self.out_dir)
        
        try:
            if self.encryption_pass:
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ''
        except:
            print('could not parse encryption_pass')
        
        try:
            if self.hex_key:
                encryption_key = '/key "{0}"'.format(self.hex_key)
            else:
                encryption_key = ''
        except:
            print('could not parse hex_key')
        
        try:
            if self.nec:
                nec = '/config "{0}"'.format(self.nec)
            else:
                nec = ''
        except:
            print('could not parse encryption_pass') 
        
        try:
            if self.site_file == True:
                site_file = '/site '
            elif self.site_file:
                site_file = '/site "{0}"'.format(self.site_file)
            else:
                site_file = ''
        except:
            print('could not parse encryption_pass')

        try:
            rld_count = count_files(self.rld_dir, self.site_filter, 'rld')
            self.start_time = time.time()
            print('\nConverting {0} files from {1}\n'.format(rld_count, self.rld_dir))
            print('Saving outputs to {0}'.format(self.out_dir))

            cmd = [self.sympro_path, 
                   "/cmd", self.process_type, 
                   "/file", '"'+"\\".join([self.rld_dir, self.site_filter])+'*.rld"', 
                   encryption,
                   encryption_key,
                   nec,
                   site_file,  
                   "/type", '"'+self.convert_type+'"',
                   "/outputdir", '"'+self.out_dir[:-1]+'"'
            ]

            # print('\nUsing command line script:\n{}'.format(" ".join(cmd)))
            self.cmd = cmd
            
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
        """uses SymPRO utility NrgRldSiteSerialRename.exe to rename files with site number and logger serial number.
        
        This function is only compatible with Windows>=7 AND 
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

        try:
            if self.encryption_pass:
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ''
        except:
            print('could not parse encryption_pass')

        try:
            if self.hex_key:
                encryption_key = '/key "{0}"'.format(self.hex_key)
            else:
                encryption_key = ''
        except:
            print('could not parse hex_key')            

        try:
            if self.nec:
                nec = '/config "{0}"'.format(self.nec)
            else:
                nec = ''
        except:
            print('could not get nec file')

        try:
            if self.site_file:
                site_file = '/site "{0}"'.format(self.site_file)
            else:
                site_file = ''
        except:
            print('could not get site file')

        cmd = [self.sympro_path, 
                   "/cmd", "convert", 
                   "/file", '"'+self.filepath+'"', 
                   encryption,
                   encryption_key,
                   nec,
                   site_file,  
                   "/type", '"'+self.convert_type+'"',
                   "/outputdir", '"'+self.out_dir[:-1]+'"'
            ]
        self.cmd = cmd

        try:
            print("{0} ... \t\t".format(filepath), end="", flush=True)
            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            print("[DONE]")
        
        except:
            print("\n\t processing {0} [FAILED]".format(filepath))
            pass
        
        print("\nQueue processed\n")

class nrg_convert_api(object):
    """Uses NRG hosted web-based API to convert RLD files text format

    To sign up for the service, go to https://services.nrgsystems.com/
    
    Parameters
    ----------
    rld_dir : str
        path to rld file directory
    out_dir : str
        path to save text export files
    filename : str
        provide for single file conversion
    site_filter : str, optional
        text filter for limiting file set
    filter2 : str, optional
        another text filter...
    start_date : str, optional
        text start date to filter on "YYYY-mm-dd"
    end_date : str, optional
        text end date to filter on "YYYY-mm-dd"
    client_id : str
        provided by NRG Systems
    client_secret : str
        provided by NRG Systems
    token : str
        deprecated, for beta conversion service users
    encryption_pass : str, optional
        password for rld files (set in logger)
    header_type : str
        [standard], columnonly, or none
    nec_file : str, optional
        path to NEC file for custom export formatting
    export_type : str
        [meas], samples, diag, comm

    Examples
    --------
    Convert a single RLD file to Text with NRG Convert API

    >>> from nrgpy.convert_rld import nrg_convert_api
    >>> filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
    >>> txt_dir = "/home/user/data/sympro/000123/txt/"
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrg_convert_api(
            file_filter=file_filter, 
            filename=filename, 
            client_id=client_id,
            client_secret=client_secret,
        ) 

    Convert a folder of RLD files to Text with NRG Convert API

    >>> from nrgpy.convert_rld import nrg_convert_api
    >>> file_filter = "000175"
    >>> rld_directory = "rlds"
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> converter = nrg_convert_api(
            file_filter=file_filter, 
            rld_dir=rld_directory, 
            client_id=client_id,
            client_secret=client_secret,
            start_date="2020-01-01",
            end_date="2020-01-31",
        )
    >>> converter.process()    
    
    """
    def __init__(self, rld_dir='', out_dir='', filename='', site_filter='',
                 filter2 = '', start_date='1970-01-01', end_date='2150-12-31',
                 client_id='', client_secret='', token='', 
                 encryption_pass='', header_type='standard', nec_file='',
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
        
        self.filter2 = filter2
        self.start_date = start_date
        self.end_date = end_date
        self.header_type = header_type
        self.nec_file = nec_file
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        
        affirm_directory(self.out_dir)

        if self.client_id and self.client_secret:

            self.session_token, self.session_start_time = maintain_session_token(client_id=self.client_id, client_secret=self.client_secret)
        
            if self.session_token:
                self.convert_url = ConvertServiceUrl
            else:
                print("Unable to get session token for conversion")                

        else:
            self.convert_url = nrgApiUrl
            print("[Deprecation warning]\n------------------------------------------------------")
            print(" NRGPy Convert API will require a client_id and \n client_secret starting March 15, 2020.")
            print(" Please contact support@nrgsystems.com or visit \n https://services.nrgsystems.com to sign up.")
            print("------------------------------------------------------\n")            
    
        if len(tk) > 10 and len(self.token) < 10:
            self.token = tk

        if (not self.token) and (not self.client_id) and (not self.client_secret):
            print('[Access error] Valid credentials are required.\nPlease contact support@nrgsystems.com or visit \nhttps://services.nrgsystems.com for API access')

        if filename != '':
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar=False
            self.start_time = datetime.now()
            self.single_file(filename)


    def process(self, progress_bar=True):
        if self.client_id and self.client_secret:
            self.session_token, self.session_start_time = maintain_session_token(client_id=self.client_id, client_secret=self.client_secret)

        self.progress_bar = progress_bar
        self.start_time = datetime.now()
        
        self.files = [
            f for f in sorted(glob.glob(self.rld_dir + '*.rld'))\
            if self.site_filter in f and self.filter2 in f\
            and date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        
        for rld in self.files:
            self.single_file(rld)
            self.counter += 1

        print('\n')


    def convert(self):
        self.process()
    def directory(self):
        self.process()


    def single_file(self, rld):
        try:
            if self.progress_bar:
                draw_progress_bar(self.counter, self.raw_count, self.start_time)
            else:
                print("Processing {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad),str(self.raw_count).ljust(self.pad),os.path.basename(rld)), end="", flush=True)
        
            RldFileBytes = open(rld,'rb').read()
            EncodedFileBytes = base64.encodebytes(RldFileBytes)

            if self.convert_url == ConvertServiceUrl:
                # CONVERT 2.0
                if self.nec_file:
                    NecFile = open(self.nec_file,'rb').read()
                    NECFileBytes = base64.encodebytes(NecFile)
                else:
                    NECFileBytes = ''

                if not token_valid(self.session_start_time): self.session_token, self.session_start_time = request_session_token(self.client_id, self.client_secret)
                headers = {"Authorization": "Bearer {}".format(self.session_token)}

                self.Data = {
                            'filebytes': EncodedFileBytes,
                            'necfilebytes': NECFileBytes,
                            'headertype': self.header_type,     # standard | columnonly  | none
                            'exporttype': self.export_type,     # measurements (default) | samples
                            'exportformat': self.export_format, # csv_zipped (default)   | parquet
                            'encryptionkey': self.encryption_pass,
                            'columnheaderformat': '',           # not implemented yet
                        }             
                self.resp=requests.post(data=self.Data, url=self.convert_url, headers=headers)

            else:
                # BETA CONVERT
                Data = {'apitoken': self.token,
                        'encryptionpassword': self.encryption_pass,
                        'headertype': self.header_type, #standard | columnonly | none
                        'exportformat': self.export_format, # csv_zipped (default) | parquet
                        'filebytearray': EncodedFileBytes} 

                self.resp=requests.post(data=Data, url=self.convert_url)

            zippedDataFile = zipfile.ZipFile(io.BytesIO(self.resp.content))
            regDataFile = self.resp.content
            name = zippedDataFile.infolist().pop()
            outFileName =  "".join(rld.split(self.folder_split)[-1:])[:-4] + '_' + self.export_type +  '.txt'

            with open(os.path.join(self.out_dir, outFileName),'wb') as outputfile:
                outputfile.write(zippedDataFile.read(name))

            try:
                filename = os.path.join(self.out_dir, outFileName)
                fileContents = open(filename,"r").read()
                f = open(filename,"w", newline="\r\n")
                f.write(fileContents)
                f.close()
            except:
                print("Could not convert Windows newline characters properly; file may be unstable")

            if self.progress_bar == False: print("[DONE]")

        except Exception as e:
            if self.progress_bar == False: print("[FAILED]")
            print('unable to process file: {0}'.format(rld))
            print(e)
            print(str(self.resp.status_code) + " " + self.resp.reason + "\n")
            pass

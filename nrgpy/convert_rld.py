#!/bin/usr/python

import base64
import io
import glob
import os
import pandas as pd
from pathlib import Path
import requests
import subprocess
import zipfile

nrgApiUrl = 'https://services.nrgsystems.com/api/Convert?code=yafm/4r/axuaMMGTP9SkBRNrpmEhrrM4B4sU6ehrXDG6bJaMpFhbIg=='
tk = ''

class local(object):
    
    def __init__(self, rld_dir='', out_dir='', encryption_pass='',
                 sympro_path=r'"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"',
                 convert_type='meas', site_filter='', **kwargs):
        self.rld_dir = rld_dir.replace('/','\\')
        self.out_dir  = out_dir.replace('/','\\')
        self.encryption_pass = encryption_pass
        self.sympro_path = sympro_path
        self.convert_type = convert_type
        self.site_filter = site_filter
        if self.check_platform() == 'win32':
            pass
        else:
            print("""
            convert_rld.local() method ONLY compatible with Windows OS. 
            Please use convert_rld.nrg_convert_api() method instead.
            """)
        #self.directory()
        #self.single_file()
    
    def __info__(self):
        usage = """
        ------------------------------------------------------------------------------
        local(): 
        
        For handling NRG SymphoniePRO Data Logger raw data files in the *.rld format.
        This method uses locally installed SymphoniePRO Desktop software to convert
        *.rld files to txt format (tab-delimited-text).
        
        requirements:
            1. installation of SymphoniePRO Desktop Software on Windows 7 or later
            2. pandas >= v0.23 
            3. sympro_txt.py
        
        kwargs:
            1. rld_dir: default = '', or specify directory. Note for unc values, you 
                        will need to escape all forward slashes, e.g.
                        rld_dir = "\\\\sol\\techsupport\\data\\"
            2. out_dir: default = '', see note for 1.
            3. encryption_pass: default = '', specify data encryption password if logger is 
                        set up for that.
            4. sympro_path: default= "C:\Program Files (x86)\Renewable NRG Systems\SymPRO Desktop\SymPRODesktop.exe"
            5. convert_type: default='meas', alternately specify 'comm', 'diag', sample', or 'events'
            6. site_filter: default = '', or specify part or all of the file you'd like to
                        filter on. Eg. site_filter='123456_2018-09' would filter on site 123456
                        and only the month of September in 2018.
        
        functions:
            concat_txt(): combines all txt files in txt_dir (out_dir by default) that 
                        include self.site_filter into one txt file with header from first file.
                        out_file can be specified; defaults to %Y-%m-%d_SymPRO.txt in 
                        current directory.
            directory(): processes all rld files in self.rld_dir, outputs to txt files 
                        to out_dir
            info(): prints this message.
            rename_rld(): uses
            single_file(): pass single file's complete path for export.
        ------------------------------------------------------------------------------
        
        """
        print(usage)

    def check_platform(self):
        """
        determine which operating system python is running on
        """
        from sys import platform
        return(platform)
        
    def directory(self):
        """
        processes all rld files in self.rld_dir, outputs to txt files to out_dir
        """
        if os.path.exists(self.out_dir):
            pass
        else:
            try:
                print("output directory does not exist, creating...", end="", flush=True)
                os.makedirs(self.out_dir)
                print("[OK]")
            except:
                print('[FAILED]')
        file_filter = self.rld_dir + self.site_filter + '*' + '.rld'
        print(file_filter)
        try:
            if self.encryption_pass != '':
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ''
        except:
            print('could not parse encryption_pass')
        try:
            print('\nConverting files in {0}\n'.format(self.rld_dir))
            print('Saving outputs to {0}'.format(self.out_dir))
            cmd = [self.sympro_path, 
                   "/cmd", "convert", 
                   "/file", '"'+file_filter+'"', 
                   encryption,  
                   "/outputdir", '"'+self.out_dir[:-1]+'"'
            ]
            #print(" ".join(cmd))
            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            print('\nTXT files saved in {0}\n'.format(self.out_dir))
        except FileNotFoundError:
            print("""
                  No instance of SymphoniePRO Desktop Application found.

                  Please follow the link below to download and install this software:
                  https://www.nrgsystems.com/support/product-support/software/symphoniepro-desktop-application

                  """)
        except:
            print('Unable to process files in directory')

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
    def __init__(self, rld_dir='', out_dir='', site_filter='', encryption_pass='',
                 token='', header_type='standard', export_type='meas', 
                 export_format='csv_zipped', **kwargs):    
        if local.check_platform == 'win32':
            self.rld_dir = rld_dir.replace('/','\\')
            self.out_dir = out_dir.replace('/','\\')
        else:
            self.rld_dir = rld_dir.replace('\\','/')
            self.out_dir = out_dir.replace('\\','/')
        self.encryption_pass = encryption_pass
        self.export_format = export_format
        self.export_type = export_type
        self.site_filter = site_filter
        self.header_type = header_type
        self.token = token
        
        #import nrgApiUrl, token as tk
        self.NrgUrl = nrgApiUrl
        if len(tk) > 10 and len(self.token) < 10:
            self.token = tk
        if self.token == '':
            print('\n\nA valid token is required to use the nrg_convert_api.\nPlease contact support@nrgsystems.com for an API token')
#        self.process()

    def process(self):
        if os.path.exists(self.out_dir):
            pass
        else:
            try:
                print("output directory does not exist, creating...", end="", flush=True)
                os.makedirs(self.out_dir, exists_ok=True)
                print("[OK]")
            except:
                print('[FAILED]')

        filelist = sorted(glob.glob(self.rld_dir + self.site_filter + '*.rld'))
        #print(filelist)
        #print(self.rld_dir)
        for rld in filelist:
            try:
                print("Processing: {0} ... \t\t".format(rld), end="", flush=True)
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
                outFileName =  "".join(rld.split("\\")[-1:])[:-4] + '_' + self.export_type +  '.txt'

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
                print(str(self.resp.status_code) + " " + self.resp.reason + "\n"
                      + str(self.resp.content))
                pass

        print('\nQueue processed\n')

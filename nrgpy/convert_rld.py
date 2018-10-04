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


class local(object):
    
    def __init__(self, **kwargs):
        self.raw_dir = kwargs.get('raw_dir', '')
        self.out_dir  = kwargs.get('out_dir', '')
        self.password = kwargs.get('password', '')
        self.sympro_path = kwargs.get('sympro_path', r'"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"')
        self.convert_type = kwargs.get('convert_type', 'meas')
        self.filter = kwargs.get('filter', '')
        #self.directory()
        #self.single_file()
    
    def info(self):
        usage = """
        ------------------------------------------------------------------------------
        local(): 
        
        For handling NRG SymphoniePRO Data Logger raw data files in the *.rld format.
        This method uses locally installed SymphoniePRO Desktop software to convert
        *.rld files to txt format (tab-delimited-text).
        
        requirements:
            1. installation of SymphoniePRO Desktop Software on Windows 7 or later
            2. pandas
            3. sympro_txt.py
        
        kwargs:
            1. raw_dir: default = '', or specify directory. Note for unc values, you 
                        will need to escape all forward slashes, e.g.
                        raw_dir = "\\\\sol\\techsupport\\data\\"
            2. out_dir: default = '', see note for 1.
            3. password: default = '', specify data encryption password if logger is 
                        set up for that.
            4. sympro_path: default= "C:\Program Files (x86)\Renewable NRG Systems\SymPRO Desktop\SymPRODesktop.exe"
            5. convert_type: default='meas', alternately specify 'comm', 'diag', sample', or 'events'
            6. filter: default = '', or specify part or all of the file you'd like to
                        filter on. Eg. filter='123456_2018-09' would filter on site 123456
                        and only the month of September in 2018.
        
        functions:
            concat_txt(): combines all txt files in txt_dir (out_dir by default) that 
                        include self.filter into one txt file with header from first file.
                        out_file can be specified; defaults to %Y-%m-%d_SymPRO.txt in 
                        current directory.
            directory(): processes all rld files in self.raw_dir, outputs to txt files 
                        to out_dir
            info(): prints this message.
            rename_rld(): uses
            single_file(): pass single file's complete path for export.
        ------------------------------------------------------------------------------
        
        """
        print(usage)


    def directory(self):
        file_filter = self.raw_dir + self.filter + '*' + '.rld'
        print(file_filter)
        try:
            if self.password != '':
                encryption = "/pass {0}".format(self.password)
            else:
                encryption = ''
        except:
            print('could not parse password')
        try:
            print('\nConverting files in {0}\n'.format(self.raw_dir))
            cmd = [self.sympro_path, "/cmd", "convert", "/file", '"'+file_filter+'"', encryption,  "/outputdir", '"'+self.out_dir[:-1]+'"']
            #print(" ".join(cmd))
            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            print('\nTXT files saved in {0}\n'.format(self.out_dir))
        except:
            print('Whoops! something went wrong...')

    def rename_rlds(self, **kwargs):
        renamer_path = kwargs.get('renamer_path', r"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/Default Application Files/Utilities/NrgRldSiteSerialRename.exe")
        
        for f in os.listdir(self.raw_dir):
            filepath = self.raw_dir + f
            if f[-4:].lower()==".rld" and self.filter in f:
                rename_cmd = [renamer_path, '"'+filepath+'"']
                try:
                    subprocess.run(" ".join(rename_cmd), stdout=subprocess.PIPE)
                except:
                    print("Unable to rename {0}".format(f))
                    pass
                    
            else:
                pass
            

    def single_file(self, filepath=''):
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
        blah blah blah, michael should fill this out
    """
    def __init__(self, rld_dir='', out_dir='', filter='', encryption_pass='',
                 token='', headertype='columnonly', **kwargs):    
        self.rld_dir = rld_dir
        self.out_dir = out_dir
        self.filter = filter
        self.encryption_pass = encryption_pass
        self.token = token
        self.headertype = headertype
    
        self.NrgUrl = 'https://nrgconvert.azurewebsites.net/api/Convert?code=yafm/4r/axuaMMGTP9SkBRNrpmEhrrM4B4sU6ehrXDG6bJaMpFhbIg=='
#        self.process()

    def process(self):
        if os.path.exists(self.out_dir):
            pass
        else:
            try:
                print("output directory does not exist, creating...", end="", flush=True)
                os.makedirs(self.out_dir)
                print("[OK]")
            except:
                print('[FAILED]')

        filelist = glob.glob(os.path.join(self.rld_dir, self.filter + '*.rld'))
        for rld in filelist:
            try:
                print("Processing: {0} ... \t\t".format(rld), end="", flush=True)
                RldFileBytes = open(rld,'rb').read()
                EncodedFileBytes = base64.encodebytes(RldFileBytes)

                Data = {'apitoken': self.token,
                        'headertype': self.headertype, #standard | columnonly | none
                        'filebytearray': EncodedFileBytes} 

                self.resp=requests.post(data=Data, url=self.NrgUrl)

                zippedDataFile = zipfile.ZipFile(io.BytesIO(self.resp.content))
                regDataFile = self.resp.content

                name = zippedDataFile.infolist().pop()
                
                #zippedDataFile.extractall(path=self.out_dir)

                with open(os.path.join(self.out_dir, "".join(rld.split("/")[-1:])[:-4] + '.txt'),'wb') as outputfile:
                    outputfile.write(zippedDataFile.read(name))
                    #outputfile.write(regDataFile)
                print("[DONE]")

            except:
                print("[FAILED]")
                print('unable to process file: {0}'.format(rld))
                print(str(self.resp.status_code) + " " + self.resp.reason)
                pass

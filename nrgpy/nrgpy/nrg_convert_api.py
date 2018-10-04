#does not yet handle encrypted files

def nrg_convert_api(**kwargs):

    #imports
    import requests
    import base64
    import zipfile
    import io
    from pathlib import Path
    import os

    #kwargs
    filefilter = kwargs.get('filefilter', "")
    directory = kwargs.get('directory', os.getcwd())
    token = kwargs.get('token', "")
    
    #constants
    NrgUrl = 'https://nrgconvert.azurewebsites.net/api/Convert?code=yafm/4r/axuaMMGTP9SkBRNrpmEhrrM4B4sU6ehrXDG6bJaMpFhbIg=='
    
    pathlist = Path(directory).glob(filefilter + '*.rld')
    for rldFilePath in pathlist:
            sourceRld = str(rldFilePath)
            print("Processing: ", sourceRld)
            RldFileBytes = open(sourceRld,'rb').read()
            EncodedFileBytes = base64.encodebytes(RldFileBytes)

            Data = {'apitoken':token,
                    'headertype':'columnonly', #standard | columnonly | none
                    'filebytearray':EncodedFileBytes} 

            resp=requests.post(data=Data, url=NrgUrl)

            zippedDataFile = zipfile.ZipFile(io.BytesIO(resp.content))

            name = zippedDataFile.infolist().pop()
            with open(os.path.basename(rldFilePath)[:-4] + '.txt','wb') as outputfile:
                outputfile.write(zippedDataFile.read(name))

# <img alt="NRGPy" src="https://www.nrgsystems.com/mysite/images/logo.png?v=3" height="40">

NRGPy is the Python package for processing NRG Symphonie Data files

- Website and source: https://github.com/nrgpy/nrgpy
- Support: support@nrgsystems.com

It provides:

- Tools for converting binary ".rld" and ".rwd files to text format
    - using locally installed SymphoniePRO Desktop Software and Symphonie Data Retriever
    - using web api (compatible with Linux!) *(SymphoniePRO only at this time)
- Tools for reading text exports into Pandas dataframes
- Timestamp adjustment (of text files)

***
## Installation:

    pip install nrgpy

## Examples:

### RLD files

#### Convert a folder of RLD files to Text with SymphoniePRO Desktop Software:
```python
from nrgpy.convert_rld import local
date_filter = '2018-10' # filter on any text in the filenames
text_folder_name = 'text_outputs/'
fut = local(rld_dir='', out_dir=text_folder_name, site_filter=date_filter)
fut.directory()
```
#### Convert a folder of RLD files to Text with NRG Convert API
```python
from nrgpy.convert_rld import nrg_convert_api
site_filter = "000175"
rld_directory = "rlds"
token = "contact support@nrgsystems.com for token"
fut = nrg_convert_api(site_filter=site_filter, rld_dir=rld_directory, token=token)
fut.process()
```

#### Read files
```python
site_filter = "000175"
from nrgpy.sympro_txt import sympro_txt_read

sympro_dfs = sympro_txt_read()
sympro_dfs.concat_txt(txt_dir=text_folder_name, site_filter=site_filter, output_txt=False)
```

### RWD files

#### Convert a folder of RWD files to Text with Symphonie Data Retriever
```python
from nrgpy.convert_rwd import local
site_filter = '0434201902' # for Feb 2019 files from site 0434
rwd_directory = 'C:/Users/[user]/rwd/'
out_directory = 'C:/Users/[user]/txt/'


converter = local(site_filter=site_filter, rwd_dir=rwd_directory, out_dir=out_directory)
converter.convert()
```

#### Convert a folder of RWD files to Text with Symphonie Data Retriever _on Linux_
```python
from nrgpy.convert_rwd import local
rwd_directory = '/home/user/datafiles/rwd'
out_directory = '/home/user/datafiles/txt'
wine_directory = '/home/user/prefix32/drive_c/'


converter = local(site_filter=site_filter, 
                  rwd_dir=rwd_directory, 
                  out_dir=out_directory,
                  wine_folder=wine_directory,
                  )
converter.convert()
```
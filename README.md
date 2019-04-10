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
converter = local(rld_dir='', out_dir=text_folder_name, file_filter=date_filter)
converter.convert()
```
#### Convert a folder of RLD files to Text with NRG Convert API
```python
from nrgpy.convert_rld import nrg_convert_api
file_filter = "000175"
rld_directory = "rlds"
token = "contact support@nrgsystems.com for token"
converter = nrg_convert_api(file_filter=file_filter, rld_dir=rld_directory, token=token)
converter.convert()
```

#### Read files
```python
file_filter = "000175"
from nrgpy.sympro_txt import sympro_txt_read

sympro_dfs = sympro_txt_read()
sympro_dfs.concat_txt(txt_dir=text_folder_name, file_filter=file_filter, output_txt=False)
```

### RWD files

#### Convert a folder of RWD files to Text with Symphonie Data Retriever
```python
from nrgpy.convert_rwd import local
file_filter = '0434201902' # for Feb 2019 files from site 0434
rwd_directory = 'C:/Users/[user]/rwd/'
out_directory = 'C:/Users/[user]/txt/'


converter = local(file_filter=file_filter, rwd_dir=rwd_directory, out_dir=out_directory)
converter.convert()
```

#### Convert a folder of RWD files to Text with Symphonie Data Retriever _on Linux_
```python
from nrgpy.convert_rwd import local
rwd_directory = '/home/user/datafiles/rwd'
out_directory = '/home/user/datafiles/txt'
wine_directory = '/home/user/.wine/drive_c/' # path to wine's "C:\" drive
use_site_file = False # set to True to use local site file for scaling and headers


converter = local(file_filter=file_filter, 
                  rwd_dir=rwd_directory, 
                  out_dir=out_directory,
                  wine_folder=wine_directory,
                  use_site_file=use_site_file
                  )
converter.convert()
```


You can also convert a single file with SDR, and save it in the same directory:

```python
from nrgpy.convert_rwd import local
filename = '/path/to/file'
converter = local(filename=filename)
```

#### Read TXT files exported from RWD files

```python
from nrgpy.txt_utils import read_text_data
dt = 'rwd'
txt_file = '/path/to/file.txt'
reader = read_text_data(data_type=dt, filename=txt_file)
```

or concatenate a whole lot of files:

```python
dt = 'rwd'
txt_dir = '/path/to/text/files'
file_filter = 'text_in_filenames_you_want'
reader = read_text_data(data_type=dt, txt_dir=txt_dir, file_filter=file_filter)
reader.concat()
```

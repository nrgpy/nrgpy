# <img alt="NRGPy" src="https://www.nrgsystems.com/mysite/images/logo.png?v=3" height="40">

NRGPy is the Python package for processing NRG Data files

- Website and source: https://github.com/nrgpy/nrgpy
- Support: support@nrgsystems.com

It provides tools for:

- Converting binary ".rld" and ".rwd files to text format
    - using locally installed SymphoniePRO Desktop Software and Symphonie Data Retriever
    - using web api (compatible with Linux!) *(SymphoniePRO only at this time)
- Reading Symphonie text exports into Pandas dataframes
- Reading Spidar zip/csv files into Pandas dataframes
- Timestamp adjustment (of text files)
- Simple quality checks on data

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

#### Convert a single RLD file to Text with NRG Convert API
```python
from nrgpy.convert_rld import nrg_convert_api
filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
token = "contact support@nrgsystems.com for token"
txt_dir = "/home/user/data/sympro/000123/txt/"
converter = nrg_convert_api(token=token, filename=filename, out_dir=txt_dir)
```

#### Read files
```python
file_filter = "000175"
from nrgpy.sympro_txt import sympro_txt_read

sympro_dfs = sympro_txt_read()
sympro_dfs.concat_txt(txt_dir=text_folder_name, file_filter=file_filter, output_txt=False)
```

#### Read with more options...
```python
from nrgpy.sympro_txt import sympro_txt_read

sympro_dfs = sympro_txt_read()
sympro_dfs.concat_txt(
    txt_dir=text_folder_name, 
    file_filter="000175", 
    start_date="2019-10-01",
    end_date="2019-10-31",
    ch_details=True,
    output_txt=True,
    output_file="000175_2019_October_Data.txt"
)
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
wine_directory = '/home/user/prefix32/drive_c/' # path to wine's "C:\" drive


converter = local(file_filter=file_filter, 
                  rwd_dir=rwd_directory, 
                  out_dir=out_directory,
                  wine_folder=wine_directory,
                  use_site_file=False # set to True to use site files
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


### Spidar files
Spidar Vertical Profiler remote sensors generate archived csv data files.

 CSV archived in a Zip format.

These can be read directly into the spidar_txt_read method. See the docstring in 
spidar_txt.py for more information.

Eg.
``` python
In [1]: from nrgpy.spidar_txt import spidar_data_read                                                                          

In [2]: fname = "/spidar/1922AG7777_CAG70-SPPP-LPPP_NRG1_AVGWND_2019-07-07_1.zip"                            

In [3]: reader = spidar_data_read(filename=fname)                                                                              

In [4]: reader.heights                                                                                                         
Out[4]: [40, 60, 80, 90, 100, 120, 130, 160, 180, 200]

In [5]: reader.data                                                                                                            
Out[5]: 
                     pressure[mmHg]  temperature[C]  ...  dir_200_std[Deg]  wind_measure_200_quality[%]
Timestamp                                            ...                                               
2019-07-06 23:40:00          749.66           24.13  ...             28.77                           68
2019-07-06 23:50:00          749.63           24.08  ...             14.31                            0
2019-07-07 00:00:00          749.64           23.99  ...             20.59                            0
...
```
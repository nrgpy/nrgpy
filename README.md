# ![NRGPy](https://www.gravatar.com/avatar/6282094b092c756acc9f7552b164edfe?s=24) nrgpy

**nrgpy** is the Python package for processing NRG Data Files

- Website and source: https://github.com/nrgpy/nrgpy
- Documentation: https://nrgpy.github.io/nrgpy/
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
## Installation

    pip install nrgpy

## Examples

### RLD files

#### Convert a folder of RLD files to Text with SymphoniePRO Desktop Software

```python
import nrgpy
date_filter = '2018-10' # filter on any text in the filenames
text_folder_name = 'text_outputs/'
converter = nrgpy.local_rld(rld_dir='', out_dir=text_folder_name, file_filter=date_filter)
converter.convert()
```

#### Convert a folder of RLD files to Text with NRG Convert API

```python
import nrgpy
file_filter = "000175"
rld_directory = "rlds"
client_id = "contact support@nrgsystems.com for access"
client_secret = "contact support@nrgsystems.com for access"
converter = nrgpy.nrg_api_convert(
    file_filter=file_filter, 
    rld_dir=rld_directory, 
    client_id=client_id,
    client_secret=client_secret,
    start_date="2019-11-01",
    end_date="2019-11-30",
)
converter.process()
```

#### Convert a single RLD file to Text with NRG Convert API
```python
import nrgpy
filename = "/home/user/data/sympro/000123/000123_2019-05-23_19.00_003672.rld
txt_dir = "/home/user/data/sympro/000123/txt/"
client_id = "contact support@nrgsystems.com for access"
client_secret = "contact support@nrgsystems.com for access"
converter = nrgpy.nrg_api_convert(
    file_filter=file_filter, 
    filename=filename, 
    client_id=client_id,
    client_secret=client_secret,
)
```

#### Read files
```python
file_filter = "000175"
import nrgpy

reader = nrgpy.sympro_txt_read()
reader.concat_txt(
    txt_dir=text_folder_name, 
    file_filter=file_filter, 
    start_date="2019-11-01",
    end_date="2019-11-30",
)
```

#### Read with more options...
```python
import nrgpy

reader = nrgpy.sympro_txt_read()
reader.concat_txt(
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
import nrgpy

file_filter = '0434201902' # for Feb 2019 files from site 0434
rwd_directory = 'C:/Users/[user]/rwd/'
out_directory = 'C:/Users/[user]/txt/'

converter = nrgpy.local_rwd(file_filter=file_filter, rwd_dir=rwd_directory, out_dir=out_directory)
converter.convert()
```

#### Convert a folder of RWD files to Text with Symphonie Data Retriever _on Linux_
```python
import nrgpy

rwd_directory = '/home/user/datafiles/rwd'
out_directory = '/home/user/datafiles/txt'
wine_directory = '/home/user/prefix32/drive_c/' # path to wine's "C:\" drive


converter = nrgpy.local_rwd(
                file_filter=file_filter, 
                rwd_dir=rwd_directory, 
                out_dir=out_directory,
                wine_folder=wine_directory,
                use_site_file=False # set to True to use site files
            )
converter.convert()
```


You can also convert a single file with SDR, and save it in the same directory:

```python
import nrgpy

filename = '/path/to/file'
converter = nrgpy.local_rwd(filename=filename)
```

#### Read TXT files exported from RWD files

```python
import nrgpy

dt = 'rwd'
txt_file = '/path/to/file.txt'
reader = nrgpy.read_text_data(data_type=dt, filename=txt_file)
```

or concatenate a whole lot of files:

```python
dt = 'rwd'
txt_dir = '/path/to/text/files'
file_filter = 'text_in_filenames_you_want'
reader = nrgpy.read_text_data(data_type=dt, txt_dir=txt_dir, file_filter=file_filter)
reader.concat()
```


### Spidar files
Spidar Vertical Profiler remote sensors generate archived csv data files.

 CSV archived in a Zip format.

These can be read directly into the spidar_txt_read method. See the docstring in 
spidar_txt.py for more information.

Eg.
``` python
In [1]: import nrgpy

In [2]: fname = "/spidar/1922AG7777_CAG70-SPPP-LPPP_NRG1_AVGWND_2019-07-07_1.zip"                            

In [3]: reader = nrgpy.spidar_data_read(filename=fname)                                                                              

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

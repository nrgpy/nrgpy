<img alt="NRGPy" src="https://www.nrgsystems.com/mysite/images/logo.png?v=3" height="">

# Symphonie Data Retriever | Convert files on Linux

**Summary** <br>
The following is an example of how to convert RWD raw wind data files from Symphonie loggers to TXT format by using WINE on Ubuntu 18.04 Linux. Steps for other distros should be quite similar. 


Note that this process requires the presense of an x-environment (GUI). The SDR installation will not complete without a graphical environment.
<br><br>
**Steps** <br>

1. Install WINE <br>
    `sudo apt install wine-stable winetricks` <br><br>
1. Download Symphonie Data Retriever installation media <br>
    `wget https://www.nrgsystems.com/assets/software-downloads/5570-SDR-7.08.18.exe` <br><br>
1. Configure 32-bit wine prefix <br>
    `export WINEPREFIX="/home/$USER/prefix32"` <br>
    `export WINEARCH=win32` <br><br>
1. Install the software <br>
    `wine 5570-SDR-7.08.18.exe` <br>
    `#accept all defaults` <br>
    `winetricks jet40`<br><br>
    `#accept all defaults` <br>
1. Copy RWD files to `~/prefix32/drive_c/NRG/RawData/` folder <br>
    `cp /path-to-data-files/*RWD ~/prefix32/drive_c/NRG/RawData/`<br>
    `cd ~/prefix32/drive_c/NRG/SymDR/` <br><br>
1. Use 'No Queue' mode to process RWD files into Text files without requiring a site file. The RWD file must be called referencing C:\\NRG\\... Exports of single files will land in `~/.wine/drive_c/NRG/ScaledData/` note that the backslashes must be escaped as in: <br>
`user@ubuntu:~/prefix32/drive_c/NRG/SymDR$ wine SDR.exe /q C:\\NRG\\RawData\\009620160210021.RWD` <br><br>
1. If the file uses an encryption pin, use /z mode <br>
    `wine SDR.exe /z 1234 ...`<br><br>
1. To iterate through all files for a particular site in the RawData directory, use a for loop like:
    ```bash
    for filename in ../RawData/0096*RWD; do
        wine SDR.exe /q C:\\NRG\\RawData\\"$filename";
    done
    ```
    Note that in this case, the txt files will land in the RawData folder

### Reading file with Python Pandas:
``` python
import pandas as pd
rwd_data = pd.read_csv(
                '/home/user/.wine/drive_c/NRG/ScaledData/009620160210021.txt', 
                 skiprows=170, 
                 sep='\t')
```
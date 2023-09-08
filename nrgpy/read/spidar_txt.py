from datetime import datetime
from glob import glob
import os
from nrgpy.utils.utilities import (
    check_platform,
    windows_folder_path,
    linux_folder_path,
    string_date_check,
    draw_progress_bar,
)
import pandas as pd


class SpidarRead:
    """reads in CSV file(s) using pandas and creates

    Parameters
    ----------
    data_file : str
        path to single CSV or ZIP to be read

    Returns
    --------
    data : obj
        pandas dataframe of all available data
    heights : list
        list of measurement heights

    Examples
    ----------
    Read a spidar data file into an object:

    >>> import nrgpy
    >>> reader = nrgpy.spidar_data_read(filename="1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-04_1.zip")
    >>> reader.heights
    ['40', '60', '80', '90', '100', '120', '130', '160', '180', '200']

    >>> reader.data
            Timestamp  pressure[mmHg]  temperature[C]  ...  dir_200_mean[Deg]  dir_200_std[Deg]  wind_measure_200_quality[%]
    0   2019-07-03 23:40:00          753.55           23.68  ...             342.36             63.63                           48
    1   2019-07-03 23:50:00          753.47           23.76  ...             345.70             57.59                           38
    2   2019-07-04 00:00:00          753.46           23.96  ...             314.16             82.73                           20
    ...

    Ex. read a directory of spidar data files into an object:

    >>> reader = nrgpy.spidar_data_read()
    >>> reader.concat_txt(
            txt_dir="/path/to/spidardata/",
            file_filter="2020-01",
            progress_bar=False
        )
    Adding 1/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-01_1.zip [OK]
    Adding 2/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-01_2.csv [OK]
    Adding 3/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-02_1.zip [OK]
    Adding 4/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-03_1.zip [OK]
    Adding 5/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-04_1.zip [OK]
    Adding 6/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-05_1.zip [OK]
    Adding 7/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-06_1.zip [OK]
    Adding 8/8  ...  /home/user/spidardata/1922AG0070_CAG70-SPPP-LPPP_PENT_AVGWND_2019-07-07_1.zip [OK]
    >>> reader.serial_number
    '1922AG0070'
    """

    def __init__(self, filename=""):
        self.filename = filename
        self.reader_type = "SpidarV1"

        if self.filename:
            self.read_file(self.filename)
            pass

    def __repr__(self):
        return "<class {}: {} >".format(self.__class__.__name__, self.filename)

    def read_file(self, f):
        try:
            self.data = pd.read_csv(
                f, encoding="UTF_16_LE", parse_dates=True, index_col=[0]
            )
        except UnicodeDecodeError:
            self.data = pd.read_csv(
                f, encoding="UTF_8", parse_dates=True, index_col=[0]
            )

        self.data.reset_index(drop=False, inplace=True)
        self.columns = self.data.columns
        self.get_heights()
        self.serial_number = os.path.basename(f).split("_")[0]

    def concat_txt(
        self,
        txt_dir="",
        output_txt=False,
        out_file="",
        file_filter="",
        file_filter2="",
        start_date="1970-01-01",
        end_date="2150-12-31",
        progress_bar=True,
    ):
        """concatenate files in a folder

        parameters
        ----------
        txt_dir : str (path-like)
            path to csv or csv.zip files
        output_txt : boolean
            export concatenated data
        out_file : str
            optional, filename of text export
        start_date : str
            yyy-mm-dd formatted string
        end_date : str
            yyy-mm-dd formatted string
        progress_bar : boolean
            show progress bar instead of each file being concatenated

        returns
        -------
        None
            adds data dataframe to reader object
        """
        self.txt_dir = txt_dir
        self.output_txt = output_txt
        self.out_file = out_file
        self.file_filter = file_filter
        self.file_filter2 = file_filter2
        self.start_date = start_date
        self.end_date = end_date

        if check_platform() == "win32":
            self.txt_dir = windows_folder_path(txt_dir)
        else:
            self.txt_dir = linux_folder_path(txt_dir)

        first_file = True
        files = [
            f
            for f in sorted(glob(self.txt_dir + "*"))
            if self.file_filter in f
            and self.file_filter2 in f
            and string_date_check(self.start_date, self.end_date, f)
        ]

        self.file_count = len(files)
        self.pad = len(str(self.file_count))
        self.counter = 1
        self.start_time = datetime.now()

        for f in files:
            if self.file_filter in f and self.file_filter2 in f:
                if progress_bar:
                    draw_progress_bar(self.counter, self.file_count, self.start_time)
                else:
                    print(
                        "Adding {0}/{1}  ...  {2} ".format(
                            str(self.counter).rjust(self.pad),
                            str(self.file_count).ljust(self.pad),
                            f,
                        ),
                        end="",
                        flush=True,
                    )
                if first_file:
                    first_file = False
                    try:
                        base = spidar_data_read(f)
                        if not progress_bar:
                            print("[OK]")
                        pass
                    except IndexError:
                        print("Only standard Spidar headertypes accepted")
                        break
                else:
                    file_path = f
                    try:
                        s = spidar_data_read(file_path)
                        base.data = base.data.append(s.data, sort=False)
                        if not progress_bar:
                            print("[OK]")
                    except Exception as e:
                        if not progress_bar:
                            print("[FAILED]")
                        print("could not concat {0}".format(file_path))
                        print(e)
                        pass
            else:
                pass
            self.counter += 1

        if out_file != "":
            self.out_file = out_file
        if output_txt:
            base.data.to_csv(txt_dir + out_file, sep=",", index=False)

        try:
            self.base = base
            self.heights = base.heights
            self.serial_number = base.serial_number
            self.data = base.data.drop_duplicates(subset=["Timestamp"], keep="first")
            self.data.reset_index(drop=True, inplace=True)
            self.data.reset_index(drop=True, inplace=True)

        except Exception as e:
            print("No files match to contatenate.")
            print(e)
            return None

    def get_heights(self):
        self.heights = [
            int(col.split("_")[1])
            for col in self.columns
            if "horz_mean" in col and "m/s" in col
        ]


spidar_data_read = SpidarRead
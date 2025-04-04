try:
    from nrgpy import log
except ImportError:
    pass
from datetime import datetime, timedelta
from glob import glob
import os
import re
import pandas as pd
from nrgpy.common.enums import LoggerModel
from nrgpy.utils.utilities import (
    check_platform,
    locate_text_in_df_column,
    windows_folder_path,
    linux_folder_path,
    draw_progress_bar,
    string_date_check,
    renamer,
)


class LogrRead:
    def __init__(
        self,
        filename: str = "",
        out_file: str = "",
        text_timestamps: bool = False,
        logger_local_time: bool = False,
        **kwargs,
    ):
        """Class of Pandas dataframes created from LOGR data files.

        If a filename is passed when calling class, the file is read in alone.
        Otherwise, an instance of the class is created, and the concat_txt function may
        be called to combine all txt files in a directory.

        Filters may be used on any part of the filename, to combine a subset of dat
        files in a directory.

        Parameters
        ----------
        filename : str, optional
            path to filename
        out_file : str, optional
            path to outputted file
        text_timestamps : boolean
            set to True for text timestamps
        logger_local_time : boolean
            (True) convert dat file UTC timestamps to logger local time

        Returns
        ---------
        ch_info : obj
            pandas dataframe of ch_list (below) pulled out of file with
            logr_read.arrange_ch_info()
        ch_list : list
            list of channel info; can be converted to json w/ import json ...
            json.dumps(fut.ch_info)
        data : obj
            pandas dataframe of all data
        head : obj
            lines at the top of the txt file..., used when rebuilding timeshifted files
        site_info : obj
            pandas dataframe of site information
        logger_sn : str
        logger_type : str
        latitude : float
        longitude : float
        elevation : int
        site_description : str
        start_date : str
        """
        self.filename = filename
        self.text_timestamps = text_timestamps
        self.out_file = out_file
        self.logger_local_time = logger_local_time
        self.reader_type = "LOGR"

        if out_file == "":
            out_file = datetime.today().strftime("%Y-%m-%d") + "_LOGR.dat"

        if self.filename:
            self.process_file()

    def process_file(self) -> None:
        i = 0
        self.set_timestamp_col()
        with open(self.filename) as infile:
            for line in infile:
                if line == "Data\n":
                    break
                else:
                    i = i + 1
        with open(self.filename) as myfile:
            self.head = "".join([myfile.readline() for _ in range(2)])

        header_len = i + 1
        read_len = header_len - 5
        self.site_info = pd.read_csv(
            self.filename,
            skiprows=2,
            sep="\t",
            index_col=False,
            nrows=read_len,
            usecols=[0, 1],
            header=None,
        )
        self.site_info = self.site_info.iloc[
            : self.site_info.loc[self.site_info[0] == "Data"].index.tolist()[0] + 1
        ]
        self.format_site_data()
        self.create_data_df(header_len)
        if str(self.filename).lower().endswith("dat"):
            self.arrange_ch_info()

    def set_timestamp_col(self) -> None:
        if self.filename.lower().endswith("diag"):
            self.timestamp_col = "Stats_Timestamp"
        else:
            self.timestamp_col = "Timestamp"

    def create_data_df(self, header_len: int) -> None:
        self.suffix = str(self.filename).lower().split(".")[-1]
        if self.suffix == "log":
            try:
                if self.logger_model in LoggerModel.LOGR_SOLAR.value:
                    self.data = pd.read_csv(
                        self.filename,
                        names=logr_log_columns,
                        skiprows=header_len,
                        sep=",",
                        encoding="iso-8859-1",
                     )
                else:
                    self.data = pd.read_csv(
                        self.filename,
                        names=logr_log_columns,
                        skiprows=header_len,
                        sep="\t",
                        encoding="iso-8859-1",
                    )

                self.first_timestamp = self.data.iloc[0][self.timestamp_col]
            except IndexError:
                pass
        elif self.suffix == "diag":
            try:
                self.data = pd.read_csv(
                    self.filename,
                    # names=logr_diag_columns,
                    skiprows=header_len,
                    sep="\t",
                    encoding="iso-8859-1",
                )
                self.first_timestamp = self.data.iloc[0][self.timestamp_col]
            except IndexError:
                pass
        else:
            self.data = pd.read_csv(
                self.filename, skiprows=header_len, sep="\t", encoding="iso-8859-1"
            )
            self.format_timestamps()
            self.first_timestamp = self.data.iloc[0][self.timestamp_col]

    def format_timestamps(self) -> None:
        if not self.text_timestamps:
            self.data[self.timestamp_col] = pd.to_datetime(self.data[self.timestamp_col])
        if self.logger_local_time and not self.text_timestamps:
            self.data["TimestampUTC"] = self.data[self.timestamp_col]
            self.data[self.timestamp_col] = self.data["TimestampUTC"] + timedelta(
                hours=int(self.time_zone)
            )
        elif self.logger_local_time and self.text_timestamps:
            print("Cannot convert timestamps to local if using text_timestamps==True")
            log.error(
                "Cannot convert timestamps to local if using text_timestamps==True"
            )

    def __repr__(self):
        return "<class {}: {} >".format(self.__class__.__name__, self.filename)

    def arrange_ch_info(self) -> None:
        """creates ch_info dataframe and ch_list array"""

        # correction for calculated channel colon missing
        def return_channel_number(x: pd.Series) -> int:
            """temporary fix for missing colon on dat file Channel key"""
            if pd.isnull(x["Channel:"]):
                return x["Channel"]
            else:
                return x["Channel:"]

        array = [
            "Channel:",
            "Channel",  # <--- fix for missing colon in dat file Channel key
            "Sensor Type:",
            "Description:",
            "Serial Number:",
            "Measurand:",
            "Height:",
            "Bearing:",
            "Scale Factor:",
            "Offset:",
            "Units:",
            "Vane Mounting Angle:",
            "Gust Source Channel:",
        ]

        self.array = array
        self.ch_info = pd.DataFrame()
        ch_data = {}
        ch_list = []
        ch_details = 0

        for row in self.site_info.loc[self.site_info[0].isin(array)].iterrows():
            if (
                row[1][0] in (array[0], array[1]) and ch_details == 0
            ):  # start channel data read
                ch_details = 1
                ch_data[row[1][0]] = row[1][1]

            elif (
                row[1][0] in (array[0], array[1]) and ch_details == 1
            ):  # close channel, start new data read
                ch_list.append(ch_data)
                ch_data = {}
                ch_data[row[1][0]] = row[1][1]

            elif row[1][0] in str(array):
                ch_data[row[1][0]] = row[1][1]

        ch_list.append(ch_data)  # last channel's data
        ch_df = pd.DataFrame(ch_list)

        self.ch_list = ch_list
        self.ch_info = pd.concat(
            [self.ch_info, ch_df], ignore_index=True, axis=0, join="outer"
        )

        self.ch_info["Channel:"] = self.ch_info.apply(
            lambda x: return_channel_number(x), axis=1
        )

    def format_site_data(self) -> None:
        """take dat header to create oject data"""
        try:
            self.Site_info = self.site_info.copy()
            self._site_info = self.Site_info.T
            self._site_info.columns = self._site_info.iloc[0]
            self._site_info.columns = self._site_info.iloc[0]
            self._site_info = self._site_info[1:]

            try:
                width = list(self._site_info.columns.values).index("Sensor History")
                self._site_info = self._site_info.iloc[:, :width]
            except (
                ValueError
            ):  # allows for parsing site info in diagnostic & events export,
                # which don't have sensor history
                pass

            self._site_info.rename(columns=renamer(), inplace=True)
            self._site_info.columns = [
                str(col).replace(":", "").strip() for col in self._site_info.columns
            ]

            self.latitude = float(self._site_info["Latitude"].values[0])
            self.longitude = float(self._site_info["Longitude"].values[0])
            self.elevation = int(self._site_info["Elevation"].values[0])
            self.location = self._site_info["Location"].values[0]
            self.project = self._site_info["Project"].values[0]
            self.site_description = self._site_info["Site"].values[0]

            self.logger_sn = self._site_info["Serial Number"].values[0]
            self.site_number = self.logger_sn
            self.logger_type = self._site_info["Model Number"].values[0]
            self.logger_model = self.logger_type
            self.time_zone = self._site_info["Time Zone"].values[0]

            try:
                self.ftp_fw_version = self._site_info["FTP FW Version"].values[0]
                self.created_fw_version = self._site_info["Created FW Version"].values[
                    0
                ]
            except KeyError:
                self.ftp_fw_version = self._site_info["FW Version"].values[0]
                self.created_fw_version = None
            # self.ch_info.drop(columns=['Channel'], inplace=True)

        except Exception as e:
            self.e = e
            print("Warning: error processing site_info: {}".format(e))
            log.exception(f"Cannot parse site info: {e}")

    def concat_txt(
        self,
        dat_dir: str = "",
        file_type: str = "statistical",
        file_filter: str = "",
        filter2: str = "",
        start_date: str = "1970-01-01",
        end_date: str = "2150-12-31",
        ch_details: bool = False,
        output_txt: bool = False,
        out_file: str = "",
        progress_bar: bool = True,
        drop_duplicates: bool = True,
        **kwargs,
    ):
        """Will concatenate all text files in the dat_dir

        files must match the site_filter argument. Note these are both blank by default.

        Parameters
        ----------
        dat_dir : str (path-like)
            directory holding txt files
        file_type : str
            type of export (meas, event, comm, sample, etc...)
        file_filter : str
            text filter for txt files, like site number, etc.
        filter2 : str
            secondary text filter
        start_date : str
            for filtering files to concat based on date "YYYY-mm-dd"
        end_date : str
            for filtering files to concat based on date "YYYY-mm-dd"
        ch_details : bool
            show additional info in ch_info dataframe
        output_txt : bool
            create a txt output of data df
        out_file : str
            filename to write data dataframe too if output_txt = True
        progress_bar : bool
            show bar on concat [True] or list of files [False]
        drop_duplicates : bool
            drop duplicate timestamps [True] or leave duplicates [False]

        Returns
        -------
        ch_info : obj
            pandas dataframe of ch_list (below) pulled out of file with
            logr_read.arrange_ch_info()
        ch_list : list
            list of channel info; can be converted to json w/ import json ...
            json.dumps(fut.ch_info)
        data : obj
            pandas dataframe of all data
        head : obj
            lines at the top of the txt file..., used when rebuilding timeshifted files
        site_info : obj
            pandas dataframe of site information
        logger_sn : str
        ipack_sn : str
        logger_type : str
        ipack_type : str
        latitude : float
        longitude : float
        elevation : int
        site_number : str
        site_description : str
        start_date : str
        dat_file_names : list
            list of files included in concatenation

        Examples
        --------
        Read files into nrgpy reader object

        >>> import nrgpy
        >>> reader = nrgpy.logr_read()
        >>> reader.concat_txt(
                dat_dir='/path/to/dat/files/',
                file_filter='123456', # site 123456
                start_date='2020-01-01',
                end_date='2020-01-31',
            )
        Time elapsed: 2 s | 33 / 33 [=============================================] 100%
        Queue processed
        >>> reader.logger_sn
        '511'
        >>> reader.ch_info
                Channel: 	Description: 	Offset:	Scale Factor: 	Serial Number: 	Type: 	Units:
        0 	1 	        NRG S1 	        0.13900 	0.09350 	94120000059 	Anemometer 	m/s
        1 	2 	        NRG S1 	        0.13900 	0.09350 	94120000058 	Anemometer 	m/s
        2 	3 	        NRG S1 	        0.13900 	0.09350 	94120000057 	Anemometer 	m/s
        3 	4 	        NRG 40C Anem 	0.35000 	0.76500 	179500324860 	Anemometer 	m/s
        4 	5 	        NRG 40C Anem 	0.35000 	0.76500 	179500324859 	Anemometer 	m/s
        5 	6 	        NRG S1 	        0.13900 	0.09350 	94120000056 	Anemometer 	m/s
        6 	13 	        NRG 200M Vane 	-1.46020 	147.91100 	10700000125 	Vane        Deg
        7 	14 	        NRG 200M Vane 	-1.46020 	147.91100 	10700000124 	Vane        Deg
        8 	5 	        NRG T60 Temp 	-40.85550 	44.74360 	9400000705      Analog      C
        9 	6 	        NRG T60 Temp 	40.85550 	44.74360 	9400000xxx      Analog      C
        10 	7 	        NRG RH5X Humi 	0.00000 	20.00000 	NaN 	        Analog      %RH
        11 	0 	        NRG BP60 Baro 	95.27700 	243.91400 	NaN 	        Analog      hPa
        12 	1 	        NRG BP60 Baro 	95.04400 	244.23900 	9396FT1937      Analog  	hPa
        """

        if "site_filter" in kwargs and file_filter == "":
            self.file_filter = kwargs.get("site_filter")
        else:
            self.file_filter = file_filter

        self.ch_details = ch_details
        self.start_date = start_date
        self.end_date = end_date
        self.filter2 = filter2
        self.file_type = file_type
        self.dat_file_names = []

        if "txt_dir" in kwargs and not dat_dir:
            dat_dir = kwargs.get("txt_dir")  # type: ignore

        if check_platform() == "win32":
            self.dat_dir = windows_folder_path(dat_dir)
        else:
            self.dat_dir = linux_folder_path(dat_dir)

        first_file = True

        files = self.get_filtered_file_list()

        self.file_count = len(files)
        self.pad = len(str(self.file_count))
        self.counter = 1
        self.start_time = datetime.now()
        self.failed_files = []

        log.info(f"Concatenating {self.file_count} files...")

        for f in files:
            if progress_bar:
                draw_progress_bar(self.counter, self.file_count, self.start_time)
            else:
                print(
                    "Adding {0}/{1} ... {2} ... ".format(
                        str(self.counter).rjust(self.pad),
                        str(self.file_count).ljust(self.pad),
                        os.path.basename(f),
                    ),
                    end="",
                    flush=True,
                )

            if first_file:
                first_file = False

                try:
                    self.base = LogrRead(
                        f,
                        text_timestamps=self.text_timestamps,
                        logger_local_time=self.logger_local_time,
                    )
                    self.timestamp_col = self.base.timestamp_col
                    if not progress_bar:
                        print("[OK]")
                    self.dat_file_names.append(os.path.basename(f))
                except IndexError:
                    print("Only standard LOGR headertypes accepted")
                    break
                except Exception:
                    if not progress_bar:
                        print("[FAILED]")
                    # print("could not concat {0}".format(os.path.basename(f)))
                    log.exception("could not concat {0}".format(os.path.basename(f)))
                    break
            else:
                try:
                    s = LogrRead(
                        f,
                        text_timestamps=self.text_timestamps,
                        logger_local_time=self.logger_local_time,
                    )
                    self.base.data = pd.concat(
                        [self.base.data, s.data], ignore_index=True, axis=0, join="outer"
                    )
                    if not str(s.filename).lower().endswith(("log", "diag")):
                        self.base.ch_info = pd.concat(
                            [self.base.ch_info, s.ch_info],
                            ignore_index=True,
                            axis=0,
                            join="outer",
                        )
                    if not progress_bar:
                        print("[OK]")
                    self.dat_file_names.append(os.path.basename(f))

                except Exception:
                    log.exception(f"could not concat {os.path.basename(f)}")
                    self.failed_files.append(f)
                    if not progress_bar:
                        print("[FAILED]")
                    print("could not concat {0}".format(os.path.basename(f)))
                    pass

            self.counter += 1

        self.data = self.base.data.copy()

        if out_file != "":
            self.out_file = out_file

        try:
            if str(self.dat_file_names[-1]).lower().endswith("dat"):
                self.ch_info = s.ch_info
                self.ch_list = s.ch_list
                self.site_info = s.site_info
                self.array = s.array

                self.data.reset_index(drop=True, inplace=True)
                self.base.ch_info["ch"] = self.base.ch_info["Channel:"].astype(int)

                try:
                    self.ch_info = (
                        self.base.ch_info.sort_values(by=["ch"])
                        .drop_duplicates(
                            subset=[
                                col for col in self.array if col in self.base.ch_info.columns
                            ],
                            ignore_index=True,
                        )
                        .drop(columns=["ch", "Channel"], axis=1, errors="ignore")
                    )
                except Exception:
                    log.exception("could not sort ch_info")
            else:
                self.site_info = self.base.site_info

            if drop_duplicates:
                log.info("Dropping duplicate timestamps")
                self.data = self.data.drop_duplicates(
                    subset=[self.timestamp_col], keep="first"
                )
            else:
                self.data = self.base.data
            self.data.reset_index(drop=True, inplace=True)

            self.first_timestamp = self.base.first_timestamp
            self.format_site_data()
            print("\n")
            log.info(f"Concatenation of {len(self.data)} rows complete")

        except UnboundLocalError:
            print("No files match to contatenate.")
            log.error(f"No files in {self.dat_dir} match to contatenate.")

        if len(self.failed_files) > 0:
            print(
                f"{len(self.failed_files)} files unable to be concatenated. See failed_files list"  # noqa: E501
            )

        if output_txt:
            self.data.to_csv(os.path.join(dat_dir, out_file), sep=",", index=False)


    def get_filtered_file_list(self) -> list:
        files = [
            os.path.join(self.dat_dir, f)
            for f in sorted(os.listdir(self.dat_dir))
            if self.file_filter in f  # type: ignore
            and self.filter2 in f
            and self.file_type in f
            and string_date_check(self.start_date, self.end_date, f)
        ]

        return files

    def output_txt_file(
        self,
        standard: bool = True,
        shift_timestamps: bool = False,
        out_file: str = "",
        **kwargs,
    ) -> None:
        out_dir = kwargs.get("out_dir", "")

        if shift_timestamps:
            os.makedirs(out_dir, exist_ok=True)
            file_date = (
                str(self.data.iloc[0][self.timestamp_col])
                .replace(" ", "_")
                .replace(":", ".")[:-3]
            )
            file_num = self.filename.split("_")[len(self.filename.split("_")) - 2]
            file_name = "{0}_{1}_{2}_meas.txt".format(
                self.site_number, file_date, file_num
            )
            output_name = os.path.join(out_dir, file_name)

            self.output_name = output_name
            output_file = open(output_name, "w+", encoding="utf-8")
            output_file.truncate()
            output_file.write(self.head)
            output_file.close()

            with open(output_name, "a", encoding="utf-8") as f:
                try:
                    self.site_info = self.site_info.replace(
                        self.first_timestamp, str(self.data.iloc[0][self.timestamp_col])
                    )
                except Exception:
                    print(
                        "couldn't rename 'Effective Date:' info in {0}".format(
                            output_name
                        )
                    )
                    log.exception(
                        "couldn't rename 'Effective Date:' info in {0}".format(
                            output_name
                        )
                    )
                self.site_info.to_csv(
                    f,
                    header=False,
                    sep="\t",
                    index=False,
                    index_label=False,
                    lineterminator="\n",
                )

            output_file.close()

            with open(output_name, "U") as f:
                text = f.read()
                while "\t\n" in text:
                    text = text.replace("\t\n", "\n")

            with open(output_name, "w") as f:
                f.write(text)

            with open(output_name, "a", encoding="utf-8") as f:
                self.data.round(6).to_csv(
                    f,
                    header=True,
                    sep="\t",
                    index=False,
                    index_label=False,
                    lineterminator="\n",
                )

            output_file.close()
            self.insert_blank_header_rows(output_name)

        if standard:
            if out_file != "":
                output_name = out_file
            else:
                output_name = self.out_file[:-4] + "_standard.txt"

            print(
                "\nOutputting file: {0}   ...   ".format(output_name),
                end="",
                flush=True,
            )
            log.info("\nOutputting file: {0}   ...   ".format(output_name))

            try:
                output_file = open(output_name, "w+", encoding="utf-8")
                output_file.truncate()
                # output_file.write(self.head)
                output_file.close()

                # write header
                with open(output_name, "a", encoding="utf-8") as f:
                    self.site_info.to_csv(
                        f,
                        header=False,
                        sep="\t",
                        index=False,
                        index_label=False,
                        lineterminator="\n",
                    )
                output_file.close()

                # write data
                with open(output_name, "a", encoding="utf-8") as f:
                    self.data.round(6).to_csv(
                        f,
                        header=True,
                        sep="\t",
                        index=False,
                        index_label=False,
                        lineterminator="\n",
                    )
                output_file.close()
                self.insert_blank_header_rows(output_name)
                print("[OK]")

            except Exception:
                print("[FAILED]")
                log.exception(f"Outputting {output_name} failed")

    def insert_blank_header_rows(self, filename: str):
        """insert blank rows when using shift_timestamps()

        ensures the resulting text file looks and feels like an
        original LOGR  export
        """
        header_section_headings = [
            "Site Properties",
            "File Properties",
            "Sensor History",
            "Data",
        ]

        blank_list = []
        field_lines = {}

        for h in header_section_headings:
            for i in locate_text_in_df_column(self.site_info, h):
                blank_list.append(i)
                field_lines[h] = i + 2

        skip_first_channel = True
        _channel = locate_text_in_df_column(self.site_info, "Channel:")
        for i in _channel:
            if skip_first_channel:
                skip_first_channel = False
            else:
                blank_list.append(i)

        f_read = open(filename, "r")
        contents = f_read.readlines()
        f_read.close()

        contents[field_lines[header_section_headings[0]]] = (
            header_section_headings[0] + "\n"
        )
        contents[field_lines[header_section_headings[1]]] = (
            header_section_headings[1] + "\n"
        )
        contents[field_lines[header_section_headings[2]]] = (
            header_section_headings[2] + "\n"
        )
        contents[field_lines[header_section_headings[3]]] = (
            header_section_headings[3] + "\n"
        )

        for i in list(reversed(sorted(blank_list))):
            contents.insert(i + 2, "\n")

        f_write = open(filename, "w")
        contents = "".join(contents)
        f_write.write(contents)
        f_write.close()


def shift_timestamps(
    txt_folder: str = "",
    out_folder: str = "",
    file_filter: str = "",
    start_date: str = "1970-01-01",
    end_date: str = "2150-12-31",
    seconds: int = 3600,
):
    """Takes as input a folder of exported standard text files and
    time to shift in seconds.

    Parameters
    ----------
    txt_folder : str
        path to folder with txt files to shift
    out_folder : str
        where to put the shifted files (in subfolder by default)
    file_filter : str
        filter for restricting file set
    start_date : str
        date filter "YYYY-mm-dd"
    end_date : str
        date filter "YYYY-mm-dd"
    seconds : int
        time in seconds to shift timestamps (default 3600)

    Returns
    -------
    obj
        text files with shifted timestamps; new file names include shifted
        timestamp.

    """
    if out_folder:
        out_dir = out_folder
    else:
        out_dir = os.path.join(txt_folder, "shifted_timestamps")

    os.makedirs(out_dir, exist_ok=True)

    files = [
        f
        for f in sorted(glob(txt_folder + "/" + "*.txt"))
        if file_filter in f and string_date_check(start_date, end_date, f)
    ]

    file_count = len(files)
    counter = 1
    start_time = datetime.now()

    for f in files:
        try:
            draw_progress_bar(counter, file_count, start_time)
            f = os.path.join(txt_folder, f)
            fut = LogrRead(filename=f)
            fut.format_site_data()
            fut.data[fut.timestamp_col] = pd.to_datetime(fut.data[fut.timestamp_col]) + timedelta(
                seconds=seconds
            )
            fut.output_txt_file(
                shift_timestamps=True, standard=False, out_dir=out_dir, out_file=f
            )
        except pd.errors.EmptyDataError:
            pass

        except Exception:
            log.exception(f"unable to shift timestamps in {f}")

        counter += 1


LogrRead = LogrRead
logr_diag_columns = [
    "Stats_Timestamp",
    "VIN_RP_V_Avg",
    "VIN_RP_V_Min",
    "VIN_RP_V_Max",
    "VIN_RP_V_SD",
    "12_4V_V_Avg",
    "12_4V_V_Min",
    "12_4V_V_Max",
    "12_4V_V_SD",
    "12_4V_mA_Avg",
    "12_4V_mA_Min",
    "12_4V_mA_Max",
    "12_4V_mA_SD",
    "3_3V_V_Avg",
    "3_3V_V_Min",
    "3_3V_V_Max",
    "3_3V_V_SD",
    "3_3V_mA_Avg",
    "3_3V_mA_Min",
    "3_3V_mA_Max",
    "3_3V_mA_SD",
    "COMA EXC_V_Avg",
    "COMA EXC_V_Min",
    "COMA EXC_V_Max",
    "COMA EXC_V_SD",
    "COMA EXC_mA_Avg",
    "COMA EXC_mA_Min",
    "COMA EXC_mA_Max",
    "COMA EXC_mA_SD",
    "COMB EXC_V_Avg",
    "COMB EXC_V_Min",
    "COMB EXC_V_Max",
    "COMB EXC_V_SD",
    "COMB EXC_mA_Avg",
    "COMB EXC_mA_Min",
    "COMB EXC_mA_Max",
    "COMB EXC_mA_SD",
    "+VIN_RP_Avg",
    "+VIN_RP_Min",
    "+VIN_RP_Max",
    "+VIN_RP_SD",
    "13_3V_V_Avg",
    "13_3V_V_Min",
    "13_3V_V_Max",
    "13_3V_V_SD",
    "15V_V_Avg",
    "15V_V_Min",
    "15V_V_Max",
    "15V_V_SD",
    "12V_V_Avg",
    "12V_V_Min",
    "12V_V_Max",
    "12V_V_SD",
    "5V_V_Avg",
    "5V_V_Min",
    "5V_V_Max",
    "5V_V_SD",
    "-VIN_RP_V_Avg",
    "-VIN_RP_V_Min",
    "-VIN_RP_V_Max",
    "-VIN_RP_V_SD",
    "-15V_V_Avg",
    "-15V_V_Min",
    "-15V_V_Max",
    "-15V_V_SD",
    "12V_mA_Avg",
    "12V_mA_Min",
    "12V_mA_Max",
    "12V_mA_SD",
]

logr_log_columns = [
    "Timestamp",
    "EpochTime",
    "EventType",
    "Description",
    "Details",
]

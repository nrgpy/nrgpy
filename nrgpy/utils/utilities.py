try:
    from nrgpy import logger
except ImportError:
    pass
from datetime import datetime
import os
import pathlib
import pickle
import pandas as pd
import psutil
import re
import sys
import traceback


def affirm_directory(directory: str) -> None:
    """create directory if not exists

    print status to terminal
    """
    if os.path.exists(directory):
        pass

    else:
        try:
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass
        except Exception:
            pass


def check_platform() -> sys.platform:
    """determine which operating system python is running on"""
    return sys.platform


def count_files(
    directory: str, filters: str, extension: str, show_files: bool = False, **kwargs
) -> int:
    """counts the number of files in the first level of a directory

    Parameters
    ----------
    directory : str
        path of directory to be checked
    filters : str
        filter present in file to be checked
    extension : str
        secondary filter
    show_files : bool, optional
        if set to True, prints file name
    start_time :  int
        seconds; if set, use as reference; only count if file is newer than start_time
    """
    if "start_time" in kwargs:
        start_time = kwargs.get("start_time")
    count = 0
    file_list = []

    for dirpath, subdirs, files in os.walk(directory):
        for x in files:
            if os.path.isfile(os.path.join(directory, x)):
                if filters in x:
                    if extension.lower() in x.lower():
                        try:
                            if os.path.getmtime(os.path.join(dirpath, x)) > start_time:
                                file_list.append(x)
                                count = count + 1

                        except NameError:
                            file_list.append(x)
                            count = count + 1

    if show_files:
        return count, file_list
    return count


def string_date_check(start_date: str, end_date: str, string: str) -> bool:
    """returns true if string date is between dates

    Parameters
    ----------
    start_date : str
        "YYYY-mm-dd"
    end_date : str
        "YYYY-mm-dd"
    string : str
        string including date to check
    """
    # LOGR & SymphonieClassic
    date_format_no_dash = "([0-9]{4}[0-9]{2}[0-9]{2})"
    strp_format_no_dash = "%Y%m%d"
    # ZX datafile
    date_format_zx = "(Y[0-9]{4}_M[0-9]{2}_D[0-9]{2})"
    strp_format_zx = "Y%Y_M%m_D%d"
    # SymphoniePRO
    date_format_with_dash = "([0-9]{4}\-[0-9]{2}\-[0-9]{2})"
    strp_format_with_dash = "%Y-%m-%d"
    # NRG Cloud TXT Export
    date_format_with_dot = "([0-9]{4}\.[0-9]{2}\.[0-9]{2})"
    strp_format_with_dot = "%Y.%m.%d"

    try:
        start = datetime.strptime(start_date, strp_format_with_dash)
        end = datetime.strptime(end_date, strp_format_with_dash)
    except TypeError:
        print(traceback.format_exc())
        start = start_date
        end = end_date

    if re.search(date_format_no_dash, string):
        date_text = re.search(date_format_no_dash, string)
        try:
            file_date = datetime.strptime(date_text[0], strp_format_no_dash)
        except ValueError:
            ext_date_format_no_dash = "([0-9]{6}[0-9]{4}[0-9]{2}[0-9]{2})"
            date_text = re.search(ext_date_format_no_dash, string)
            file_date = datetime.strptime(date_text[0][6:], strp_format_no_dash)

    elif re.search(date_format_with_dash, string):
        date_text = re.search(date_format_with_dash, string)
        file_date = datetime.strptime(date_text[0], strp_format_with_dash)
    elif re.search(date_format_with_dot, string):
        date_text = re.search(date_format_with_dot, string)
        file_date = datetime.strptime(date_text[0], strp_format_with_dot)
    elif re.search(date_format_zx, string):
        date_text = re.search(date_format_zx, string)
        file_date = datetime.strptime(date_text[0], strp_format_zx)

    if (file_date >= start) and (file_date <= end):
        return True
    else:
        return False


# in case anyone is using this directly
date_check = string_date_check


def draw_progress_bar(
    index, total, start_time, barLen=45, header="Time elapsed", label=""
) -> None:
    """simple text progress bar"""
    percent = index / total
    pad = len(str(total))

    sys.stdout.write("\r")
    sys.stdout.write(
        "{}: {} {} | {} {} / {} {} [{:<{}}] {:.0f}%\t".format(
            header,
            (datetime.now() - start_time).seconds,
            "s",
            str(index).rjust(pad),
            label,
            total,
            label,
            "=" * int(barLen * percent),
            barLen,
            percent * 100,
        )
    )
    sys.stdout.flush()


def linux_folder_path(folder_path) -> str:
    """assert folder_path ending with '/'"""
    folder_path = folder_path.replace("\\", "/").replace(" ", "\ ")

    if folder_path.endswith("/"):
        pass
    else:
        folder_path = folder_path + "/"

    return folder_path


def windows_folder_path(folder_path) -> str:
    """convert '/' to '\\' in folder_path and assert ending in '\\'"""
    folder_path = folder_path.replace("/", "\\")

    if folder_path.endswith("\\"):
        pass
    else:
        folder_path = folder_path + "\\"

    return folder_path


class renamer:
    """for replacing duplicate column names after transpose"""

    def __init__(self):
        self.d = dict()

    def __call__(self, x):
        if x not in self.d:
            self.d[x] = 0
            return x

        else:
            self.d[x] += 1
            return "%s_%d" % (x, self.d[x])


def save(reader, filename="") -> None:
    """save reader as a Python pickle file, to be recalled later"""
    if not filename:
        try:
            filename = f"{reader.site_number}_reader.pkl"
        except Exception:
            filename = f"{reader.serial_number}_reader.pkl"

    with open(filename, "wb") as pkl:
        pickle.dump(reader, pkl, protocol=pickle.HIGHEST_PROTOCOL)


def load(site_number: str = "", serial_number: str = "", filename: str = "") -> object:
    """recall a reader from a pickle file by site number or filename

    parameters
    ----------
    site_number : str
        6-digit site number of stored reader OR spidar serial number
    filename : str
        full or relative path of pickle file

    returns
    -------
    object
        contents of pickle file

    """
    if not filename and not serial_number:
        filename = f"{site_number}_reader.pkl"

    if serial_number and not filename:
        filename = f"{serial_number}_reader.pkl"

    with open(filename, "rb") as pkl:
        reader = pickle.load(pkl)

    return reader


def data_months(start_date: str, end_date: str, output: str = "string") -> list:
    """returns list of months for a date range in YYYY-mm-dd format

    parameters
    ----------
    start_date : str or datetime
        YYYY-mm-dd formatted date or datetime object
    end_date : str or datetime
        must be same formatting as start_date or god help you
    output : str
        "string" or "datetime"; specify date types you want returned.

    returns
    -------
    list
    """

    if isinstance(start_date, str) and re.match(
        "^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])", start_date
    ):
        start_year = start_date.split("-")[0]
        start_month = start_date.split("-")[1]
        start_day = start_date.split("-")[2]
        end_year = end_date.split("-")[0]
        end_month = end_date.split("-")[1]
        end_day = end_date.split("-")[2]

    elif isinstance(start_date, datetime):
        start_year = start_date.year
        start_month = start_date.month
        start_day = start_date.day
        end_year = end_date.year
        end_month = end_date.month
        end_day = end_date.day

    else:
        print(f"unsupported date type: {output}\nuse 'YYYY-mm-dd' or datetime object")
        return False

    years = list(range(int(start_year), int(end_year) + 1))

    months = []

    for y in years:
        if str(y) == str(start_year):
            _month0 = int(start_month)
        else:
            _month0 = 1

        if str(y) == str(end_year):
            _month12 = int(end_month)
        else:
            _month12 = 12

        for _m in list(range(_month0, _month12 + 1)):
            if output == "string":
                months.append(f"{y}-{str(_m).zfill(2)}-01")

            elif output == "datetime":
                months.append(datetime(y, _m, 1))

            else:
                print(f"unsupported output type: {output}\nuse 'string' or 'datetime'")
                return False

    return months


def create_spd_filename_from_cloud_export(filename: str) -> str:
    cld_fmt = "%m-%d-%Y"
    spd_fmt = "%Y-%m-%d"

    splits = filename.split("_")
    site = splits[0].zfill(6)
    start = datetime.strptime(splits[1], cld_fmt).strftime(spd_fmt)
    end = datetime.strptime(splits[3], cld_fmt).strftime(spd_fmt)
    outname = "_".join([site, start, end, splits[-1]]).replace("Measurements", "meas")

    return outname


def rename_cloud_export_like_spd(filepath: str) -> bool:
    """rename nrg cloud export files with SPD formatting"""

    filename = os.path.basename(filepath)
    directory = os.path.dirname(filepath)
    new_filename = create_spd_filename_from_cloud_export(filename)

    try:
        os.rename(filepath, os.path.join(directory, new_filename))
        logger.info(f"renamed {filename} to {new_filename}")
        return True

    except FileExistsError:
        logger.info(f"{new_filename} exists, replacing")
        os.remove(os.path.join(directory, new_filename))
        os.rename(filepath, os.path.join(directory, new_filename))
        logger.info(f"renamed {filename} to {new_filename}")

    except Exception:
        logger.error(f"couldn't rename {filename} to {new_filename}")
        print(f"couldn't rename {filename} to {new_filename}")
        import traceback

        logger.debug(traceback.format_exc())
        print(traceback.format_exc())
        return False


def fix_export_siteid_filename(filepath: str, site_number: str) -> str:
    """Change out NRG Cloud site id with padded site number"""
    filename = os.path.basename(filepath)
    if filename.startswith("siteid"):
        filename = site_number + "_".join(filename.split("_")[1:])
        filepath = os.path.join(os.path.dirname(filepath), filename)

    return filepath


def is_sympro_running() -> bool:
    """checks pid list for instance of sympro running"""

    if psutil.WINDOWS:
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if p.name() == "SymPRODesktop.exe":
                return True

    return False


def set_start_stop(reader: object, with_time: bool = False) -> None:
    """ """
    reader.start_date = reader.data["Timestamp"].loc[0]
    reader.end_date = reader.data["Timestamp"].loc[len(reader.data) - 1]

    if not with_time:
        reader.start_date = reader.start_date.date()
        reader.end_date = reader.end_date.date()


def locate_text_in_df_column(
    dataframe: pd.DataFrame, text: str, column: str | int = 0
) -> list:
    return dataframe.loc[dataframe[column].str.contains(text)].index

from datetime import datetime
import os
import pathlib
import pickle
import re
import sys


def affirm_directory(directory):
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
        except:
            pass


def check_platform():
    """determine which operating system python is running on"""
    from sys import platform
    return(platform)


def count_files(directory, filters, extension, show_files=False, **kwargs):
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
                            if os.path.getmtime(os.path.join(dirpath,x)) > start_time:
                                file_list.append(x)
                                count = count + 1

                        except NameError:
                            file_list.append(x)
                            count = count + 1

    if show_files == True:
        return count, file_list
    return count


def date_check(start_date, end_date, string):
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
    date_format = "([0-9]{4}\-[0-9]{2}\-[0-9]{2})"

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end   = datetime.strptime(end_date, "%Y-%m-%d")
    except TypeError:
        start = start_date
        end = end_date

    try:
        date_text = re.search(date_format, string)
        file_date = datetime.strptime(date_text[0], "%Y-%m-%d")
        if (file_date >= start) and (file_date <= end):
            return True
        else:
            return False
    except Exception as e:
        return False


def draw_progress_bar(index, total, start_time, barLen=45):
    """simple text progress bar"""
    percent = index / total
    pad = len(str(total))

    sys.stdout.write("\r")
    sys.stdout.write(
        "Time elapsed: {} {} | {} / {} [{:<{}}] {:.0f}%\t".format(
            (datetime.now() - start_time).seconds, "s",
            str(index).rjust(pad),
            total,
            "=" * int(barLen * percent),
            barLen,
            percent * 100
        )
    )
    sys.stdout.flush()


def linux_folder_path(folder_path):
    """assert folder_path ending with '/' """
    folder_path = folder_path.replace('\\', '/').replace(' ', '\ ')

    if folder_path.endswith('/'):
        pass
    else:
        folder_path = folder_path + '/'

    return folder_path


def windows_folder_path(folder_path):
    """convert '/' to '\\' in folder_path and assert ending in '\\'"""
    folder_path = folder_path.replace('/', '\\')

    if folder_path.endswith('\\'):
        pass
    else:
        folder_path = folder_path + '\\'

    return folder_path


class renamer():
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


def save(reader, filename=""):
    """save reader as a Python pickle file, to be recalled later"""
    if not filename:
        try:
            filename = f"{reader.site_number}_reader.pkl"
        except:
            filename = f"{reader.serial_number}_reader.pkl"

    with open(filename, 'wb') as pkl:
        pickle.dump(reader, pkl, protocol=pickle.HIGHEST_PROTOCOL)


def load(site_number="", filename=""):
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
    if not filename:
        filename = f"{site_number}_reader.pkl"

    with open(filename, 'rb') as pkl:
        reader = pickle.load(pkl)

    return reader

#!/bin/usr/python
import os
import pathlib


def check_platform():
    """
    determine which operating system python is running on
    """
    from sys import platform
    return(platform)


def affirm_directory(directory):
    """
    create directory if not exists, print status to terminal
    """
    if os.path.exists(directory):
        pass
    else:
        try:
            print("{0} does not exist, creating...\t\t".format(directory), end="", flush=True)
            try:
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                print("[OK]")
            except:
                print('[FAILED]')
        except:
            print('[FAILED]')



def windows_folder_path(folder_path):
    """
    convert '/' to '\\' in folder_path and assert ending in '\\'
    """
    folder_path = folder_path.replace('/', '\\')
    if folder_path.endswith('\\'):
        pass
    else:
        folder_path = folder_path + '\\'
    return folder_path


def linux_folder_path(folder_path):
    """
    assert folder_path ending with '/'
    """
    folder_path = folder_path.replace('\\', '/').replace(' ', '\ ')
    if folder_path.endswith('/'):
        pass
    else:
        folder_path = folder_path + '/'
    return folder_path


def count_files(directory, filters, extension, show_files=False, **kwargs):
    """
    counts the number of files in the first level of a directory

    parameters:
        1 -  directory | the directory to be checked
        2 -    filters | text/string filter present in file to be checked
        3 -  extension | secondary text/string filter 
        4 - show_files | optional: if set to True, prints file name
        5 - start_time | kwarg: seconds; if set, use as reference; 
                            only count if file is newer than start_time
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

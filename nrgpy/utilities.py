#!/bin/usr/python


def check_platform():
    """
    determine which operating system python is running on
    """
    from sys import platform
    return(platform)


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
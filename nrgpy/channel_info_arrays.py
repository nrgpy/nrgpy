#!/bin/usr/python


def return_array(data_file_type):
    """
    return data file header parameter array
    based on data_file_type
    """
    if data_file_type.lower() in ["symplus3", "symphonieplus3", "sp3"]:
        return_sp3_ch_info()
    elif data_file_type.lower() in ["sympro", "symphoniepro"]:
        return_spro_ch_info()
    else:
        return 0


def return_sp3_ch_info():
    """
    returns array of sensor info parameters for
    SymphoniePLUS3 txt export files
    """
    
    array = [
        'Channel #\t',
        'Type\t',
        'Description\t',
        'Details\t',
        'Serial Number\t',
        'Height	90\t',
        'Scale Factor\t',
        'Offset\t',
        'Units\t'
    ]

    return array


def return_spro_ch_info():
    """
    returns array of possible channel parameters
    for SymphoniePRO txt export files
    """

    array = [
        'Channel:',
        'Export Channel:',
        'Effective Date:',
        'Type:',
        'Description:',
        'Serial Number:',
        'Height:',
        'Bearing:',
        'Scale Factor:',
        'Offset:',
        'Units:',
        'P-SCM Type:'
    ]

    return array

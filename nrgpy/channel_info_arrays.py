#!/bin/usr/python


def return_array(data_file_type):
    """
    return data file header parameter array
    based on data_file_type
    """
    if data_file_type.lower() in ["symplus3", "symphonieplus3", "sp3", "4941"]:
        a, b, c = return_sp3_ch_info()
        return a, b, c
    elif data_file_type.lower() in ["sympro", "symphoniepro", "8206"]:
        a, b, c = return_spro_ch_info()
        return a, b, c
    else:
        return 0


def return_sp3_ch_info():
    """
    returns array of sensor info parameters for
    SymphoniePLUS3 txt export files
    """
    
    array = [
        'Channel #',
        'Type',
        'Description',
        #'Details',
        'Serial Number',
        'Height 90',
        'Scale Factor',
        'Offset',
        'Units'
    ]

    header_sections = {}
    header_sections['site_info_start'] = "-----Site Information-----"
    header_sections['sensor_info_start'] = "-----Sensor Information-----"
    header_sections['data_header'] = "Date & Time Stamp"
    skip_rows = 6
    
    return array, header_sections, skip_rows


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

    header_sections = {}
    header_sections['site_info_start'] = "Export Parameters"
    header_sections['sensor_info_start'] = "Sensor History"
    header_sections['data_header'] = "Data\n"
    skip_rows = 2

    return array, header_sections, skip_rows

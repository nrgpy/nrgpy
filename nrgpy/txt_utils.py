#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
import re
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path


class symplus3(object):
    """
    class for handling symplus3 txt exports
    """
    def __init__(self, )
        pass

    
    def arrange_ch_info(self):
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

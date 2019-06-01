import pyodbc
import pandas as pd
from nrgpy.utilities import check_platform

class nsd(object):
    import pyodbc
    import pandas as pd
    from nrgpy.utilities import check_platform
    def __init__(self, nsd_file=''):
        if check_platform() != 'win32':
            print("nsd functions only compatible with Windows")
            return False
        self.nsd_file = nsd_file
        self.driver_check = self.check_for_jet_drivers()
        if self.driver_check == True:
            try:
                self.conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'+r'DBQ='+self.nsd_file+';'
                self.conn = pyodbc.connect(self.conn_str)
            except Exception as e:
                self.e = e
                print("whomp, whomp.")
        else:
            print("Microsoft Access drivers required for these functions.")
            print("Download drivers from:")
            print("https://www.microsoft.com/en-US/download/details.aspx?id=13255\n\n")
            print("Note: Python architecture must match any installed Microsoft Office")
            print("architecture (32-bit or 64-bit)")
            print("If your MS Office is installed in C:\Program Files (x86), you'll need")
            print("the 32-bit version of Python 3+ to use these functions\n\n")

    
    def read_sensor_history(self):
        """
        read SensorHistory table into dataframe

        returns
            sensor_history dataframe
        """
        sql = "SELECT * FROM SensorHistory"
        try:
            self.sensor_history = pd.read_sql(sql, self.conn)
        except Exception as e_sh:
            self.sensor_history_e = e_sh


    def read_channel_settings(self, channel=0):
        """
        read individual channel settings from sensor history table
        """
        sql = "SELECT * FROM SensorHistory WHERE Channel = {0}".format(channel)
        try:
            self.channel_settings = pd.read_sql(sql, self.conn)
        except Exception as rcs_e:
            self.channel_settings = False
            self.rcs_e = rcs_e


    def write_channel_settings(self, channel=0, description='',
                           print_precision=-9999, units='',
                           serial_number='', height='',
                           scale_factor=-9999, offset=-9999):
        """
        write new sensor history to site file
        """
        if channel > 0:
            channel = " WHERE Channel = {}".format(channel)
            if description != '':
                description = " SensorDesc = '{}',".format(description)
            if print_precision != -9999:
                print_precision = " PrintPrecision = {},".format(print_precision)
            else:
                print_precision = ""
            if units != '':
                units = " Units = '{}',".format(units)
            if serial_number != '':
                serial_number = " SerialNumber = '{}',"
            if height != '':
                height = " Height = '{}',".format(height)
            if scale_factor != -9999:
                scale_factor = " ScaleFactor = {},".format(scale_factor)
            else:
                scale_factor = ""
            if offset != -9999:
                offset = " Offset = {},".format(offset)
            else:
                offset = ""
        sql = "UPDATE SensorHistory SET{0}{1}{2}{3}{4}{5}{6}".format(
            description, str(print_precision), units, serial_number, height, 
            str(scale_factor), str(offset))[:-1]
        self.sql = ''.join([char for char in sql+channel])
        self.conn.execute(self.sql)
        self.conn.commit()

    def check_for_jet_drivers(self):
        """
        check for jet database drivers
        """
        self.drivers = [x for x in pyodbc.drivers()]
        if "Microsoft Access Driver (*.mdb, *.accdb)" in self.drivers:
            return True
        return False

"""
conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'+r'DBQ='+filename+';'

conn = pyodbc.connect(conn_str)

sql = "SELECT * FROM SensorHistory"

sensor_history = pd.read_sql(sql, conn)

sensor_history

e_sql = "UPDATE SensorHistory SET SensorDesc = 'Some Description' WHERE Channel = 1;"
"""
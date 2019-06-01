import pyodbc
import pandas as pd

class connect(object):
    def __init__():
        pass


"""
filename = r"\\sol\techsupport\services\_newserviceideas\nrgpy-nsd-reader\0322.nsd"

conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'+r'DBQ='+filename+';'

conn = pyodbc.connect(conn_str)

sql = "SELECT * FROM SensorHistory"

sensor_history = pd.read_sql(sql, conn)

sensor_history

e_sql = "UPDATE SensorHistory SET SensorDesc = 'Some Description' WHERE Channel = 1;"
"""
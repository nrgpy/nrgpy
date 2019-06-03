# <img alt="NRGPy" src="https://www.nrgsystems.com/mysite/images/logo.png?v=3" height="40">

# nsd_functions.py 
- for handling NRG Site Database (NSD) files from Symphonie, SymphoniePLUS and SymphoniePLUS3 Data Loggers.

_Note_: __this feature set is only compatible with Windows installations__. If you have any MS Office programs installed on the host computer, the Python installation must be the same architecture (either 32-bit or 64-bit). Download the driver to connect to the NSD database here:

https://www.microsoft.com/en-US/download/details.aspx?id=13255


## Example for using nsd_functions.py to read and change sensor history settings in NSD files.
``` python
In [1]: from nrgpy.nsd_functions import nsd

In [2]: db = nsd(nsd_file="C:/NRG/SiteFiles/0322.nsd")

In [3]: db.read_channel_settings(channel=1)

In [4]: db.channel_settings
Out[4]: 
   TimeStamp  Channel  SensorType          SensorDesc SerialNumber  Height  ScaleFactor  Offset  PrintPrecision Units SensorDetail SensorNotes
0 1899-12-30        1           1    NRG #40 Anem. m/s    SN002618  50   m        0.766   0.332               1   m/s

In [5]: db.write_channel_settings(channel=1, description="50m CLASS 1 m/s", scale_factor=1, offset=1)

In [6]: db.read_channel_settings(channel=1)

In [7]: db.channel_settings
Out[7]: 
   TimeStamp  Channel  SensorType       SensorDesc SerialNumber  Height  ScaleFactor  Offset  PrintPrecision Units SensorDetail SensorNotes
0 1899-12-30        1           1  50m CLASS 1 m/s     SN002618  50   m          1.0     1.0               1   m/s
```

## Read all sensor history into a dataframe:

```python
In [1]: from nrgpy.nsd_functions import nsd

In [2]: db = nsd(nsd_file="C:/NRG/SiteFiles/0322.nsd")

In [3]: db.read_sensor_history()

In [4]: db.sensor_history
Out[4]: 
    TimeStamp  Channel  SensorType            SensorDesc SerialNumber  Height  ScaleFactor   Offset  PrintPrecision  Units SensorDetail SensorNotes
0  1899-12-30        1           1     NRG #40 Anem. m/s     SN002618  50   m        1.000    1.000               1    m/s
1  1899-12-30        2           1     NRG #40 Anem. m/s       SN0066  50   m        0.759    0.365               1    m/s
2  1899-12-30        3           1     NRG #40 Anem. m/s     SN006613  22   m        0.758    0.386               1    m/s
3  1899-12-30        4           1     NRG #40 Anem. m/s     SN000009  22   m        0.762    0.370               1    m/s
4  1899-12-30        5           0      No SCM Installed     --------  ------        0.000    0.000               0  -----
5  1899-12-30        6           0      No SCM Installed     --------  ------        0.000    0.000               0  -----
6  1899-12-30        7           3        200P Wind Vane         DBTT  46   m        0.351  305.000               0    deg
7  1899-12-30        8           3        200P Wind Vane         DBTT  20   m        0.351  305.000               0    deg
8  1899-12-30        9           0      No SCM Installed     --------  ------        0.000    0.000               0  -----
9  1899-12-30       10           4             Voltmeter      SN:0032  3    m        0.021    0.000               1      v
10 1899-12-30       11           4     NRG #110S Temp  C          SN:       0        0.136  -86.381               1      C
11 1899-12-30       12           0      No SCM Installed     --------  ------        0.000    0.000               0  -----
12 1899-12-30       13           1     NRG #40 Anem. m/s          SN:       m        0.765    0.350               1    m/s
13 1899-12-30       14           1     NRG #40 Anem. m/s          SN:       m        0.765    0.350               1    m/s
14 1899-12-30       15           1     NRG #40 Anem. m/s          SN:       m        0.765    0.350               1    m/s

```
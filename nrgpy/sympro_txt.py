#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
import re
from nrgpy.utilities import check_platform, windows_folder_path, linux_folder_path, draw_progress_bar, date_check, renamer
import traceback


class sympro_txt_read(object):

    def __init__(self, filename='', out_file='', text_timestamps=False, **kwargs):
        """Class of pandas dataframes created from SymPRO standard txt output.

        If a filename is passed when calling class, the file is read in alone. Otherwise,
        and instance of the class is created, and the concat_txt function may be called to
        combine all txt files in a directory.

        filter may be used on any part of the filename, to combine a subset of text files in
        a directory.

        Parameters
        ----------
        filename : str, optional
            path to filename
        out_file : str, optional
            path to outputted file
        text_timestamps : boolean
            set to True for text timestamps

        Returns
        ---------
        ch_info : obj
            pandas dataframe of ch_list (below) pulled out of file with sympro_txt_read.arrange_ch_info()
        ch_list : list
            list of channel info; can be converted to json w/ import json ... json.dumps(fut.ch_info)
        data : obj
            pandas dataframe of all data
        head : obj
            lines at the top of the txt file..., used when rebuilding timeshifted files
        site_info : obj
            pandas dataframe of site information
        logger_sn : str
        ipack_sn : str
        logger_type : str
        ipack_type : str
        latitude : float
        longitude : float
        elevation : int
        site_number : str
        site_description : str
        start_date : str
        """

        self.filename = filename
        self.text_timestamps = text_timestamps
        self.out_file = out_file

        if out_file == "":
            out_file = datetime.today().strftime("%Y-%m-%d") + "_SymPRO.txt"

        if 'ch_details' in kwargs:
            self.ch_details = kwargs.get('ch_details')
        else:
            self.ch_details = False

        if self.filename:
            i = 0
            with open(self.filename) as infile:
                for line in infile:
                    if line == "Data\n":
                        break
                    else:
                        i = i + 1
            with open(self.filename) as myfile:
                self.head = "".join([next(myfile) for x in range(2)])

            header_len = i + 1
            read_len = header_len - 5

            self.site_info = pd.read_csv(self.filename, skiprows=2, sep="\t",
                                        index_col=False, nrows=read_len,
                                        usecols=[0,1], header=None)

            self.site_info = self.site_info.iloc[:self.site_info.loc[self.site_info[0] == 'Data'].index.tolist()[0]+1]
            self.data = pd.read_csv(self.filename, skiprows=header_len, sep="\t", encoding='iso-8859-1')
            if not self.text_timestamps:
                self.data['Timestamp'] = pd.to_datetime(self.data['Timestamp'])
            self.first_timestamp = self.data.iloc[0]['Timestamp']
            self.arrange_ch_info()


    def __repr__(self):
        return '<class {}: {} >'.format(self.__class__.__name__,self.filename)

    def arrange_ch_info(self):
        """creates ch_info dataframe and ch_list array"""
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
            'Units:'
        ]

        if self.ch_details == True:
            array += [
                'P-SCM Type:',
                'Total Direction Offset:',
                'Dead Band East:',
                'Dead Band West:',
                'Excitation Mode:',
                'Excitation Value:',
                'Data Logging Mode:'
            ]
        else:
            pass

        self.array = array
        self.ch_info = pd.DataFrame()
        ch_data = {}
        ch_list = []
        ch_details = 0

        for row in self.site_info.loc[self.site_info[0].isin(array)].iterrows():

            if row[1][0] == array[0] and ch_details == 0: # start channel data read
                ch_details = 1
                ch_data[row[1][0]] = row[1][1]

            elif row[1][0] == array[0] and ch_details == 1: # close channel, start new data read
                ch_list.append(ch_data)
                ch_data = {}
                ch_data[row[1][0]] = row[1][1]

            elif row[1][0] in str(array):
                ch_data[row[1][0]] = row[1][1]

        ch_list.append(ch_data) # last channel's data

        self.ch_list = ch_list
        self.ch_info = self.ch_info.append(ch_list)

        return self

    def format_site_data(self):
        """take txt header to create oject data"""
        try:
            self.Site_info = self.site_info.copy()
            self._site_info = self.Site_info.T
            self._site_info.columns = self._site_info.iloc[0]
            self._site_info.columns = self._site_info.iloc[0]
            self._site_info = self._site_info[1:]

            width = list(self._site_info.columns.values).index('Sensor History')

            self._site_info.rename(columns=renamer(), inplace=True)
            self._site_info.drop(self._site_info.iloc[:, width:len(self._site_info.columns)], axis=1, inplace=True, errors='ignore')
            self._site_info.columns = [str(col).replace(':','').strip() for col in self._site_info.columns]

            self.latitude = float(self._site_info['Latitude'].values[0])
            self.longitude = float(self._site_info['Longitude'].values[0])
            self.elevation = int(self._site_info['Elevation'].values[0])
            self.location = self._site_info['Location'].values[0]
            self.site_number = self._site_info['Site Number'].values[0]
            self.site_description = self._site_info['Site Description'].values[0]

            self.logger_sn = self._site_info['Serial Number'].values[0]
            self.ipack_sn = self._site_info['Serial Number_1'].values[0]
            self.logger_type = self._site_info['Model'].values[0]
            self.ipack_type = self._site_info['Model_1'].values[0]
            self.time_zone = self._site_info['Time Zone'].values[0]

        except Exception as e:
            self.e = e
            print("Warning: error processing site_info: {}".format(e))

    def concat_txt(self, txt_dir='', file_type='meas', file_filter='',
                    filter2='', start_date='1970-01-01', end_date='2150-12-31',
                    ch_details=False, output_txt=False, out_file='',
                    progress_bar=True, **kwargs):
        """Will concatenate all text files in the txt_dir

        files must match the site_filter argument. Note these are both blank by default.

        Parameters
        ----------
        txt_dir : str
            directory holding txt files
        file_type : str
            type of export (meas, event, comm, sample, etc...)
        file_filter : str
            text filter for txt files, like site number, etc.
        filter2 : str
            secondary text filter
        start_date : str
            for filtering files to concat based on date "YYYY-mm-dd"
        end_date : str
            for filtering files to concat based on date "YYYY-mm-dd"
        ch_details : bool
            show additional info in ch_info dataframe
        output_txt : bool
            create a txt output of data df
        out_file : str
            filename to write data dataframe too if output_txt = True
        progress_bar : bool
            show bar on concat [True] or list of files [False]

        Returns
        ---------
        ch_info : obj
            pandas dataframe of ch_list (below) pulled out of file with sympro_txt_read.arrange_ch_info()
        ch_list : list
            list of channel info; can be converted to json w/ import json ... json.dumps(fut.ch_info)
        data : obj
            pandas dataframe of all data
        head : obj
            lines at the top of the txt file..., used when rebuilding timeshifted files
        site_info : obj
            pandas dataframe of site information
        logger_sn : str
        ipack_sn : str
        logger_type : str
        ipack_type : str
        latitude : float
        longitude : float
        elevation : int
        site_number : str
        site_description : str
        start_date : str
        txt_file_names : list
            list of files included in concatenation

        Examples
        --------
        Read files into nrgpy reader object

        >>> import nrgpy
        >>> reader = nrgpy.sympro_txt_read()
        >>> reader.concat_txt(
                txt_dir='/path/to/txt/files/',
                file_filter='123456', # site 123456
                start_date='2020-01-01',
                end_date='2020-01-31',
            )
        Time elapsed: 2 s | 33 / 33 [=============================================] 100%
        Queue processed
        >>> reader.logger_sn
        '820600019'
        >>> reader.ch_info
         	Bearing: 	Channel: 	Description: 	Effective Date: 	Height: 	Offset: 	Scale Factor: 	Serial Number: 	Type: 	Units:
        0 	50.00 	    1 	        NRG S1 	        2020-01-31 00:00:00 	33.00 	0.13900 	0.09350 	    94120000059 	Anemometer 	m/s
        1 	230.00 	    2 	        NRG S1 	        2020-01-31 00:00:00 	0.00 	0.13900 	0.09350 	    94120000058 	Anemometer 	m/s
        2 	50.00 	    3 	        NRG S1 	        2020-01-31 00:00:00 	22.00 	0.13900 	0.09350 	    94120000057 	Anemometer 	m/s
        3 	230.00 	    4 	        NRG 40C Anem 	2020-01-31 00:00:00 	22.00 	0.35000 	0.76500 	    179500324860 	Anemometer 	m/s
        4 	50.00 	    5 	        NRG 40C Anem 	2020-01-31 00:00:00 	12.00 	0.35000 	0.76500 	    179500324859 	Anemometer 	m/s
        5 	230.00 	    6 	        NRG S1 	        2020-01-31 00:00:00 	12.00 	0.13900 	0.09350 	    94120000056 	Anemometer 	m/s
        6 	320.00 	    13 	        NRG 200M Vane 	2020-01-31 00:00:00 	32.00 	-1.46020 	147.91100 	    10700000125 	Vane 	        Deg
        7 	320.00 	    14 	        NRG 200M Vane 	2020-01-31 00:00:00 	21.00 	-1.46020 	147.91100 	    10700000124 	Vane 	        Deg
        8 	0.00 	    15 	        NRG T60 Temp 	2020-01-31 00:00:00 	34.00 	-40.85550 	44.74360 	    9400000705          Analog          C
        9 	0.00 	    16 	        NRG T60 Temp 	2020-01-31 00:00:00 	2.00 	-40.85550 	44.74360 	    9400000xxx          Analog          C
        10 	0.00 	    17 	        NRG RH5X Humi 	2020-01-31 00:00:00 	0.00 	0.00000 	20.00000 	    NaN 	        Analog          %RH
        11 	0.00 	    20 	        NRG BP60 Baro 	2020-01-31 00:00:00 	0.00 	495.27700 	243.91400 	    NaN 	        Analog          hPa
        12 	0.00 	    21 	        NRG BP60 Baro 	2020-01-31 00:00:00 	2.00 	495.04400 	244.23900 	    9396FT1937          Analog  	hPa
        """

        if 'site_filter' in kwargs and file_filter == '':
            self.file_filter = kwargs.get('site_filter')
        else:
            self.file_filter = file_filter

        self.ch_details = ch_details
        self.start_date = start_date
        self.end_date = end_date
        self.filter2 = filter2
        self.file_type = file_type
        self.txt_file_names = []

        if check_platform() == 'win32':
            self.txt_dir = windows_folder_path(txt_dir)
        else:
            self.txt_dir = linux_folder_path(txt_dir)

        first_file = True

        files = [
            f for f in sorted(glob(self.txt_dir + '*.txt'))\
            if self.file_filter in f and self.filter2 in f\
            and date_check(self.start_date, self.end_date, f)
        ]

        self.file_count = len(files)
        self.pad = len(str(self.file_count))
        self.counter = 1
        self.start_time = datetime.now()

        for f in files:

            if self.file_filter in f and self.file_type in f and self.filter2 in f:

                if progress_bar:
                    draw_progress_bar(self.counter, self.file_count, self.start_time)
                else:
                    print("Adding {0}/{1} ... {2} ... ".format(str(self.counter).rjust(self.pad),str(self.file_count).ljust(self.pad),os.path.basename(f)), end="", flush=True)

                if first_file == True:
                    first_file = False

                    try:
                        base = sympro_txt_read(f, text_timestamps=self.text_timestamps)
                        if progress_bar != True: print("[OK]")
                        self.txt_file_names.append(os.path.basename(f))
                    except IndexError:
                        print('Only standard SymPRO headertypes accepted')
                        break
                    except:
                        if progress_bar != True: print("[FAILED]")
                        print("could not concat {0}".format(os.path.basename(f)))
                        pass
                else:
                    file_path = f

                    try:
                        s = sympro_txt_read(file_path, ch_details=self.ch_details, text_timestamps=self.text_timestamps)
                        base.data = base.data.append(s.data, sort=False)
                        if progress_bar != True: print("[OK]")
                        self.txt_file_names.append(os.path.basename(f))

                    except:
                        if progress_bar != True: print("[FAILED]")
                        print("could not concat {0}".format(os.path.basename(f)))
                        pass
            else:
                pass
            self.counter += 1

        if out_file != "":
            self.out_file = out_file

        if output_txt == True:
            base.data.to_csv(os.path.join(txt_dir, out_file), sep=',', index=False)

        try:
            self.ch_info = s.ch_info
            self.ch_list = s.ch_list
            self.array = s.array
            self.data = base.data.drop_duplicates(subset=['Timestamp'], keep='first')
            self.data.reset_index(drop=True,inplace=True)
            self.head = s.head
            self.site_info = s.site_info
            self.format_site_data()
            print("\n")

        except UnboundLocalError:
            print("No files match to contatenate.")
            return None



    def select_channels_for_reformat(self, epe=False, soiling=False):
        """determines which of the channel headers fit those required for post-processing for either

            a. EPE formatting
            b. soiling ratio calculation

        Note that this formatting requires the the channel headers to be full (requires
        Local export of text files, as of 0.1.8.
        """
        # for EPE formatting
        ch_anem = ['Anem','Anemometer','anem','anemometer','Anemômetro','anemômetro']
        ch_vane = ['Vane','vane','Direction','direction','Veleta','veleta','Direção','direção','Vane w/Offset']
        ch_baro = ['mb','hpa','hPa','millibar','kPa', 'baro', 'Baro']
        ch_relh = ['%RH','%rh','RH','rh']
        ch_temp = ['C','c','?C','Temp','deg c','deg f','temp']

        # for soiling station
        ch_I_units = ['amps','amperes','a','current']
        ch_shunt_desc = ['shunt','isc','current']
        ch_clean_desc = ['clean']
        ch_soiled_desc = ['soil','soiled','dirty']
        ch_PV_temp = ['pv','panel']

        if epe == True:
            self.anem1 = self.ch_info.loc[self.ch_info['Type:'].isin(ch_anem)].sort_values(['Height:'],ascending=False).iloc[[0]]
            self.anem2 = self.ch_info.loc[self.ch_info['Type:'].isin(ch_anem)].sort_values(['Height:'],ascending=True).iloc[[0]]
            self.anem3 = self.ch_info.loc[self.ch_info['Type:'].isin(ch_anem)].sort_values(['Height:'],ascending=False).iloc[[1]]

            self.vane1 = self.ch_info.loc[self.ch_info['Type:'].isin(ch_vane)].sort_values(['Height:'],ascending=False).iloc[[0]]
            self.vane2 = self.ch_info.loc[self.ch_info['Type:'].isin(ch_vane)].sort_values(['Height:'],ascending=False).iloc[[1]]

            try:
                self.baro = self.ch_info.loc[self.ch_info['Units:'].isin(ch_baro)].sort_values(['Height:'],ascending=False).iloc[[0]]
            except:
                self.baro = None
            try:
                self.relh = self.ch_info.loc[self.ch_info['Units:'].isin(ch_relh)].sort_values(['Height:'],ascending=False).iloc[[0]]
            except:
                self.relh = None
            try:
                self.temp = self.ch_info.loc[self.ch_info['Units:'].isin(ch_temp)].sort_values(['Height:'],ascending=False).iloc[[0]]
            except:
                self.temp = None
            self.make_header_for_epe()

        # select channels needed for soiling calculation
        if soiling == True:
            try:
                self.isc_clean = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_clean_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_I_units))))]
                self.isc_soiled = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_soiled_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_I_units))))]
                self.pv_temp_clean = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_clean_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_temp))))]
                self.pv_temp_soiled = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_soiled_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_temp))))]
            except:
                print("SC and PV Temp fields unavailable for calculation")


    def format_data_for_epe(self):
        baro_ch = "Ch" + str(self.baro['Channel:'].iloc[0]) + "_"
        temp_ch = "Ch" + str(self.temp['Channel:'].iloc[0]) + "_"
        relh_ch = "Ch" + str(self.relh['Channel:'].iloc[0]) + "_"
        anem1_ch = "Ch" + str(self.anem1['Channel:'].iloc[0]) + "_"
        anem2_ch = "Ch" + str(self.anem2['Channel:'].iloc[0]) + "_"
        anem3_ch = "Ch" + str(self.anem3['Channel:'].iloc[0]) + "_"
        vane1_ch = "Ch" + str(self.vane1['Channel:'].iloc[0]) + "_"
        vane2_ch = "Ch" + str(self.vane2['Channel:'].iloc[0]) + "_"

        self.data['CH01'] = self.data["Timestamp"].str.split(' ', 1).str[0].str.replace('-','')
        self.data['CH02'] = self.data["Timestamp"].str.split(' ', 1).str[1].str.replace(':','')
        self.data['CH03'] = "000"
        try:
            self.data['CH04'] = self.data[[col for col in self.data.columns if (baro_ch in col and 'Avg' in col)]]
        except:
            self.data['CH04'] = "000"
        try:
            self.data['CH05'] = self.data[[col for col in self.data.columns if (temp_ch in col and 'Avg' in col)]]
        except:
            self.data['CH05'] = "000"
        try:
            self.data['CH06'] = self.data[[col for col in self.data.columns if (relh_ch in col and 'Avg' in col)]]
        except:
            self.data['CH06'] = "000"
        try:
            self.data['CH07'] = self.data[[col for col in self.data.columns if (anem1_ch in col and 'Avg' in col)]]
            self.data['CH08'] = self.data[[col for col in self.data.columns if (anem1_ch in col and 'Max' in col)]]
            self.data['CH09'] = self.data[[col for col in self.data.columns if (anem1_ch in col and 'Min' in col)]]
            self.data['CH10'] = self.data[[col for col in self.data.columns if (anem1_ch in col and 'SD' in col)]]
        except:
            self.data['CH07'], self.data['CH08'], self.data['CH09'], self.data['CH10'] = "000"
        try:
            self.data['CH11'] = self.data[[col for col in self.data.columns if (vane1_ch in col and 'Avg' in col)]]
            self.data['CH12'] = self.data[[col for col in self.data.columns if (vane1_ch in col and 'SD' in col)]]
        except:
            self.data['CH11'], self.data['CH12'] = "000"
        try:
            self.data['CH13'] = self.data[[col for col in self.data.columns if (anem2_ch in col and 'Avg' in col)]]
            self.data['CH14'] = self.data[[col for col in self.data.columns if (anem2_ch in col and 'Max' in col)]]
            self.data['CH15'] = self.data[[col for col in self.data.columns if (anem2_ch in col and 'Min' in col)]]
            self.data['CH16'] = self.data[[col for col in self.data.columns if (anem2_ch in col and 'SD' in col)]]
        except:
            self.data['CH13'], self.data['CH14'], self.data['CH15'], self.data['CH16'] = "000"
        try:
            self.data['CH17'] = self.data[[col for col in self.data.columns if (vane2_ch in col and 'Avg' in col)]]
            self.data['CH18'] = self.data[[col for col in self.data.columns if (vane2_ch in col and 'SD' in col)]]
        except:
            self.data['CH17'], self.data['CH18'] = "000"
        try:
            self.data['CH19'] = self.data[[col for col in self.data.columns if (anem3_ch in col and 'Avg' in col)]]
            self.data['CH20'] = self.data[[col for col in self.data.columns if (anem3_ch in col and 'Max' in col)]]
            self.data['CH21'] = self.data[[col for col in self.data.columns if (anem3_ch in col and 'Min' in col)]]
            self.data['CH22'] = self.data[[col for col in self.data.columns if (anem3_ch in col and 'SD' in col)]]
        except:
            self.data['CH19'], self.data['CH20'], self.data['CH21'], self.data['CH22'] = "000"


    def make_header_for_epe(self):
        array     = ['Site Number:']
        sitenum   = self.site_info.loc[self.site_info[0].isin(array)][1].to_string().split(" ")[-1]
        starttime = self.data.head(1).values[0][0].replace("-","").replace(" ","").replace(":","")
        endtime   = self.data.tail(1).values[0][0].replace("-","").replace(" ","").replace(":","")

        a1_height = str(self.anem1['Height:'].iloc[0])
        a2_height = str(self.anem2['Height:'].iloc[0])
        a3_height = str(self.anem3['Height:'].iloc[0])
        v1_height = str(self.vane1['Height:'].iloc[0])
        v2_height = str(self.vane2['Height:'].iloc[0])

        header = []

        header.append('Estaçao ' + str(sitenum))
        header.append('Início ' + str(starttime))
        header.append('Fim ' + str(endtime))
        header.append('CH01 Dia do início do intervalo (de 10 minutos) de medição [AAAMMDD]')
        header.append('CH02 Horário do início do intervalo (de 10 minutos) de medição [hhmmss]')
        header.append('CH03 Código de erro do intervalo, com "0" indicando medição sem erro')
        header.append('CH04 Pressão do ar [hPa]: média do intervalo')
        header.append('CH05 Temperatura do ar [°C]: média do intervalo')
        header.append('CH06 Umidade relativa do ar [%rel]: média do intervalo')
        header.append('CH07 Anemômetro superior '+a1_height+', velocidade do vento [m/s]: média do intervalo')
        header.append('CH08 Anemômetro superior '+a1_height+', velocidade do vento [m/s]: máximo do intervalo')
        header.append('CH09 Anemômetro superior '+a1_height+', velocidade do vento [m/s]: mínimo do intervalo')
        header.append('CH10 Anemômetro superior '+a1_height+', velocidade do vento [m/s]: desvio padrão do intervalo')
        header.append('CH11 Wind Vane superior '+v1_height+', direção de vento [°]: média do intervalo')
        header.append('CH12 Wind Vane superior '+v1_height+', direção de vento [°]: desvio padrão do intervalo')
        header.append('CH13 Anemômetro 2 '+a2_height+', velocidade do vento [m/s]: média do intervalo')
        header.append('CH14 Anemômetro 2 '+a2_height+', velocidade do vento [m/s]: máximo do intervalo')
        header.append('CH15 Anemômetro 2 '+a2_height+', velocidade do vento [m/s]: mínimo do intervalo')
        header.append('CH16 Anemômetro 2 '+a2_height+', velocidade do vento [m/s]: desvio padrão do intervalo')
        header.append('CH17 Wind Vane 2 '+v2_height+', direção de vento [°]: média do intervalo')
        header.append('CH18 Wind Vane 2 '+v2_height+', direção de vento [°]: média do intervalo')
        header.append('CH19 Anemômetro 3 '+a3_height+', velocidade do vento [m/s]: média do intervalo')
        header.append('CH20 Anemômetro 3 '+a3_height+', velocidade do vento [m/s]: máximo do intervalo')
        header.append('CH21 Anemômetro 3 '+a3_height+', velocidade do vento [m/s]: mínimo do intervalo')
        header.append('CH22 Anemômetro 3 '+a3_height+', velocidade do vento [m/s]: desvio padrão do intervalo')
        header.append('CH01|CH02|CH03|CH04|CH05|CH06|CH07|CH08|CH09|CH10|CH11|CH12|CH13|CH14|CH15|CH16|CH17|CH18|CH19|CH20|CH21|CH22|')
        header.append('dados')
        self.header = header


    def calculate_soiling_ratio(self, method="IEC", T0=25, G0=1000, alpha=0.0004,
                                I_clean_SC_0=0.900000, I_soiled_SC_0=0.900000 ):
        isc_clean_ch = "Ch" + str(self.isc_clean['Channel:'].iloc[0]) + "_"
        isc_soiled_ch = "Ch" + str(self.isc_soiled['Channel:'].iloc[0]) + "_"
        pv_clean_ch = "Ch" + str(self.pv_temp_clean['Channel:'].iloc[0]) + "_"
        pv_soiled_ch = "Ch" + str(self.pv_temp_soiled['Channel:'].iloc[0]) + "_"

        try:
            self.data['I_clean_SC'] = self.data[[col for col in self.data.columns if (isc_clean_ch in col and 'Avg' in col)]]
            self.data['I_soiled_SC'] = self.data[[col for col in self.data.columns if (isc_soiled_ch in col and 'Avg' in col)]]
            self.data['T_clean'] = self.data[[col for col in self.data.columns if (pv_clean_ch in col and 'Avg' in col)]]
            self.data['T_soiled'] = self.data[[col for col in self.data.columns if (pv_soiled_ch in col and 'Avg' in col)]]

        except:
            print("error replicating ISC or PV data")

        if method == "IEC":
            try:
                # calculate G
                self.data['G'] = G0 * (self.data['I_clean_SC'] * (1 - alpha * (self.data['T_clean'] - T0))) / I_clean_SC_0
            except:
                print("could not calculate G column")
            try:
                # calculate SR
                self.data['SR'] = self.data['I_soiled_SC'] / (I_soiled_SC_0 * (1 + (alpha * (self.data['T_soiled'] - T0))) * (self.data['G'] / G0))
            except:
                print("could not calculate SR column")


    def output_txt_file(self, epe=False, soiling=False, standard=True,
                        shift_timestamps=False, out_file='', **kwargs):

        out_dir = kwargs.get('out_dir', '')

        if epe == True:
            if out_file != '':
                output_name = out_file
            else:
                output_name = self.out_file[:-4]+"_EPE.txt"
            print("\nOutputting file: {0}   ...   ".format(output_name), end="", flush=True)

            try:
                output_file = open(output_name, 'w+', encoding='utf-16')
                output_file.truncate()
                self.select_channels_for_reformat(epe=True)
                self.format_data_for_epe()

                for line in self.header:
                    try:
                        output_file.write(line + "\n")
                    except:
                        pass
                output_file.close()

                col_prefix = "CH"
                cols = []
                for i in range(1,23,1):
                    col_num  = str(i).zfill(2)
                    col_name = col_prefix + str(col_num)
                    cols.append(col_name)
                self.cols = cols

                with open(output_name, 'a', encoding='utf-16') as f:
                    self.data.to_csv(f, header=False, sep="|", columns=cols, index=False,
                                    index_label=False, decimal=",", line_terminator="|\n",
                                    float_format='%.2f')

                f.close()
                print("[OK]")

            except Exception as e:
                print("[FAILED]")
                print(e)

        else:
            if soiling == True:
                if out_file != '':
                    output_name = out_file
                else:
                    output_name = self.out_file[:-4]+"_soiling.txt"

                output_file = open(output_name, 'w+', encoding = 'utf-8')
                output_file.truncate()
                output_file.write(self.head)
                output_file.close()

                # write header
                with open(output_name, 'a', encoding='utf-8') as f:
                    self.site_info.to_csv(f, header=False, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")

                output_file.close()

                #write data
                with open(output_name, 'a', encoding='utf-8') as f:
                    self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")
                output_file.close()


            if shift_timestamps == True:

                os.makedirs(out_dir, exist_ok=True)
                file_date = str(self.data.iloc[0]['Timestamp']).replace(" ","_").replace(":",".")[:-3]
                file_num = self.filename.split("_")[len(self.filename.split("_")) - 2]
                file_name = "{0}_{1}_{2}_meas.txt".format(self.site_number, file_date, file_num)
                output_name = os.path.join(out_dir, file_name)

                self.output_name = output_name
                output_file = open(output_name, 'w+', encoding = 'utf-8')
                output_file.truncate()
                output_file.write(self.head)
                output_file.close()

                with open(output_name, 'a', encoding='utf-8') as f:
                    try:
                        self.site_info = self.site_info.replace(self.first_timestamp,str(self.data.iloc[0]['Timestamp']))
                    except:
                        print("couldn't rename 'Effective Date:' info in {0}".format(output_name))
                        pass
                    self.site_info.to_csv(f, header=False, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")

                output_file.close()

                with open(output_name, 'U') as f:
                    text = f.read()
                    while '\t\n' in text:
                        text = text.replace('\t\n','\n')

                with open(output_name, 'w') as f:
                    f.write(text)

                with open(output_name, 'a', encoding='utf-8') as f:
                    self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")

                output_file.close()
                self.insert_blank_header_rows(output_name)

            if standard == True:
                if out_file != '':
                    output_name = out_file
                else:
                    output_name = self.out_file[:-4]+"_standard.txt"

                print("\nOutputting file: {0}   ...   ".format(output_name), end="", flush=True)

                try:
                    output_file = open(output_name, 'w+', encoding = 'utf-8')
                    output_file.truncate()
                    output_file.write(self.head)
                    output_file.close()

                    # write header
                    with open(output_name, 'a', encoding='utf-8') as f:
                        self.site_info.to_csv(f, header=False, sep="\t", index=False,
                                            index_label=False, line_terminator="\n")
                    output_file.close()

                    #write data
                    with open(output_name, 'a', encoding='utf-8') as f:
                        self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                            index_label=False, line_terminator="\n")
                    output_file.close()
                    self.insert_blank_header_rows(output_name)
                    print("[OK]")

                except Exception as e:
                    print("[FAILED]")
                    print(e)


    def insert_blank_header_rows(self,filename):
        """insert blank rows when using shift_timestamps()

        ensures the resulting text file looks and feels like an
        original Sympro Desktop exported
        """
        header_section_headings = ["Export Parameters",
                                   "Site Properties",
                                   "Logger History",
                                   "iPack History",
                                   "Sensor History",
                                   "Data"]

        blank_list = []
        for i in self.site_info[self.site_info[0].str.contains("Export Parameters") == True].index:
          blank_list.append(i)
          export_parameter_line = i + 2

        for i in self.site_info[self.site_info[0].str.contains("Site Properties") == True].index:
           blank_list.append(i)
           site_properties_line = i + 2

        for i in self.site_info[self.site_info[0].str.contains("Logger History") == True].index:
            blank_list.append(i)
            logger_history_line = i + 2

        for i in self.site_info[self.site_info[0].str.contains("iPack History") == True].index:
            blank_list.append(i)
            ipack_history_line = i + 2

        for i in self.site_info[self.site_info[0].str.contains("Sensor History") == True].index:
            blank_list.append(i)
            sensor_history_line = i + 2

        skip_first_channel = True
        for i in self.site_info[self.site_info[0].str.contains("Channel:") == True].index:
           if skip_first_channel == True:
                skip_first_channel = False
           else:
              blank_list.append(i)

        for i in self.site_info[self.site_info[0].str.match("Data") == True].index:
           blank_list.append(i)
           data_line = i + 2

        for i in self.site_info[self.site_info[0].str.contains("Data Type:") == True].index:
            blank_list.remove(i)

        for i in self.site_info[self.site_info[0].str.contains("Data Logging Mode:") == True].index:
            blank_list.remove(i)

        f_read = open(filename, 'r')
        contents = f_read.readlines()
        f_read.close()

        contents[export_parameter_line] = header_section_headings[0] + '\n'
        contents[site_properties_line]  = header_section_headings[1] + '\n'
        contents[logger_history_line]   = header_section_headings[2] + '\n'
        contents[ipack_history_line]    = header_section_headings[3] + '\n'
        contents[sensor_history_line]   = header_section_headings[4] + '\n'
        contents[data_line]             = header_section_headings[5] + '\n'

        for i in list(reversed(sorted(blank_list))):
            contents.insert(i+2, "\n")

        f_write = open(filename, 'w')
        contents = "".join(contents)
        f_write.write(contents)
        f_write.close()


def shift_timestamps(txt_folder="", out_folder="", file_filter="",
                     start_date="1970-01-01", end_date="2150-12-31",
                     seconds=3600):
    """Takes as input a folder of exported standard text files and
    time to shift in seconds.

    Parameters
    ----------
    txt_folder : str
        path to folder with txt files to shift
    out_folder : str
        where to put the shifted files (in subfolder by default)
    file_filter : str
        filter for restricting file set
    start_date : str
        date filter "YYYY-mm-dd"
    end_date : str
        date filter "YYYY-mm-dd"
    seconds : int
        time in seconds to shift timestamps (default 3600)

    Returns
    -------
    obj
        text files with shifted timestamps; new file names include shifted
        timestamp.

    """
    if out_folder:
        out_dir = out_folder
    else:
        out_dir = os.path.join(txt_folder, "shifted_timestamps")

    os.makedirs(out_dir, exist_ok=True)

    files = [
        f for f in sorted(glob(txt_folder + "/" + '*.txt'))\
        if file_filter in f and \
        date_check(start_date, end_date, f)
    ]

    file_count = len(files)
    counter = 1
    start_time = datetime.now()

    for f in files:

        try:
            draw_progress_bar(counter, file_count, start_time)
            f = os.path.join(txt_folder, f)
            fut = sympro_txt_read(filename=f)
            fut.format_site_data()
            fut.data['Timestamp'] = pd.to_datetime(fut.data['Timestamp']) + timedelta(seconds=seconds)
            fut.output_txt_file(shift_timestamps=True, standard=False, out_dir=out_dir, out_file=f)
        except pd.errors.EmptyDataError:
            pass

        except Exception as e:
            print(traceback.format_exc())
            pass

        counter += 1

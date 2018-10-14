#!/bin/usr/python
import datetime
from datetime import datetime, timedelta
import os
import pandas as pd
import re


class sympro_txt_read(object): # object is path to SPRO_export.txt file
    
    # read txt file into data, site_info and ch_info dataframes
    def __init__(self, filename='', **kwargs):
        self.filename = filename
        self.filter = kwargs.get('filter', '')
        
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
            self.site_info = self.site_info.iloc[:self.site_info.ix[self.site_info[0]=='Data'].index.tolist()[0]+1]
            self.data = pd.read_csv(self.filename, skiprows=header_len, sep="\t", encoding='iso-8859-1')
            self.first_timestamp = self.data.iloc[0]['Timestamp']
            self.arrange_ch_info()
        else:
            print('instance created, no filename specified')
        
    def __repr__(self):
        return '<class {}: {} >'.format(self.__class__.__name__,self.filename)
    
    def arrange_ch_info(self): # create dataframe of channel info
        array = ['Channel:',
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
                 'P-SCM Type:']


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

    def concat_txt(self, output_txt=False, txt_dir='', out_file='',
                    header='standard', **kwargs):
        self.filter = kwargs.get('filter', '')
        first_file = True
        for f in sorted(os.listdir(txt_dir)):
            if self.filter in f:
                print("Adding {0} ...\t\t".format(f), end="", flush=True)
                if first_file == True:
                    first_file = False
                    try:
                        base = sympro_txt_read(txt_dir + f)
                        print("[OK]")
                        pass
                    except IndexError:
                        print('Only standard SymPRO headertypes accepted')
                        break
                else:
                    file_path = txt_dir + f
                    try:
                        s = sympro_txt_read(file_path)
                        base.data = base.data.append(s.data, sort=False)
                        print("[OK]")
                    except:
                        print("[FAILED]")
                        print("could not concat {0}".format(file_path))
                        pass
            else:
                pass
        if output_txt == True:
            if out_file == "":
                out_file = datetime.datetime.today().strftime("%Y-%m-%d") + "_SymPRO.txt"
            base.data.to_csv(txt_dir + out_file, sep=',', index=False)
        self.ch_info = s.ch_info
        self.ch_list = s.ch_list
        self.data = base.data.drop_duplicates(subset=['Timestamp'], keep='first')
        self.head = s.head
        self.site_info = s.site_info
        
        
    def select_channels(self, epe=False, soiling=False): 
        # for EPE formatting
        ch_anem = ['Anem','Anemometer','anem','anemometer','Anemômetro','anemômetro']
        ch_vane = ['Vane','vane','Direction','direction','Veleta','veleta','Direção','direção','Vane w/Offset']
        ch_baro = ['mb','hpa','hPa','millibar','kPa']
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
            self.make_header()

        # select channels needed for soiling calculation
        if soiling == True:
            try:
                self.isc_clean = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_clean_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_I_units))))]
                self.isc_soiled = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_soiled_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_I_units))))]
                self.pv_temp_clean = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_clean_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_temp))))]
                self.pv_temp_soiled = self.ch_info.loc[(self.ch_info['Description:'].str.lower().str.contains('|'.join(ch_soiled_desc)) & (self.ch_info['Units:'].str.lower().str.contains('|'.join(ch_temp))))]
            except:
                print("SC and PV Temp fields unavailable for calculation")
        return self

    def format_data(self):
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

        return self 

    def make_header(self):
        array     = ['Site Number:']
        sitenum   = self.site_info.loc[self.site_info[0].isin(array)][1].to_string().split(" ")[-1]
        starttime = self.data.head(1).as_matrix()[0][0].replace("-","").replace(" ","").replace(":","")
        endtime   = self.data.tail(1).as_matrix()[0][0].replace("-","").replace(" ","").replace(":","")

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

        return self

    
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
                
        if method == "IEEE":
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


    def output_txt_file(self, output_type='standard', epe=False, soiling=False, standard=False, 
                        shift_timestamps=False):
        if output_type == 'epe':
            output_name = self.filename[:-4]+"_EPE.txt"
            output_file = open(output_name, 'w+', encoding='utf-16')
            output_file.truncate()

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
            
        else:
            if output_type == 'soiling':
                output_name = self.filename[:-4]+"_soiling.txt"
                output_file = open(output_name, 'w+', encoding = 'utf-16')
                output_file.truncate()
                output_file.write(self.head)       
                output_file.close()
                # write header
                with open(output_name, 'a', encoding='utf-16') as f:
                    self.site_info.to_csv(f, header=False, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")            
                output_file.close()
                #write data
                with open(output_name, 'a', encoding='utf-16') as f:
                    self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")
                output_file.close()
                
            if shift_timestamps == True:
                print("shifting timestamps... {0}".format(self.filename))
                cwd = os.getcwd()
                out_dir = cwd + "\\std_exports\\"
                os.makedirs(out_dir, exist_ok=True)
                site_num = self.site_info.loc[4][1]
                if datetime.strptime(self.first_timestamp, '%Y-%m-%d %H:%M:%S') > datetime(1980,1,1):
                    print("{0} skipped...".format(self.filename))
                    return self
                else:
                    file_date = str(self.data.iloc[0]['Timestamp']).replace(" ","_").replace(":",".")[:-3]
                    file_num = self.filename.split("_")[len(self.filename.split("_")) - 2]
                    file_name = site_num + '_' + file_date + '_' + file_num + "_meas.txt"
                    output_name = os.path.join(out_dir, file_name)
                    self.output_name = output_name
                output_file = open(output_name, 'w+', encoding = 'utf-8')
                output_file.truncate()
                output_file.write(self.head)       
                output_file.close()
                # write header
                with open(output_name, 'a', encoding='utf-8') as f:
                    try:
                        self.site_info = self.site_info.replace(self.first_timestamp,str(self.data.iloc[0]['Timestamp']))
                    except:
                        print("couldn't rename 'Effective Date:' info in {0}".format(output_name))
                        pass
                    self.insert_blank_header_rows()
                    self.site_info_write.to_csv(f, header=False, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")            
                output_file.close()
                with open(output_name, 'U') as f:
                    text = f.read()
                    while '\t\n' in text:
                        text = text.replace('\t\n','\n')
                with open(output_name, 'w') as f:
                    f.write(text)
                #write data
                with open(output_name, 'a', encoding='utf-8') as f:
                    self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")
                output_file.close()
                
            if output_type == 'standard':
                output_name = self.filename[:-4]+"_standard.txt"
                output_file = open(output_name, 'w+', encoding = 'utf-16')
                output_file.truncate()
                output_file.write(self.head)       
                output_file.close()
                # write header
                with open(output_name, 'a', encoding='utf-16') as f:
                    self.site_info.to_csv(f, header=False, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")            
                output_file.close()
                #write data
                with open(output_name, 'a', encoding='utf-16') as f:
                    self.data.round(6).to_csv(f, header=True, sep="\t", index=False,
                                        index_label=False, line_terminator="\n")
                output_file.close()

        
        return self
    
    def insert_blank_header_rows(self):
        """
            function used to insert blank rows when using shift_timestamps() 
            function so that the resulting text file looks and feels like an
            original Sympro Desktop exported
        """
        blank_list = []
        for i in self.site_info[self.site_info[0].str.contains("Export Parameter")==True].index:
          blank_list.append(i)
        
        for i in self.site_info[self.site_info[0].str.contains("Site Properties")==True].index:
           blank_list.append(i)
    
        for i in self.site_info[self.site_info[0].str.contains("Logger History")==True].index:
            blank_list.append(i)

        for i in self.site_info[self.site_info[0].str.contains("iPack History")==True].index:
            blank_list.append(i)

        for i in self.site_info[self.site_info[0].str.contains("Sensor History")==True].index:
            blank_list.append(i)

        skip_first_channel = True
        for i in self.site_info[self.site_info[0].str.contains("Channel:")==True].index:
           if skip_first_channel == True:
                skip_first_channel = False
           else:
              blank_list.append(i)

        for i in self.site_info[self.site_info[0].str.match("Data")==True].index:
           blank_list.append(i)

        for i in self.site_info[self.site_info[0].str.contains("Data Type:")==True].index:
            blank_list.remove(i)
    
        self.site_info_write = self.site_info

        line = pd.DataFrame({0: "", 1: ""}, index=[2])
        i = 0
        for ind in blank_list:
           self.site_info_write = pd.concat([self.site_info_write.iloc[:i+ind], line, self.site_info_write.iloc[i+ind:]]).reset_index(drop=True)
           i = i + 1
           
        return self
    
def shift_timestamps(txt_folder="", seconds=3600, output_txt=True):
    """
        Takes as input a folder of exported standard text files and
        time to shift in seconds.
        
    """    
    file_list = []
    for f in sorted(os.listdir(txt_folder)):
        try:
            f = os.path.join(txt_folder, f)
            fut = sympro_txt_read(f)
            fut.data['Timestamp'] = pd.to_datetime(fut.data['Timestamp']) + timedelta(seconds=seconds)
            if output_txt == True:
                fut.output_txt_file(shift_timestamps=True)
                file_list.append(fut.output_name)
        except:
            print("unable to process {0}".format(f))
            pass
    out_dir = txt_folder + "\\std_exports\\"
    for f in sorted(os.listdir(out_dir)):
        first_file = os.path.join(out_dir, f)
        break
    concat_txt = sympro_txt_read(first_file)
    skip_file = True # remove first file from list
    for f in sorted(os.listdir(out_dir)):
        if skip_file == True:
            skip_file = False
            pass
        else:
            f = os.path.join(out_dir, f)
            _fut = sympro_txt_read(f)
            concat_txt.data = pd.concat([concat_txt.data,_fut.data])
    concat_txt.output_txt_file(standard=True)
    return concat_txt


    
import pandas as pd
import os
from datetime import datetime
import argparse
import re
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument('--website_name', type=str, required=True)
parser.add_argument('--decode_weather_code', type=str,default='False', required=False)

args = parser.parse_args()

website_name = args.website_name.split('.')[0].lower()
print('Website:',website_name)
decode_weather_code = str(args.decode_weather_code).lower() == "true"
print('Decode_weather_code:',decode_weather_code)
dir_path = os.path.join(os.getcwd(),'data',f'{website_name}')
un_preprocessed_dir_path = os.path.join(dir_path,'un_preprocessed')
preprocessed_dir_path = os.path.join(dir_path,'preprocessed')

def Preprocess_Meteo_Data(dir_path):
    weather_dict = {
    0: 'Unknown',
    1: 'Clear',
    2: 'Fair',
    3: 'Cloudy',
    4: 'Overcast',
    5: 'Fog',
    6: 'Freezing Fog',
    7: 'Light Rain',
    8: 'Rain',
    9: 'Heavy Rain',
    10: 'Freezing Rain',
    11: 'Heavy Freezing Rain',
    12: 'Sleet',
    13: 'Heavy Sleet',
    14: 'Light Snowfall',
    15: 'Snowfall',
    16: 'Heavy Snowfall',
    17: 'Rain Shower',
    18: 'Heavy Rain Shower',
    19: 'Sleet Shower',
    20: 'Heavy Sleet Shower',
    21: 'Snow Shower',
    22: 'Heavy Snow Shower',
    23: 'Lightning',
    24: 'Hail',
    25: 'Thunderstorm',
    26: 'Heavy Thunderstorm',
    27: 'Storm',
    1000: 'Unknown'
    }
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"):
            try: 
                csv_file = os.path.join(dir_path, filename)
                me_data=pd.read_csv(csv_file,index_col=[0])
                me_data = me_data.rename(columns={'time':'Time','temp':'Temp(C)', 'dwpt':'Dew_point(C)','rhum':'Humidity(%)', 'prcp':'Precipitation(mm)','snow':'Snow_Depth','wdir':'Wind_direct','wspd':'Wind_speed(km/h)','wpgt':'Peak_gust','pres':'Barometer(mbar)','tsun':'Sunshine_duration',	'coco':'Weather'})
                me_data['Time']=[datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')for date in me_data['Time']]
                me_data['Temp(C)'] = [float(temp) for temp in me_data['Temp(C)']]
                me_data['Weather'] = me_data['Weather'].fillna(1000).astype(int)
                me_data['Barometer(mbar)'] = me_data['Barometer(mbar)'].fillna(1100).astype(int)
                if decode_weather_code:
                    me_data['Weather'] = [weather_dict[code] for code in me_data['Weather']]
                me_data.to_csv(os.path.join(preprocessed_dir_path,filename))
            except Exception as err:
                print(f"{type(err).__name__} was raised {err}")#print the error
                print("Dataset is already preprocessed!")
    return

def Preprocess_Timeandate_Data(dir_path):
    def correct_Temp(temp):
        new_temp = float(str(temp).replace("°F","").replace("°C",""))
        # new_temp = (new_temp - 32) / 1.8
        return np.round(new_temp,1)
    def correct_Windspeed(wind_speed):
        new_wind_speed = float(str(wind_speed).replace("km/h","").replace("mi","").replace("No wind",'0').replace("nan",'9999'))
        return int(new_wind_speed)
    def correct_Barometer(barometer):
        new_barometer = float(str(barometer).replace("mbar","").replace("hg","").replace("nan","9999"))
        return int(new_barometer)
    def correct_Visibility(visibility):
        new_visibility = float(str(visibility).replace("mi","").replace("km","").replace("nan","9999"))
        return int(new_visibility)
    def correct_month(date):
        char_to_replace = {'januari':'January', 
                           'februari':'February', 
                           'maart':'March', 
                           'april':'April',
                           'mei':'May', 
                           'juni':'June', 
                           'juli':'July', 
                           'augustus':'August', 
                           'september':'September', 
                           'oktober':'October', 
                           'november':'November',
                           'december':'December',
                           'Jan':'January', 
                           'Feb':'February', 
                           'Mar':'March', 
                           'Apr':'April', 
                           'Jun':'June', 
                           'Jul':'July', 
                           'Aug':'August', 
                           'Sep':'September', 
                           'Oct':'October', 
                           'Nov':'November',
                           'Dec':'December',
                           }
        pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in char_to_replace.keys()) + r')\b')
        # Replace matched words with corresponding values from the dictionary
        result = pattern.sub(lambda x: char_to_replace[x.group()],str(date)).replace("-"," ")
        return " ".join(result.split(" ")[:2])
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"): 
            print(filename)
            try:
                csv_file = os.path.join(dir_path, filename)
                tad_data = pd.read_csv(csv_file)
                tad_data = tad_data.iloc[1:]
                # Iterate over all key-value pairs in dictionary
                tad_data['Date']=[correct_month(date) for date in tad_data['Date']]
                tad_data = tad_data.dropna(subset=['Date'])
                tad_data = tad_data.dropna(subset=['Year'])
                tad_data['Date']=tad_data['Date'].astype(str) +' '+ tad_data['Year'].astype(int).astype(str)
                
                tad_data = tad_data.drop(columns='Year')
                tad_data['Date']=pd.to_datetime(tad_data['Date'], format='%d %B %Y')
                tad_data['Time']=[datetime.combine(data['Date'],datetime.strptime(data['Time'][:5],"%H:%M").time()) for index,data in tad_data.iterrows()]
                tad_data = tad_data.drop(columns=['Date'])
                
                tad_data['Temp'] = [correct_Temp(data['Temp'])for index,data in tad_data.iterrows()]
                tad_data['Wind_speed'] = [correct_Windspeed(data['Wind_speed'])for index,data in tad_data.iterrows()]
                
                tad_data['Barometer'] = [correct_Barometer(data['Barometer'])for index,data in tad_data.iterrows()]
                tad_data['Visibility'] = [correct_Visibility(data['Visibility'])for index,data in tad_data.iterrows()]
                
                tad_data['Wind_direct'] = tad_data["Wind_direct"].str.replace("°","").astype(int)
                tad_data = tad_data.rename(columns={'Temp':'Temp(C)','Wind_speed':'Wind_speed(km/h)','Humidity':'Humidity(%)','Barometer':'Barometer(mbar)','Visibility':'Visibility(km)'})
                tad_data['Humidity(%)'] = tad_data['Humidity(%)'].fillna(9999).astype(int)
                tad_data = tad_data.drop_duplicates(subset=['Time']).sort_values(by='Time').reset_index(drop=True)
                if os.path.isfile(os.path.join(preprocessed_dir_path,filename)):
                    old_data = pd.read_csv(os.path.join(preprocessed_dir_path,filename), index_col=0)
                    old_data['Time'] = pd.to_datetime(old_data['Time'])
                    tad_data = pd.concat([old_data, tad_data], ignore_index=True, sort=False).drop_duplicates(subset=['Time']).sort_values(by='Time').reset_index(drop=True)
                tad_data.to_csv(os.path.join(preprocessed_dir_path,filename))
            except Exception as err:
                print(f"{type(err).__name__} was raised {err}")#print the error
                print("Dataset is already preprocessed!")
    return

if website_name == 'meteostat':
    Preprocess_Meteo_Data(dir_path=un_preprocessed_dir_path)
elif website_name == 'timeanddate':
    Preprocess_Timeandate_Data(dir_path=un_preprocessed_dir_path) 


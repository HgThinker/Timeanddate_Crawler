import pandas as pd
import os
from datetime import datetime
import argparse

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
                           'december':'December'
                           }
        for key, value in char_to_replace.items():
        # Replace key character with value character in string
            date = date.replace(key, value)
        return date
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"):
            try:
                csv_file = os.path.join(dir_path, filename)
                tad_data = pd.read_csv(csv_file, index_col=[0])
                tad_data = tad_data.drop(columns=['Year','Province'])
                tad_data = tad_data.iloc[1:]
                # Iterate over all key-value pairs in dictionary
                tad_data['Date']=[datetime.strptime(correct_month(date), "%d %B %Y") for date in tad_data['Date']]
                tad_data['Time']=[datetime.combine(data['Date'],datetime.strptime(data['Time'][:5],"%H:%M").time()) for index,data in tad_data.iterrows()]
                tad_data = tad_data.drop(columns=['Date'])
                tad_data['Temp'] = tad_data["Temp"].str.replace("°C","").astype(float)
                tad_data['Wind_speed'] = tad_data["Wind_speed"].str.replace("km/h","").replace("No wind",'0').astype(float)
                tad_data['Barometer'] = tad_data["Barometer"].str.replace("mbar","").astype(float)
                tad_data['Visibility'] = tad_data["Visibility"].str.replace("km","").astype(float)
                tad_data['Wind_direct'] = tad_data["Wind_direct"].str.replace("°","").astype(float)
                tad_data = tad_data.rename(columns={'Temp':'Temp(C)','Wind_speed':'Wind_speed(km/h)','Humidity':'Humidity(%)','Barometer':'Barometer(mbar)','Visibility':'Visibility(km)'})
                tad_data['Humidity(%)'] = tad_data['Humidity(%)'].astype(float)
                tad_data.to_csv(os.path.join(preprocessed_dir_path,filename))
            except Exception as err:
                print(f"{type(err).__name__} was raised {err}")#print the error
                print("Dataset is already preprocessed!")
    return

if website_name == 'meteostat':
    Preprocess_Meteo_Data(dir_path=un_preprocessed_dir_path)
elif website_name == 'timeandate':
    Preprocess_Timeandate_Data(dir_path=un_preprocessed_dir_path) 


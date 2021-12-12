# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 17:09:43 2021

@author: castr
"""

#%% Libraries

import datetime as dt
import pandas as pd
import requests
import pickle
import os
import pathlib

# Import apikey
with open(pathlib.Path(__file__).parents[0].joinpath('../accuweatherapikey.txt').resolve()) as f:
    apikey = f.read()
    f.close()

#%% Location Information

def get_location_keys(apikey, path = pathlib.Path(__file__).parent.joinpath("./archive/city_parameters").resolve()):
    
    # This is location inforamtion
    accuweather_location_path = 'http://dataservice.accuweather.com/locations/v1/topcities/150'
    accuweather_params = {'apikey': apikey}
    r = requests.get(accuweather_location_path, params=accuweather_params)
    data_location = r.json()
    
    data_location_formatted = {}
    for i,e in enumerate(data_location):
        # print('key:'+e['LocalizedName'] + '|||value:' + 'element')
        data_location_formatted[e['LocalizedName']] = e
    
    # Save the dictionary somewhere. Implement logging.
    a_file = open(str(path) + '\\' + 'city_parameters.pkl', "wb") # Here work with a pathlib.Path(__file__).parent
    pickle.dump(data_location_formatted, a_file)
    a_file.close()
    
    return None

def read_cities_params(path = pathlib.Path(__file__).parent.joinpath('./archive/city_parameters').resolve()):
    pkls = os.listdir(path)
    a_file = open(str(path) + '\\' + pkls[0], "rb")
    output = pickle.load(a_file)
    
    return output

#%% 1Day forecast

def read_fc_pkl(path = pathlib.Path(__file__).parent.joinpath("./archive/forecast").resolve(), country_df = pd.DataFrame()):
    pkls = os.listdir(path)
    
    for file in pkls:
        a_file = open(str(path) + '\\' + file, "rb")
        output = pickle.load(a_file)
        data_1day_forecast = output
        a_file.close()
        name = file.split('_')[0]
        
        # index = pd.to_datetime(data_1day_forecast['Headline']['EffectiveDate']).tz_convert('CET')
        index = pd.to_datetime(data_1day_forecast['DailyForecasts'][0]['Date']).tz_convert('CET')
        minimum = data_1day_forecast['DailyForecasts'][0]['Temperature']['Minimum']['Value']
        maximum = data_1day_forecast['DailyForecasts'][0]['Temperature']['Maximum']['Value']
        country_dict = {index: [minimum, maximum, name]}
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=['minimum', 'maximum', 'city'])
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=['minimum', 'maximum', 'city'])
            country_df = country_df.append(df)

    return country_df

def fc1day(apikey, countryKey, country_df=pd.DataFrame(), path = pathlib.Path(__file__).parent.joinpath("./archive/forecast").resolve()):
    
    for i, key in countryKey.items():
        accuweather_forecast_1day = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/' + key + apikey + '&metric=true'
        r = requests.get(accuweather_forecast_1day)
        data_1day_forecast = r.json()
        
        path_ = path.joinpath("./" + i + '_' + str(dt.date.today()) + '-forecast.pkl').resolve()
        a_file = open(str(path_), "wb") # Here work with a pathlib.Path(__file__).parent
        pickle.dump(data_1day_forecast, a_file)
        a_file.close()
        
        
        # index = pd.to_datetime(data_1day_forecast['Headline']['EffectiveDate']).tz_convert('CET')
        index = pd.to_datetime(data_1day_forecast['DailyForecasts'][0]['Date']).tz_convert('CET')
        minimum = data_1day_forecast['DailyForecasts'][0]['Temperature']['Minimum']['Value']
        maximum = data_1day_forecast['DailyForecasts'][0]['Temperature']['Maximum']['Value']
        country_dict = {index: [minimum, maximum, i]}
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=['minimum', 'maximum', 'city'])
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=['minimum', 'maximum', 'city'])
            country_df = country_df.append(df)
        
    return country_df

#%% 24Hours historical/actual

def read_hist_pkl(path = pathlib.Path(__file__).parent.joinpath("./archive/historical").resolve(), country_df = pd.DataFrame()):
    pkls = os.listdir(path)
    
    for file in pkls:
        
        a_file = open(str(path) + '\\' + file, "rb")
        output = pickle.load(a_file)
        data_24hours_historical = list(output)
        a_file.close()
        name = file.split('_')[0]
        
        
        country_dict = {}
        for obs in data_24hours_historical:
            # extract index and clean it
            index = pd.to_datetime(obs['LocalObservationDateTime']).tz_convert('CET')
            if index.minute>30:
                index = index + dt.timedelta(minutes=60-index.minute)
            else:
                index = index - dt.timedelta(minutes=index.minute)
            
            value = obs['Temperature']['Metric']['Value']
            country_dict[index] = value
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[name])
        
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[name])
            country_df = pd.merge(country_df, df, left_on=country_df.index, right_on=df.index, how='outer').rename(columns={'key_0':'DateTimeCET'}).set_index('DateTimeCET') # Check index if all are DateTimeCET

    return country_df

def hist24h(apikey, countryKey, country_df = pd.DataFrame(), path = pathlib.Path(__file__).parent.joinpath("./archive/historical").resolve()):
    
    for i, key in countryKey.items():
        accuweather_historical_24hours = 'http://dataservice.accuweather.com/currentconditions/v1/' + key + '/historical/24' + apikey + '&metric=true'
        r = requests.get(accuweather_historical_24hours)
        data_24hours_historical = r.json()
        
        # Save the dictionary somewhere. Implement logging.
        path_ = path.joinpath("./" + i + '_' + str(dt.date.today())+ '-historical.pkl').resolve()
        a_file = open(str(path_), "wb") # Here work with a pathlib.Path(__file__).parent
        pickle.dump(data_24hours_historical, a_file)
        a_file.close()
        
        
        #With this part of the script, create function to standardize the reading of pkl files
        country_dict = {}
        for obs in data_24hours_historical:
            # extract index and clean it
            index = pd.to_datetime(obs['LocalObservationDateTime']).tz_convert('CET')
            if index.minute>30:
                index = index + dt.timedelta(minutes=60-index.minute)
            else:
                index = index - dt.timedelta(minutes=index.minute)
            
            value = obs['Temperature']['Metric']['Value']
            country_dict[index] = value
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[i])
        
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[i])
            country_df = pd.merge(country_df, df, left_on=country_df.index, right_on=df.index, how='outer').rename(columns={'key_0':'DateTimeCET'}).set_index('DateTimeCET') # Check index if all are DateTimeCET
        
    return country_df

#%% Forecast 12 hours

def read_fc12h_pkl(path = pathlib.Path(__file__).parent.joinpath("./archive/forecast12h").resolve(), country_df = pd.DataFrame()):
    pkls = os.listdir(path)
    
    for file in pkls:
        
        a_file = open(str(path) + '\\' + file, "rb")
        output = pickle.load(a_file)
        data_24hours_historical = list(output)
        a_file.close()
        name = file.split('_')[0]
        
        
        country_dict = {}
        for obs in data_24hours_historical:
            # extract index and clean it
            index = pd.to_datetime(obs['DateTime']).tz_convert('CET')
            if index.minute>30:
                index = index + dt.timedelta(minutes=60-index.minute)
            else:
                index = index - dt.timedelta(minutes=index.minute)
            
            value = obs['Temperature']['Value']
            country_dict[index] = value
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[name])
        
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[name])
            country_df = pd.merge(country_df, df, left_on=country_df.index, right_on=df.index, how='outer').rename(columns={'key_0':'DateTimeCET'}).set_index('DateTimeCET') # Check index if all are DateTimeCET

    return country_df


def fc12h(apikey, countryKey, country_df = pd.DataFrame(), path = pathlib.Path(__file__).parent.joinpath("./archive/forecast12h").resolve()):
    
    for i, key in countryKey.items():
        accuweather_fc_12hours = 'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/' + key + apikey + '&metric=true'
        r = requests.get(accuweather_fc_12hours)
        data_12hours_fc = r.json()
        
        # Save the dictionary somewhere. Implement logging.
        path_ = path.joinpath("./" + i + '_' + str(dt.date.today()) + '-forecast12h.pkl').resolve()
        
        print(path_)
        a_file = open(str(path_), "wb") # Here work with a pathlib.Path(__file__).parent
        pickle.dump(data_12hours_fc, a_file)
        a_file.close()
        
        
        #With this part of the script, create function to standardize the reading of pkl files
        country_dict = {}
        for obs in data_12hours_fc:
            # extract index and clean it
            index = pd.to_datetime(obs['DateTime']).tz_convert('CET')
            if index.minute>30:
                index = index + dt.timedelta(minutes=60-index.minute)
            else:
                index = index - dt.timedelta(minutes=index.minute)
            
            value = obs['Temperature']['Value']
            country_dict[index] = value
        
        if country_df.empty:
            country_df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[i])
        
        else:
            df = pd.DataFrame.from_dict(country_dict, orient='index', columns=[i])
            country_df = pd.merge(country_df, df, left_on=country_df.index, right_on=df.index, how='outer').rename(columns={'key_0':'DateTimeCET'}).set_index('DateTimeCET') # Check index if all are DateTimeCET
        
    return country_df



# a = fc12h(apikey, countryKey, country_df = pd.DataFrame(), path = pathlib.Path(__file__).parent.joinpath("./archive/forecast12h").resolve())
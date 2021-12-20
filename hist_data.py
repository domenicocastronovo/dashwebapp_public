# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 19:50:19 2021

@author: castr
"""

import logging
import datetime as dt
import pandas as pd
import weather_scrape_agg as wsa
import pathlib

if __name__ == '__main__':
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    path_fileh = pathlib.Path(__file__).parents[1].joinpath("./accuweather.out").resolve()
    fileh = logging.FileHandler(str(path_fileh))
    logger.addHandler(fileh)
    logger.info('running hist {}'.format(dt.datetime.now()))
    
    try:
        data_location_formatted = wsa.read_cities_params()
    
        selected_cities = ['Athens', 'Paris', 'Rome', 'Berlin', 'Hanoi', 'Rio de Janeiro', 
                           'London', 'Lisbon']
        countryKey = {k: v['Key'] for k,v in data_location_formatted.items() if k in selected_cities}
    
        hist_df = wsa.hist24h(wsa.apikey, countryKey)
        
        path__ = pathlib.Path(__file__).parent.joinpath("./datasets/hist.csv").resolve()
        try:
            hist_csv = pd.read_csv(str(path__), index_col=0)
            hist_csv = hist_csv.append(hist_df)
            hist_csv.to_csv(str(path__))
        except:
            logger.info('CSV was empty')
            hist_df.to_csv(str(path__))
            
        # Here we import for Heroku
        try:
            path__heroku = pathlib.Path(__file__).parents[1].joinpath("./dashwebapp_public/domc-project/datasets/hist.csv").resolve()
            hist_csv_heroku = pd.read_csv(str(path__heroku), index_col=0)
            hist_csv_heroku = hist_csv_heroku.append(hist_df)
            hist_csv_heroku.to_csv(str(path__heroku))
        except:
            logger.info('CSV was empty')
            hist_df.to_csv(str(path__heroku))

        
        
    except:
        logger.exception('Error')


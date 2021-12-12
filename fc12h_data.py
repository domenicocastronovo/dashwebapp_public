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
    logger.info('running {}'.format(dt.datetime.now()))
    
    try:
        data_location_formatted = wsa.read_cities_params()
    
        selected_cities = ['Athens', 'Paris', 'Rome', 'Berlin']
        # selected_cities = ['Athens']
        countryKey = {k: v['Key'] for k,v in data_location_formatted.items() if k in selected_cities}
        
        fc_df = wsa.fc12h(wsa.apikey, countryKey)
        fc_df.loc[:, 'query'] = fc_df.index.min()
        
        path__ = pathlib.Path(__file__).parent.joinpath("./datasets/fc.csv").resolve()
        try:
            fc_csv = pd.read_csv(str(path__), index_col=0)
            fc_csv = fc_csv.append(fc_df)
            fc_csv.to_csv(str(path__))
        except:
            logger.info('CSV was empty')
            fc_df.to_csv(str(path__))
        
    except:
        logger.exception('Error')
        
        
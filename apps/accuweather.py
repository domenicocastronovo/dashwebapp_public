# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 21:14:36 2021

@author: castr
"""

from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import datetime as dt
import pathlib
from app import app

import plotly.graph_objects as go

#%% Page Structure and TODO

'''
Structure and TODOs

- Headline
- Description explaining what they are seeing and why I did it.
- city filter | DateTime Filter.
- comparison plot.
- historical plot (?) Historical is already in comparison plot. Maybe pull more historical if api allows.
- Table of errors and more statistics.
- Map of with MAE.

'''
#%% Alpha ISO 3

iso = {'Athens':'GRC', 'Berlin':'DEU', 'Paris':'FRA', 'Rome':'ITA',
       'Hanoi':'VNM', 'Rio de Janeiro':'BRA', 'London':'GBR', 'Lisbon':'PRT',
       'Bangkok': 'THA', 'Dublin': 'IRL', 'Cape Town': 'ZAF', 'Warsaw': 'POL',
       'Tokyo': 'JPN', 'Minsk': 'BLR', 'Seoul': 'KOR'}


#%% Prepare DataFrames

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

dfh = pd.read_csv(DATA_PATH.joinpath("hist.csv"), index_col=0)
dfh.index = pd.to_datetime(dfh.index)
dfh = dfh.loc[~dfh.index.duplicated()]
dfh.sort_index(inplace=True)

dff = pd.read_csv(DATA_PATH.joinpath("fc.csv"), index_col=0)
dff.index = pd.to_datetime(dff.index)
dff = dff.add_prefix('fc_')
dff = dff.loc[~dff.index.duplicated(keep='last')] # to be fixed
dff.sort_index(inplace=True)

df_merged_noindex = pd.merge(dfh, dff, left_on=dfh.index, right_on=dff.index, how='inner').rename(columns = {'key_0':'DateTimeCET'}).set_index('DateTimeCET')
df_merged_noindex.sort_index(inplace=True)

df_merged = pd.DataFrame(index=pd.date_range(start=df_merged_noindex.index.min(),
                                             end=df_merged_noindex.index.max(),
                                             freq='H'))
df_merged = pd.merge(df_merged, df_merged_noindex, left_on=df_merged.index, 
                     right_on=df_merged_noindex.index, how='outer').rename(columns = {'key_0':'DateTimeCET'}).set_index('DateTimeCET')
df_merged.fc_query = df_merged.fc_query.ffill()


#%% Dash-Plotly

layout = html.Div([
    html.P('''
           My personal and professional interest in temperature forecasts inspired me 
           to create this dashboard. The purpose of this project is to evaluate the 
           accuracy of temperature forecasts provided by accuweather.
           Send me a message to the following profile if you notice any error or, simply, for 
           any feedback: https://www.linkedin.com/in/domenico-castronovo/ .
           If you are interested in the project's backend, please clone the following 
           repository: https://github.com/domenicocastronovo/dashwebapp_public .
           '''),
    html.H1('Accuweather Project', style={"textAlign": "center"}),
    html.H4('Data is updated every 12 hours, at 8am and 8pm. The process is automated but located in my local machine which causes missing data when access to internet is limited :/', style={"textAlign": "left"}),
    html.H1('______', style={"textAlign": "center"}),
    html.H5('''
            This Section shows the comparison between 12 hours forecast and historical data.
            ''', style={"textAlign": "center"}), 
    html.H6('''
            Below you can choose the time-frame and the city to visualize for this section.
            ''', style={"textAlign": "center"}), 

    html.Div([
        html.Div(dcc.Dropdown(
            id='city-dropdown', value='Athens', clearable=False,
            options=[{'label': x, 'value': x} for x in sorted([i for i in dfh.columns])],
            multi=False
        ), className='six columns'),
    
        
        html.Div(dcc.DatePickerRange(id='date-range',
                                     min_date_allowed=dfh.index.min(),
                                     max_date_allowed=dff.index.max(),
                                     initial_visible_month=dff.index.min(),
                                     end_date=dff.index.max(),
                                     start_date=dfh.index.max() - dt.timedelta(days=7)
        ), className='six columns'),
        
    ], className='row'),

    dcc.Graph(id='plot-comparison', figure={}),
    
    
    # dcc.Graph(id='plot-historical', figure={}),
    html.H1('______', style={"textAlign": "center"}),
    html.H5('''
            This Section shows descriptive statistics for both 12 hours forecast and historical data.
            ''', style={"textAlign": "center"}), 
    html.H6('''
            Below you can choose the time-frame and the cities to visualize for this section.
            ''', style={"textAlign": "center"}), 

    html.Div([
        html.Div(dcc.Dropdown(
            id='city-dropdown-multiple', value=['Athens', 'Berlin', 'Paris', 'Rome'], clearable=False,
            options=[{'label': x, 'value': x} for x in sorted([i for i in dfh.columns])],
            multi=True
        ), className='six columns'),        
    ], className='row'),
    
    dcc.Graph(id='boxplot-comparison', figure={}),
    dcc.Graph(id='table-comparison-described', figure={}),
    dcc.Graph(id='table-comparison-maes', figure={}),
    dcc.Graph(id='choro-mae-map', figure={}),

            
])

@app.callback(
    Output(component_id='plot-comparison', component_property='figure'),
    Input(component_id='city-dropdown', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)
def comparison(city_chosen, start_date, end_date):
    # print(city_chosen)
    # print(start_date, end_date)
    all_value = [i for i in df_merged.columns if str(city_chosen) in i or 'query' in i]
    dropdown_value = [i for i in df_merged.columns if str(city_chosen) in i]
    # print(dropdown_value)
    df_merged_copy = df_merged.copy()
    df_merged_copy = df_merged_copy[all_value]
    
    
    df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]
    
    
    
    # Using Plotly Graph Object
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_merged_copy.index, y=df_merged_copy[dropdown_value[0]],
                              mode='lines+markers', name=dropdown_value[0]))
    fig.add_trace(go.Scatter(x=df_merged_copy.index, y=df_merged_copy[dropdown_value[1]],
                              mode='lines+markers', name=dropdown_value[1]))
    for query in df_merged_copy.fc_query.unique():
        fig.add_vline(x=pd.to_datetime(query), line_width=2, line_dash="dash", line_color="green")
        
    fig.update_layout(yaxis_title = 'Celsius Degrees', 
                      title = 'Front 12 Hours Forecast and Historical Temperature (Celsius) Data Comparison ***The green vertical line represents the Datetime at which the 12 hours forecast was pulled from the data provider***')
    
    return fig

# @app.callback(
#     Output(component_id='plot-historical', component_property='figure'),
#     Input(component_id='city-dropdown', component_property='value'),
#     Input(component_id='date-range', component_property='start_date'),
#     Input(component_id='date-range', component_property='end_date')
# )
# def historical(city_chosen, start_date, end_date):
#     # print(city_chosen)
#     dropdown_value = [i for i in dfh.columns if str(city_chosen) in i]
#     # print(dropdown_value)
#     df_merged_copy = dfh.copy()
#     df_merged_copy = dfh[dropdown_value]
    
#     df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]
#     # print(df_merged_copy)
#     fig = px.line(df_merged_copy, x=df_merged_copy.index, y=city_chosen, title='Historical Values', markers=True)
#     fig.update_layout(yaxis_title='Historical Value')
#     return fig

@app.callback(
    Output(component_id='boxplot-comparison', component_property='figure'),
    Input(component_id='city-dropdown-multiple', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)
def box_plot(city_list, start_date, end_date):
    
    dropdown_value = []
    for city in list(city_list):  
        dropdown_value_city = [i for i in df_merged.columns if str(city) == i]
        dropdown_value = dropdown_value + dropdown_value_city
    
    df_merged_copy = df_merged.copy()
    df_merged_copy = df_merged_copy[dropdown_value]
    df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]
    
    box = go.Figure()
    for city in dropdown_value:
        box.add_trace(go.Box(y=df_merged_copy[city], name=city))
    
    box.update_layout(yaxis_title = str(dropdown_value), 
                      title = 'Historical Temperature (Celsius) Data BoxPlot')
        
    return box

@app.callback(
    Output(component_id='table-comparison-described', component_property='figure'),
    Output(component_id='table-comparison-maes', component_property='figure'),
    Output(component_id='choro-mae-map', component_property='figure'),
    Input(component_id='city-dropdown-multiple', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)
def table_statistics(city_list, start_date, end_date):
    
    dropdown_value = []
    dropdown_value_mae = []
    for city in list(city_list):  
        dropdown_value_city = [i for i in df_merged.columns if str(city) in i]
        dropdown_value = dropdown_value + dropdown_value_city
        dropdown_value_mae.append(dropdown_value_city)
                
    df_merged_copy = df_merged.copy()
    df_merged_copy = df_merged_copy[dropdown_value]
    df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]

    maes = {}
    for city in list(dropdown_value_mae):
        df_mae = df_merged_copy[city]
        mae = abs(df_mae[city[0]]-df_mae[city[1]])
        maes[city[0]] = round(mae.sum()/mae.count(), 2)
        
        
    df_merged_copy_described = df_merged_copy.describe().round(2).reset_index()
    df_maes = pd.DataFrame.from_dict(maes, orient='index', columns=['MAE']).reset_index()
    df_maes_choro = df_maes.copy().rename(columns={'index':'city'})
    
    described = go.Figure(data=[go.Table(
    header=dict(values=list(df_merged_copy_described.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_merged_copy_described[i] for i in df_merged_copy_described.columns],
               fill_color='lavender',
               align='left'))
    ])
    
    maes = go.Figure(data=[go.Table(
    header=dict(values=list(df_maes.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_maes[i] for i in df_maes.columns],
               fill_color='lavender',
               align='left'))
    ])
    
    # Choropleth
    for city, v in iso.items():  
        df_maes_choro.loc[df_maes_choro.city==city, 'iso3'] =  v
        
    choro = px.choropleth(df_maes_choro, locations='iso3',
                          color='MAE', hover_name='city',
                          title='Choropleth MAE Map',
                          color_continuous_scale=px.colors.sequential.Turbo)
    choro.update_layout(margin=dict(l=60, r=60, t=50, b=50))
    
    
    described.update_layout(title = 'TimeSeries Descriptive Statistics')
    maes.update_layout(title = '12 Hours Forecast - Historical Temperature (Celsius)  Mean Absolute Error')
    choro.update_layout(title = 'MAE Choropleth Map')
    
    return described, maes, choro

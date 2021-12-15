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
- Pie chart with MAE of all cities, maybe not pie, but bar chart or something.


TODO:
    - make sure that missing datetime frame will be displayed as empty.
    This is important in case of impossibility of data pulling.
'''

#%% Allign DataFrames

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


df_merged = pd.merge(dfh, dff, left_on=dfh.index, right_on=dff.index, how='inner').rename(columns = {'key_0':'DateTimeCET'}).set_index('DateTimeCET')
df_merged.sort_index(inplace=True)



#%% Dash-Plotly

layout = html.Div([
    html.H1('Accuweather Project', style={"textAlign": "center"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='city-dropdown', value='Athens', clearable=False,
            options=[{'label': x, 'value': x} for x in sorted([i for i in dfh.columns])]
        ), className='six columns'),
    
    
    
    #     html.Div(dcc.Dropdown(
    #         id='sales-dropdown', value='EU Sales', clearable=False,
    #         persistence=True, persistence_type='memory',
    #         options=[{'label': x, 'value': x} for x in sales_list]
    #     ), className='six columns'),
        
        html.Div(dcc.DatePickerRange(id='date-range',
                                     min_date_allowed=dfh.index.min(),
                                     max_date_allowed=dff.index.max(),
                                     initial_visible_month=dff.index.min(),
                                     end_date=dff.index.max(),
                                     start_date=dfh.index.min()
        ), className='six columns'),
        
    ], className='row'),

    dcc.Graph(id='plot_comparison', figure={}),
    dcc.Graph(id='plot_historical', figure={}),
])

@app.callback(
    Output(component_id='plot_comparison', component_property='figure'),
    Input(component_id='city-dropdown', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)

def comparison(city_chosen, start_date, end_date):
    # print(city_chosen)
    print(start_date, end_date)
    all_value = [i for i in df_merged.columns if str(city_chosen) in i or 'query' in i]
    dropdown_value = [i for i in df_merged.columns if str(city_chosen) in i]
    # print(dropdown_value)
    df_merged_copy = df_merged.copy()
    df_merged_copy = df_merged_copy[all_value]
    
    
    # print(start_date, end_date)
    # print(df_merged_copy)
    df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]
    
    # print(df_merged_copy)
    # fig = px.line(df_merged_copy, x=df_merged_copy.index, y=dropdown_value, title='Historical-Forecast Comparison', markers=True, color='fc_query')
    # fig.update_layout(yaxis_title='Comparison')
    
    
    # Using Plotly Graph Object
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_merged_copy.index, y=df_merged_copy[dropdown_value[0]],
                              mode='lines+markers', name=dropdown_value[0]))
    fig.add_trace(go.Scatter(x=df_merged_copy.index, y=df_merged_copy[dropdown_value[1]],
                              mode='lines+markers', name=dropdown_value[1]))
    for query in df_merged_copy.fc_query.unique():
        # df_merged_sliced = df_merged_copy.loc[df_merged_copy.fc_query == query]
        # print(type(query))
        fig.add_vline(x=pd.to_datetime(query), line_width=2, line_dash="dash", line_color="green")
        
        # fig.add_trace(go.Scatter(x=df_merged_sliced.index, y=df_merged_sliced[dropdown_value[0]],
        #                           mode='lines', name=dropdown_value[0] + ' queried on' + query))
        # fig.add_trace(go.Scatter(x=df_merged_sliced.index, y=df_merged_sliced[dropdown_value[1]],
        #                           mode='lines', name=dropdown_value[1] + ' queried on' + query))
    
    
    return fig

@app.callback(
    Output(component_id='plot_historical', component_property='figure'),
    Input(component_id='city-dropdown', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)

def historical(city_chosen, start_date, end_date):
    # print(city_chosen)
    dropdown_value = [i for i in dfh.columns if str(city_chosen) in i]
    # print(dropdown_value)
    df_merged_copy = dfh.copy()
    df_merged_copy = dfh[dropdown_value]
    
    df_merged_copy = df_merged_copy.loc[(df_merged_copy.index >= start_date) & (df_merged_copy.index <= end_date)]
    # print(df_merged_copy)
    fig = px.line(df_merged_copy, x=df_merged_copy.index, y=city_chosen, title='Historical Values', markers=True)
    fig.update_layout(yaxis_title='Athens Historical Value')
    return fig



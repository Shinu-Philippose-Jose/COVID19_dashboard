import os
import sys
import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

from data.get_data import get_johns_hopkins
from data.process_JH_data import store_relational_JH_data
from features.build_features import generate_features

get_johns_hopkins()
store_relational_JH_data()
generate_features()

df_input_large=pd.read_csv('../data/processed/COVID_final_set.csv',sep=';')

fig = go.Figure()
app = dash.Dash()

app.layout = html.Div([

    dcc.Markdown('''
    #  COVID-19 data

    This dashboard offeres a visualization of the growth of COVID-19 cases across the world. 
    Selecting the countries and the required timeline will updae te the graph appropriately.

    '''),

    dcc.Markdown('''
    ### Select countries
    '''),

    dcc.Dropdown(
        id='country_drop_down',
        options=[{'label': each,'value':each} for each in df_input_large['country'].unique()],
        value=['India', 'Germany','Japan'], # pre-selected coultries
        multi=True
    ),

    dcc.Markdown('''
        ### Select Timeline
        '''),

    dcc.Dropdown(
    id='doubling_time',
    options=[
        {'label': 'Timeline Confirmed ', 'value': 'confirmed'},
        {'label': 'Timeline Confirmed Filtered', 'value': 'confirmed_filtered'},
        {'label': 'Timeline Doubling Rate', 'value': 'confirmed_DR'},
        {'label': 'Timeline Doubling Rate Filtered', 'value': 'confirmed_filtered_DR'},
    ],
    value='confirmed',
    multi=False
    ),

    dcc.Graph(figure=fig, id='main_window_slope')
])

@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('doubling_time', 'value')])
def update_figure(country_list, show_doubling):

    print(country_list)

    if 'doubling_rate' in show_doubling:
        my_yaxis={'type':"log",
               'title':'Approximated doubling rate over 3 days'
              }
    else:
        my_yaxis={'type':"log",
                  'title':'Confirmed infected people'
              }

    traces = []
    for each in country_list:

        df_plot=df_input_large[df_input_large['country']==each]

        if show_doubling=='doubling_rate_filtered':
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        else:
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.sum).reset_index()
       #print(show_doubling)

        traces.append(dict(x=df_plot.date,
                                y=df_plot[show_doubling],
                                mode='markers+lines',
                                opacity=0.9,
                                name=each
                        )
                )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,

                xaxis={'title':'Timeline',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },

                yaxis=my_yaxis
        )
    }

if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False)



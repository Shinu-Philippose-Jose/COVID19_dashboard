import sys
import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from scipy import optimize
from scipy import integrate
from utils import SIR_model
from dash.dependencies import Input, Output,State

df_analyse=pd.read_csv('../data/processed/COVID_final_set.csv',sep=';')
df_population = pd.read_csv('../data/population.csv', sep=';')

fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
    # SIR Modeling of Covid-19 data
    This Dashboard offers a visualization for the SIR modeling of the COVID-19 data. 
    The SIR model aslo known as the Kermack-McKendrick epidemic model takes the Susceptible, Infective and Removed individuals
    into consideration in order to predict the growth rate of the epidemic. We apply the same model to the data COVID-19 pandemic data
    to predict the growth as per the SIR model along with the graph of actual growth.

    '''),

    dcc.Markdown(''' 
    ## Select a country.
    '''),

    dcc.Dropdown(
        id = 'country_drop_down',
        options=[ {'label': each,'value':each} for each in df_analyse['country'].unique()],
        value= 'India', # which are pre-selected
        multi=False),

    dcc.Graph(figure = fig, id = 'SIR_graph')
    ])

@app.callback(
    Output('SIR_graph', 'figure'),
    [Input('country_drop_down', 'value')])

def update_SIR_figure(country_drop_down):

    traces = []

    df_plot = df_analyse[df_analyse['country'] == country_drop_down]
    df_plot = df_plot[['state', 'country', 'confirmed', 'date']].groupby(['country', 'date']).agg(np.sum).reset_index()
    df_plot.sort_values('date', ascending = True).head()
    df_plot = df_plot.confirmed[55:]

    population = df_population[df_population['COUNTRY'] == country_drop_down]['Value'].values[0]

    t, fitted = SIR_model(df_plot, population)

    traces.append(dict (x = t,
                        y = fitted,
                        mode = 'markers',
                        opacity = 0.9,
                        name = 'SIR fit',
                        line = dict(color = 'green'))
                  )

    traces.append(dict (x = t,
                        y = df_plot,
                        mode = 'lines',
                        opacity = 0.9,
                        name = 'Original Data',
                        line = dict(color = 'red'))
                  )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,
                title = 'SIR model fitting for '+ country_drop_down,

                xaxis= {'title':'Days',
                       'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },

                yaxis={'title': "Infected population"}
        )
    }


if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)


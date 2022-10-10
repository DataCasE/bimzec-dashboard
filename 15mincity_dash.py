import dash
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import geopandas as gpd
import json
import os 
import glob
import geojson
import base64

image_filename = 'data/ams_logo_square_white.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

mapbox_token = ("pk.eyJ1IjoiY2FzcGFyLWVnYXMiLCJhIjoiY2poc3QwazFkMDNiaTNxbG1vMmJvZmVwcCJ9.Yy65IKfEEM015SvKt8OBqw")

# import isochrones geojson files
with open('data/all_isochrones.json') as json_data:
     geo_iso = json.load(json_data)

# import csv as "df"
df = pd.read_csv('data/isochrones - df.csv')

# create selections of df with unique values from columns, to be used for df_function below
amenity_mode = df['title'].unique()
amenity = df['amenity'].unique()
mode = df['mode'].unique()
pace = df['pace'].unique()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {'background': '#ffffff','text': '#413A38'}

def create_map(df_function):
    choro = px.choropleth_mapbox(
            df_function, geojson=geo_iso, color='mode',  color_discrete_sequence=['#E0001B'],
            locations="id", featureidkey="properties.id", opacity = 0.3,
            center={"lat": 52.352302, "lon": 4.888338}, zoom=10.5, 
            hover_name = 'title',
            hover_data={'id':False, 'value':False, 'mode':True,'pace':True})

    choro.update_layout(
        autosize=False,
        margin = dict(l=0,r=0,b=0,t=0,pad=4,autoexpand=True),
        width = 1100,
        height = 700,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        showlegend = False,
        coloraxis=dict(
            colorbar=dict(thickness=20, ticklen=3)),
        coloraxis_showscale=False,
        mapbox = dict(
            accesstoken = mapbox_token,
            style = 'mapbox://styles/caspar-egas/cjvsgazch0hk81cs3yhk2jem2'))

    return choro
    
default_selection = df[df['title'] == 'metrostop by foot']

choro_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Hr(),    
    html.H3('15 minutes Amsterdam', style={'color': colors['text']}),
    html.P('An accessibility analysis of Amsterdam based on the 15-Minute City concept. The modes of transport used are walking and cycling, differentiated by normal and slow pace. The starting points of the 15-minute isochrones are locations of different amenities.'),
    html.Div(
        dcc.Dropdown(
            id = 'amenity-dropdown',
            options = [{'label': k, 'value': k} for k in amenity_mode],
            value = 'metrostop by foot',
            multi = False,
            clearable = False,
            searchable = True,
            ),
        style={'width': '100%', 'float': 'left', 'display': 'inline-block'}),
    html.I(' Select an option from the dropdown menu'),
    html.Hr(),
    dcc.Graph(id="selected_map", figure=create_map(default_selection), config={'displayModeBar':False}),
    html.Small('Credits: This dashboard was made for the AMS Institute by Caspar Egas, Erik Boertjes, Petar Koljensic & Tom Kuipers. Made with Plotly Dash.')
    ])

@app.callback(
    Output('selected_map', 'figure'),
    Input('amenity-dropdown', 'value')
    )
def update_output(value):
    dff = df[df["title"] == (value)]
    return create_map(dff)

server = app.server

dashlayout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Row(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))),
                style={'height': '100%'}, width=2),            

                dbc.Col(dbc.Row(html.Div(children=[choro_layout])),
                style={'height': '100%'}, width=9),
                
                dbc.Col(dbc.Row(html.Div(children=' ')),
                style={'height': '100%'}, width=1),
            ],
            className="g-0",
            style={"height": "110vh", "background-color": colors['background']})
    ],
            fluid=True
)


app.layout = dashlayout

if __name__ == '__main__':
    app.run_server(debug=True)

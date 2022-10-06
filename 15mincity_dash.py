import dash
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly
import plotly.express as px
import dash_bootstrap_components as dbc
import geopandas as gpd
import json
import os 
import glob
import geojson

mapbox_token =("pk.eyJ1IjoiY2FzcGFyLWVnYXMiLCJhIjoiY2poc3QwazFkMDNiaTNxbG1vMmJvZmVwcCJ9.Yy65IKfEEM015SvKt8OBqw")

# import isochrones geojson files
# import all geojson files from the folder "data" 
isochrones = 'data/isochrones'
isochrone_files = glob.glob(os.path.join(isochrones, '*.geojson'))

# concatenate all geojson files into "geo"
geo_iso = pd.concat((gpd.read_file(f) for f in isochrone_files))

# convert the coordinate values into the right type
geo_iso.to_crs('WGS84', inplace=True)
geo_iso = json.loads(geo_iso.to_json())

# import amenity locations geojson files
# import all geojson files from the folder "data" 
# locations = 'data/locations'
# location_files = glob.glob(os.path.join(locations, '*.geojson'))

# concatenate all geojson files into "geo"
# geo_loc = pd.concat((gpd.read_file(f) for f in location_files))

# convert the coordinate values into the right type
# geo_loc.to_crs('WGS84', inplace=True)
# geo_loc = json.loads(geo_loc.to_json())

# import csv as "df"
df = pd.read_csv('data/isochrones - df.csv')

# create selections of df with unique values from columns, to be used for df_function below
amenity_mode = df['title'].unique()
amenity = df['amenity'].unique()
mode = df['mode'].unique()
pace = df['pace'].unique()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {'background': 'darkgrey','text': '#ffffff'}

def create_map(df_function):
    choro = px.choropleth_mapbox(
            df_function, geojson=geo_iso, color='mode',  color_discrete_sequence=['#6689B9','#8E9F07'],
            locations="id", featureidkey="properties.id", opacity = 0.5,
            center={"lat": 52.352302, "lon": 4.888338}, zoom=10.5, 
            hover_name = 'title',
            hover_data={'id':False, 'value':False, 'mode':True,'pace':True})

    choro.update_layout(
        autosize=False,
        margin = dict(l=0,r=0,b=0,t=0,pad=4,autoexpand=True),
        width = 1000,
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
    html.H4('The 15 minute city - Amsterdam', style={'color': colors['text']}),
    html.Hr(),
    html.Div(
        dcc.Dropdown(
            id = 'amenity-dropdown',
            options = [{'label': k, 'value': k} for k in amenity_mode],
            value = 'metrostop by foot',
            multi = False,
            ),
        style={'width': 1000, 'display': 'inline-block'}),
    html.Hr(),
    dcc.Graph(id="selected_map", figure=create_map(default_selection), config={'displayModeBar':False})])

@app.callback(
    Output('selected_map', 'figure'),
    Input('amenity-dropdown', 'value')
    )
def update_output(value):
    dff = df[df["title"] == (value)]
    return create_map(dff)

server = app.server

dashlayout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div(children=[choro_layout]),width=8),justify='center',
        className="g-0",
        style={"height": "110vh", "background-color": colors['background']})
    ]
)

app.layout = dashlayout

if __name__ == '__main__':
    app.run_server(debug=True)

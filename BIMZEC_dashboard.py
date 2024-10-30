## BIMZEC Dashboard v1.1 Aug 2024


# download dependencies
import json
import dash
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly
import plotly.express as px
import dash_bootstrap_components as dbc
import requests
from pathlib import Path
from zipfile import ZipFile
import geopandas as gpd
import shapely.geometry
import plotly.graph_objects as go
from shapely.geometry import Point

token = 'pk.eyJ1IjoiY2FzcGFyLWVnYXMiLCJhIjoiY2poc3QwazFkMDNiaTNxbG1vMmJvZmVwcCJ9.Yy65IKfEEM015SvKt8OBqw'

# Chart 1
# loading flowmap data for each scenario and creating a flowmap for each
# more elaborate way, i couldnt get the more efficient way to function with the other graphs

# Function to load dataset
def load_dataset(file_path):
    try:
        return gpd.read_file(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Define a function to process and extract lat/lon for each scenario
def process_scenario(scenario_prefix):
    roads = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_roads.zip")
    hubs = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_hubs.zip")
    suppliers = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_suppliers.zip")
    construction = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_construction.zip")
    demolition = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_demolition.zip")
    water = load_dataset(f"zip://home/bimzec/bimzec-dashboard/data/latest_data/{scenario_prefix}/{scenario_prefix}_water.zip")

    if hubs is not None:
        hubs['lon'] = hubs.geometry.x
        hubs['lat'] = hubs.geometry.y

    if suppliers is not None:
        suppliers['lon'] = suppliers.geometry.x
        suppliers['lat'] = suppliers.geometry.y

    if construction is not None:
        construction['lon'] = construction.geometry.x
        construction['lat'] = construction.geometry.y

    if demolition is not None:
        demolition['lon'] = demolition.geometry.x
        demolition['lat'] = demolition.geometry.y

    return roads, hubs, suppliers, construction, demolition, water

# Function to create a flow map for a given scenario
def create_flow_map(roads, hubs, suppliers, construction, demolition, water):
    lats = []
    lons = []
    names = []
    
    if roads is not None:
        for feature, name in zip(roads.geometry, roads.damage):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.concatenate((lats, y, [None]))
                lons = np.concatenate((lons, x, [None]))
                names = np.concatenate((names, [name]*len(y), [None]))

    flowmap = go.Figure()
        
    # Add the roads lines
    if roads is not None:
        flowmap.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(color="#FFCB00", width=2),
            name='Roads Used'
        ))

    # Add the hubs
    if hubs is not None:
        flowmap.add_trace(go.Scattermapbox(
            lat=hubs['lat'],
            lon=hubs['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=16, color='#4D1B2F'),
            name='Hubs',
            text=hubs['name'],
            hoverinfo='text'
        ))
    
    # Add the suppliers sites
    if suppliers is not None:
        flowmap.add_trace(go.Scattermapbox(
            lat=suppliers['lat'],
            lon=suppliers['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=12, color='#9E332E'),
            name='Suppliers',
            text=suppliers['material'],
            hoverinfo='text'
        ))
  
    # Add the construction sites
    if construction is not None:
        flowmap.add_trace(go.Scattermapbox(
            lat=construction['lat'],
            lon=construction['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=8, color='#D23600', opacity=0.75),
            name='Construction Sites',
            text=construction['Projectnaa'],
            hoverinfo='text'
        ))
        
    # Add the demolition sites
    if demolition is not None:
        flowmap.add_trace(go.Scattermapbox(
            lat=demolition['lat'],
            lon=demolition['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=6, color='#871F98', opacity=0.75),
            name='Demolition Sites',
            hoverinfo='name'
        ))

    # Customize layout
    flowmap.update_layout(
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4, autoexpand=True),
        width=1400,
        height=620,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        showlegend=True,
        legend=dict(title="Legend", orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
        font_family="Helvetica",
        font_size=16,
        mapbox=dict(
            accesstoken=token,
            style='mapbox://styles/caspar-egas/clxiqzqs300aj01pc41hcew9v',  # circularity basemap
            center={"lat": 52.33557, "lon": 4.892077},
            zoom=9.5
        )
    )
    
    flowmap.update_traces(below="settlement-major-label")

    return flowmap

# Process scenarios
s1_roads, s1_hubs, s1_suppliers, s1_construction, s1_demolition, s1_water = process_scenario("s1")
s2_roads, s2_hubs, s2_suppliers, s2_construction, s2_demolition, s2_water = process_scenario("s2")
s3_roads, s3_hubs, s3_suppliers, s3_construction, s3_demolition, s3_water = process_scenario("s3")
s4_roads, s4_hubs, s4_suppliers, s4_construction, s4_demolition, s4_water = process_scenario("s4")
s5_roads, s5_hubs, s5_suppliers, s5_construction, s5_demolition, s5_water = process_scenario("s5")
s6_roads, s6_hubs, s6_suppliers, s6_construction, s6_demolition, s6_water = process_scenario("s6")

# Create flow maps for each scenario
flow_map1 = create_flow_map(s1_roads, s1_hubs, s1_suppliers, s1_construction, s1_demolition, s1_water)
flow_map2 = create_flow_map(s2_roads, s2_hubs, s2_suppliers, s2_construction, s2_demolition, s2_water)
flow_map3 = create_flow_map(s3_roads, s3_hubs, s3_suppliers, s3_construction, s3_demolition, s3_water)
flow_map4 = create_flow_map(s4_roads, s4_hubs, s4_suppliers, s4_construction, s4_demolition, s4_water)
flow_map5 = create_flow_map(s5_roads, s5_hubs, s5_suppliers, s5_construction, s5_demolition, s5_water)
flow_map6 = create_flow_map(s6_roads, s6_hubs, s6_suppliers, s6_construction, s6_demolition, s6_water)

# Layout for each flowmap
flowmap1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 1 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map1", figure=flow_map1, config={'displayModeBar': False})
])

flowmap2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 2 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map2", figure=flow_map2, config={'displayModeBar': False}),
])

flowmap3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 3 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map3", figure=flow_map3, config={'displayModeBar': False}),
])

flowmap4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 4 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map4", figure=flow_map4, config={'displayModeBar': False}),
])

flowmap5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 5 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map5", figure=flow_map5, config={'displayModeBar': False}),
])

flowmap6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Scenario 6 logistics map', html.Br()], style={'color': 'black'}),
    dcc.Graph(id="flow_map6", figure=flow_map6, config={'displayModeBar': False}),
])


# Chart 2
# Donut charts with material data for 6 scenarios
# more elaborate way to prepare data for each tab

donut_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/donut_data.csv",sep=',')
donut_data1 = donut_data[donut_data['scenario']=='scenario 1']
donut_data2 = donut_data[donut_data['scenario']=='scenario 2']
donut_data3 = donut_data[donut_data['scenario']=='scenario 3']
donut_data4 = donut_data[donut_data['scenario']=='scenario 4']
donut_data5 = donut_data[donut_data['scenario']=='scenario 5']
donut_data6 = donut_data[donut_data['scenario']=='scenario 6']

donut1 = px.pie(
    donut_data1, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut1.update_traces(textposition='outside', textinfo='percent+label')
donut1.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut1", figure=donut1, config={'displayModeBar':False}),
])

donut2 = px.pie(
    donut_data2, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut2.update_traces(textposition='outside', textinfo='percent+label')
donut2.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut2", figure=donut2, config={'displayModeBar':False}),
])

donut3 = px.pie(
    donut_data3, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut3.update_traces(textposition='outside', textinfo='percent+label')
donut3.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut3", figure=donut3, config={'displayModeBar':False}),
])

donut4 = px.pie(
    donut_data4, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut4.update_traces(textposition='outside', textinfo='percent+label')
donut4.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut4", figure=donut4, config={'displayModeBar':False}),
])

donut5 = px.pie(
    donut_data5, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut5.update_traces(textposition='outside', textinfo='percent+label')
donut5.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut5", figure=donut5, config={'displayModeBar':False}),
])

donut6 = px.pie(
    donut_data6, 
    values='tons', 
    names='material',
    color_discrete_sequence= px.colors.sequential.RdBu, 
    hole=.6,
    height=500)

#donut.update_traces(textposition= 'inside', selector=dict(type='pie'))
donut6.update_traces(textposition='outside', textinfo='percent+label')
donut6.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

donut6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per material', style={'color': 'black'}),
    dcc.Graph(id="donut6", figure=donut6, config={'displayModeBar':False}),
])



# Chart 3
# Stacked bars with emissions for 6 scenarios
# more elaborate way to prepare data for each tab

stack_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/stack_data.csv",sep=',')
stack_data1 = stack_data[stack_data['scenario']=='s1']
stack_data2 = stack_data[stack_data['scenario']=='s2']
stack_data3 = stack_data[stack_data['scenario']=='s3']
stack_data4 = stack_data[stack_data['scenario']=='s4']
stack_data5 = stack_data[stack_data['scenario']=='s5']
stack_data6 = stack_data[stack_data['scenario']=='s6']

colors = {
    'Supplier to Hub': '#67001E',
    'Hub to Construction': '#B2162D',
    'Supplier to Construction': '#D5604C',
    'Demolition to Hub': '#F3A582',
}

# Create the stacked bar chart using Plotly Express
stack1 = px.bar(
    stack_data1,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack1.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack1", figure=stack1, config={'displayModeBar':False}),
])

# Create the stacked bar chart using Plotly Express
stack2 = px.bar(
    stack_data2,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack2.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack2", figure=stack2, config={'displayModeBar':False}),
])

# Create the stacked bar chart using Plotly Express
stack3 = px.bar(
    stack_data3,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack3.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack3", figure=stack3, config={'displayModeBar':False}),
])

# Create the stacked bar chart using Plotly Express
stack4 = px.bar(
    stack_data4,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack4.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack4", figure=stack4, config={'displayModeBar':False}),
])

# Create the stacked bar chart using Plotly Express
stack5 = px.bar(
    stack_data5,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack5.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack5", figure=stack5, config={'displayModeBar':False}),
])

# Create the stacked bar chart using Plotly Express
stack6 = px.bar(
    stack_data6,
    x='year', 
    y='emission', 
    color='stage', 
    barmode='stack',
    color_discrete_map= colors)

stack6.update_layout(
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black"
)

stack6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('CO2 emission per year', style={'color': 'black'}),
    dcc.Graph(id="stack6", figure=stack6, config={'displayModeBar':False}),
])


# Chart 4
# Linechart with NOX data for 6 scenarios
# more elaborate way to prepare data for each tab

nox_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/line_data.csv",sep=',')

# Rename the columns
nox_data = nox_data.rename(columns={
    'emissions_gNOX': 'NOX',
    'emissions_gPM2p5': 'PM2.5',
    'emissions_gPM10': 'PM10'
})

nox_data1 = nox_data[nox_data['scenario']=='s1']
nox_data2 = nox_data[nox_data['scenario']=='s2']
nox_data3 = nox_data[nox_data['scenario']=='s3']
nox_data4 = nox_data[nox_data['scenario']=='s4']
nox_data5 = nox_data[nox_data['scenario']=='s5']
nox_data6 = nox_data[nox_data['scenario']=='s6']


nox1 = px.line(nox_data1,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox1.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox1.update_traces(marker=dict(line=dict(width=0)))
nox1.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox1.update_yaxes(showgrid=False, zeroline=False)

nox1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox1", figure=nox1, config={'displayModeBar':False}),
])

nox2 = px.line(nox_data2,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox2.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox2.update_traces(marker=dict(line=dict(width=0)))
nox2.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox2.update_yaxes(showgrid=False, zeroline=False)

nox2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox2", figure=nox2, config={'displayModeBar':False}),
])

nox3 = px.line(nox_data3,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox3.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox3.update_traces(marker=dict(line=dict(width=0)))
nox3.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox3.update_yaxes(showgrid=False, zeroline=False)

nox3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox3", figure=nox3, config={'displayModeBar':False}),
])

nox4 = px.line(nox_data4,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox4.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox4.update_traces(marker=dict(line=dict(width=0)))
nox4.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox4.update_yaxes(showgrid=False, zeroline=False)

nox4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox4", figure=nox4, config={'displayModeBar':False}),
])

nox5 = px.line(nox_data5,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox5.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox5.update_traces(marker=dict(line=dict(width=0)))
nox5.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox5.update_yaxes(showgrid=False, zeroline=False)

nox5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox5", figure=nox5, config={'displayModeBar':False}),
])

nox6 = px.line(nox_data6,
               x='year',
               y='NOX',
               color_discrete_sequence=["#B2162D"],
               markers=True,
               labels={"NOX": "NOX emissions"})

nox6.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
nox6.update_traces(marker=dict(line=dict(width=0)))
nox6.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
nox6.update_yaxes(showgrid=False, zeroline=False)

nox6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('NOX emission per year', style={'color': 'black'}),
    dcc.Graph(id="nox6", figure=nox6, config={'displayModeBar':False}),
])



# Chart 5
# Linecharts with PM data for 6 scenarios
# more elaborate way to prepare data for each tab

pm_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/line_data.csv",sep=',')

# Rename the columns
pm_data = pm_data.rename(columns={
    'emissions_gNOX': 'NOX',
    'emissions_gPM2p5': 'PM2.5',
    'emissions_gPM10': 'PM10'
})

# Melt the 'PM2.5' and 'PM10' columns into a single 'emissions' column
pm_data = pm_data.melt(id_vars=['year', 'scenario'], value_vars=['PM2.5', 'PM10'], var_name='Emission type', value_name='emissions')

pm_data1 = pm_data[pm_data['scenario']=='s1']
pm_data2 = pm_data[pm_data['scenario']=='s2']
pm_data3 = pm_data[pm_data['scenario']=='s3']
pm_data4 = pm_data[pm_data['scenario']=='s4']
pm_data5 = pm_data[pm_data['scenario']=='s5']
pm_data6 = pm_data[pm_data['scenario']=='s6']

pm1 = px.line(pm_data1,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm1.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm1.update_traces(marker=dict(line=dict(width=0)))
pm1.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm1.update_yaxes(showgrid=False, zeroline=False)

pm1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm1", figure=pm1, config={'displayModeBar':False}),
])

pm2 = px.line(pm_data2,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm2.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm2.update_traces(marker=dict(line=dict(width=0)))
pm2.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm2.update_yaxes(showgrid=False, zeroline=False)

pm2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm2", figure=pm2, config={'displayModeBar':False}),
])

pm3 = px.line(pm_data3,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm3.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm3.update_traces(marker=dict(line=dict(width=0)))
pm3.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm3.update_yaxes(showgrid=False, zeroline=False)

pm3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm3", figure=pm3, config={'displayModeBar':False}),
])

pm4 = px.line(pm_data4,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm4.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm4.update_traces(marker=dict(line=dict(width=0)))
pm4.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm4.update_yaxes(showgrid=False, zeroline=False)

pm4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm4", figure=pm4, config={'displayModeBar':False}),
])

pm5 = px.line(pm_data5,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm5.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm5.update_traces(marker=dict(line=dict(width=0)))
pm5.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm5.update_yaxes(showgrid=False, zeroline=False)

pm5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm5", figure=pm5, config={'displayModeBar':False}),
])

pm6 = px.line(pm_data6,
             x='year',
             y='emissions',
             color_discrete_sequence=['#F3A582',"#B2162D"],
             markers=True,
             color='Emission type'
             )

pm6.update_layout(plot_bgcolor='#ffffff',
                      paper_bgcolor="#ffffff",
                      font_family="Helvetica",
                      font_color="black")
pm6.update_traces(marker=dict(line=dict(width=0)))
pm6.update_xaxes(showgrid=False, zeroline=False,dtick='M1',tickangle=45)
pm6.update_yaxes(showgrid=False, zeroline=False)

pm6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('PM2.5 and PM10 emission per year', style={'color': 'black'}),
    dcc.Graph(id="pm6", figure=pm6, config={'displayModeBar':False}),
])



# Chart 6
# Treemaps with material data for 6 scenarios
# more elaborate way to prepare data for each tab


mat_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/treemap_mat_data.csv",sep=',')

mat_data1 = mat_data[mat_data['scenario']=='scenario 1']
mat_data2 = mat_data[mat_data['scenario']=='scenario 2']
mat_data3 = mat_data[mat_data['scenario']=='scenario 3']
mat_data4 = mat_data[mat_data['scenario']=='scenario 4']
mat_data5 = mat_data[mat_data['scenario']=='scenario 5']
mat_data6 = mat_data[mat_data['scenario']=='scenario 6']

mat1 = px.treemap(mat_data1, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat1.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat1", figure=mat1, config={'displayModeBar':False}),
])

mat2 = px.treemap(mat_data2, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat2.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat2", figure=mat2, config={'displayModeBar':False}),
])

mat3 = px.treemap(mat_data3, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat3.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat3", figure=mat3, config={'displayModeBar':False}),
])

mat4 = px.treemap(mat_data4, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat4.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat4", figure=mat4, config={'displayModeBar':False}),
])

mat5 = px.treemap(mat_data5, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat5.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat5", figure=mat5, config={'displayModeBar':False}),
])

mat6 = px.treemap(mat_data6, 
                  path=[px.Constant("material"),'material'], 
                  values='tons',
                  color='tons',
                  color_continuous_scale='RdBu_r',
                  labels={"tons": "CO2 emissions"})

mat6.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

mat6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Material type emissions', style={'color': 'black'}),
    dcc.Graph(id="mat6", figure=mat6, config={'displayModeBar':False}),
])



# Chart 7
# Treemaps with circularity data for 6 scenarios
# more elaborate way to prepare data for each tab

circ_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/treemap_circ_data.csv",sep=',')

circ_data1 = circ_data[circ_data['scenario']=='scenario 1']
circ_data2 = circ_data[circ_data['scenario']=='scenario 2']
circ_data3 = circ_data[circ_data['scenario']=='scenario 3']
circ_data4 = circ_data[circ_data['scenario']=='scenario 4']
circ_data5 = circ_data[circ_data['scenario']=='scenario 5']
circ_data6 = circ_data[circ_data['scenario']=='scenario 6']


circ1 = px.treemap(circ_data1, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   range_color=(0, 100), 
                   color_continuous_scale='RdBu_r')

circ1.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

# Add annotations for percentages inside the blocks
annotations = []
for index, row in circ_data1.iterrows():
    annotations.append(dict(x=row['materials'], y=row['circular'],
                            text=f"{row['percentage']:.1%}",
                            font=dict(color='white', size=10),
                            showarrow=False))
    
# Add the annotations to the layout
circ1.update_layout(annotations=annotations)

circ1_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ1", figure=circ1, config={'displayModeBar':False}),
])


circ2 = px.treemap(circ_data2, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   range_color=(0, 100), 
                   color_continuous_scale='RdBu_r')

circ2.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

circ2_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ2", figure=circ2, config={'displayModeBar':False}),
])

circ3 = px.treemap(circ_data3, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   range_color=(0, 100), 
                   color_continuous_scale='RdBu_r')

circ3.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

circ3_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ3", figure=circ3, config={'displayModeBar':False}),
])

circ4 = px.treemap(circ_data4, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   range_color=(0, 100), 
                   color_continuous_scale='RdBu_r')

circ4.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

circ4_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ4", figure=circ4, config={'displayModeBar':False}),
])

circ5 = px.treemap(circ_data5, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   range_color=(0, 100), 
                   color_continuous_scale='RdBu_r')

circ5.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

circ5_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ5", figure=circ5, config={'displayModeBar':False}),
])

circ6 = px.treemap(circ_data6, 
                   path=[px.Constant("materials"),'circular'], 
                   values='percentage',
                   color='percentage',
                   color_continuous_scale='RdBu_r')

circ6.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor="white",
    font_family="Helvetica",
    font_color="black",
    width= 1300,
    height= 300,
    margin= dict(t=50, l=25, r=25, b=25)
)

circ6_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica','textAlign': 'center'}, children=[
    html.H5('Circular vs non-circular materials', style={'color': 'black'}),
    dcc.Graph(id="circ6", figure=circ6, config={'displayModeBar':False}),
])



# Graphs comparing the 6 scenarios, used for tab "Comparison"
# Initialize Dash app
app = Dash(__name__)

result_data = pd.read_csv("/home/bimzec/bimzec-dashboard/data/scenario_data/result_data.csv",sep=',')
co2_w = result_data[(result_data['result_name'] == 'co2') & (result_data['area'] == 'whole model')]
co2_m = result_data[(result_data['result_name'] == 'co2') & (result_data['area'] == 'MRA')]
co2_z = result_data[(result_data['result_name'] == 'co2') & (result_data['area'] == 'zuid-oost')]
gas_w = result_data[((result_data['result_name'] == 'NOX') | (result_data['result_name'] == 'PM2.5') | (result_data['result_name'] == 'PM10')) & (result_data['area'] == 'whole model')]
gas_m = result_data[((result_data['result_name'] == 'NOX') | (result_data['result_name'] == 'PM2.5') | (result_data['result_name'] == 'PM10')) & (result_data['area'] == 'MRA')]
gas_z = result_data[((result_data['result_name'] == 'NOX') | (result_data['result_name'] == 'PM2.5') | (result_data['result_name'] == 'PM10')) & (result_data['area'] == 'zuid-oost')]
km_w = result_data[(result_data['result_name'] == 'logistic movements') & (result_data['area'] == 'whole model')]
km_m = result_data[(result_data['result_name'] == 'logistic movements') & (result_data['area'] == 'MRA')]
km_z = result_data[(result_data['result_name'] == 'logistic movements') & (result_data['area'] == 'zuid-oost')]

@app.callback(
    Output('km_C-container', 'children'),  # Use a container to hold the graph
    [Input('km_C-dropdown', 'value')]
)
def update_km_graph(value):
    print(f"Dropdown value selected: {value}")  # Debugging
    if value == 'km_w':
        print(km_w.head())
        bar_km_w = px.bar(km_w,
                          x='value',
                          y='scenario',
                          orientation='h',
                          color='value',
                          color_continuous_scale='RdBu_r',
                          labels={"value": "kilometers of logistic movements"}
                          )
        return dcc.Graph(id='bar_km_w', figure=bar_km_w, config={'displayModeBar':False})  # Unique ID for each graph
    elif value == 'km_m':
        bar_km_m = px.bar(km_m,
                          x='value',
                          y='scenario',
                          orientation='h',
                          color='value',
                          color_continuous_scale='RdBu_r',
                          labels={"value": "kilometers of logistic movements"}
                          )
        return dcc.Graph(id='bar_km_m', figure=bar_km_m, config={'displayModeBar':False})  # Unique ID for each graph
    elif value == 'km_z':
        bar_km_z = px.bar(km_z,
                          x='value',
                          y='scenario',
                          orientation='h',
                          color='value',
                          color_continuous_scale='RdBu_r',
                          labels={"value": "kilometers of logistic movements"}
                          )
        return dcc.Graph(id='bar_km_z', figure=bar_km_z, config={'displayModeBar':False})  # Unique ID for each graph
    return html.Div("No data available")  # Fallback

km_C_layout = html.Div(style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'center'}, children=[
    html.H5(['Kilometers of logistic movements', html.Br()], style={'color': 'black'}),
    dcc.Dropdown(
        id='km_C-dropdown',
        options=[
            {'label': 'Whole model', 'value': 'km_w'},
            {'label': 'MRA', 'value': 'km_m'},
            {'label': 'Zuid-oost', 'value': 'km_z'}
        ],
        value='km_w',
        style={"width": "50%"}
    ),
    html.Div(id='km_C-container')  # Placeholder for the graph
])


# Introduction text dashboard
#Header
header=html.Div(style={'backgroundColor': '#1F7799', 'fontFamily': 'Helvetica', 'textAlign': 'center','paddingTop': '30px','paddingBottom': '30px'}, 
                children=[html.H3('BIMZEC I Tackling Urban Construction Logistics Emissions in Amsterdam', style={'color': 'white'})])

#Paragraph 1
text1 = html.Div(
    style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'left', 'width': '70%'},
    children=[
        html.P('Description:', style={'color': 'black', 'fontWeight': 'bold'}),
        html.P('The dashboard provides a visualization of transport emissions savings potential resulting from implementing a new set of solutions in urban construction within the Amsterdam Metropolitan Area (MRA). We named them BIMZEC (biobased, industrialized, modular, zero-emission, circular).'),
        html.P('It showcases the outcomes of a modelling approach that integrates diverse data sources, including stakeholder interviews and geospatial datasets, to simulate construction site behavior and estimate transportation emissions for the next decade.'),
        html.P('Through interactive charts and maps,  you can explore solutions and future scenarios for reducing emissions associated with construction logistics.')
    ])

#Paragraph 2
text2 = html.Div(
    style={'backgroundColor': 'white', 'fontFamily': 'Helvetica', 'textAlign': 'left', 'width': '80%'},
    children=[
        html.P('Scenarios:', style={'color': 'black', 'fontWeight': 'bold'}),
        html.P('Scenarios explore the impact of different solutions set as parameters on construction logistics. Starting scenario begins with the current state (Business as Usual) and transitions to the future BIMZEC state to visualize changes over time.'),
        html.P('Contact:', style={'color': 'black', 'fontWeight': 'bold'}), 
        html.P('Petar Koljensic I Researcher TU Delft p.koljensic@tudelft.nl'),
        html.P('Acknowledgements:', style={'color': 'black', 'fontWeight': 'bold'}), 
        html.P('Research I Model I Dashboard by TU Delft, Hogeschool van Amsterdam, AMS Institute 2023-2024')
    ])


# Define the layout for the tabs
tabs_layout = html.Div([
    dcc.Tabs(id='tabs-graph', value='tab-6-graph', children=[
        dcc.Tab(label='Scenario 1', value='tab-1-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Scenario 2', value='tab-2-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Scenario 3', value='tab-3-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Scenario 4', value='tab-4-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Scenario 5', value='tab-5-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Scenario 6', value='tab-6-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),
        dcc.Tab(label='Comparison', value='tab-C-graph', style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#70a7bf', 'color': 'white'}, selected_style={'fontFamily': 'Helvetica', 'fontSize': '16px', 'backgroundColor': '#1F7799', 'color': 'white'}),        
    ]),
    html.Div(id='tabs-content')
])


# if-else code to call the corresponding graphs when a scenario tab is clicked
# more elaborate way

tab_figs = html.Div(id='tabs-content-graph')

@callback(Output('tabs-content-graph', 'children'),
              Input('tabs-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap1_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack1_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut1_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox1_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm1_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat1_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ1_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-2-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap2_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack2_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut2_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox2_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm2_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat2_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ2_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-3-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap3_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack3_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut3_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox3_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm3_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat3_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ3_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-4-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap4_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack4_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut4_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox4_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm4_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat4_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ4_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-5-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap5_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack5_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut5_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox5_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm5_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat5_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ5_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-6-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap6_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[stack6_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[donut6_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 30},
                ),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[nox6_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[pm6_layout]), className = 'h-50')
                ],
                style={'height': '100%'}, width=6)
            ],
            
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[mat6_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'}),
        dbc.Row(html.Div(children=[circ6_layout]), className = 'h-50',
        style={"height": "100vh", "background-color": 'white','padding': 15,'textAlign': 'center'})
         ], style={'padding': 0}, fluid=True)
    elif tab == 'tab-C-graph':
        return dbc.Container([
        dbc.Row(html.Div(children=[flowmap6_layout]), className='h-50', style={"padding-left": 0}),
        dbc.Row(html.Div(children=[km_C_layout]), className='h-100', style= {"height": "100vh", "background-color": 'white','padding': 30})
        ], style={'padding': 0}, fluid=True)


# calling the app and creating the layout of the dashboard

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

dashlayout = dbc.Container(
    [
        dbc.Row(html.Div(children=[header]), className = 'h-50'),
        dbc.Row(
            [
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[text1]), className = 'h-50')
                ],
                style={'height': '100%'}, width=7),            
                dbc.Col(children=[
                    dbc.Row(html.Div(children=[text2]), className = 'h-50')
                ],
                style={'height': '100%'}, width=5)
            ],
            className="h-100",
            style={"height": "100vh", "background-color": 'white','padding': 15},
                ),
        dbc.Row(html.Div(children=[tabs_layout]), className = 'h-auto'), 
        html.Br(),
        dbc.Row(html.Div(children=[tab_figs]), className = 'h-auto'),
        
    ], 
            fluid=True
)

app.layout = dashlayout

if __name__ == '__main__':
    app.run_server(debug=False)







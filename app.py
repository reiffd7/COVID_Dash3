import numpy as np
import pandas as pd
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

token = 'pk.eyJ1IjoicmVpZmZkIiwiYSI6ImNrOHFjaXlmOTAyaW0zamp6ZzI4NmtmMTQifQ.4EOhJ5NJJpawQnnoBXGCkw'
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
df = pd.read_csv(url, parse_dates=['date']).sort_index()
BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"

app = dash.Dash(__name__,
                external_stylesheets=[BS])
server = app.server


# colorsclae = ["#64c988", "#80d482", "#9cdf7c", "#bae976", "#d9f271", "#fafa6e"]


## data cleaning
df[df['county'] == 'New York City'] = df[df['county'] == 'New York City'].fillna(36061.0)
# df[(df['county'] == 'Kansas City') & (df['state'] == 'Missouri')] = df[(df['county'] == 'Kansas City') & (df['state'] == 'Missouri')].replace('Kansas City', 'Jackson')
# df[(df['county'] == 'Jackson') & (df['state'] == 'Missouri')] = df[(df['county'] == 'Jackson') & (df['state'] == 'Missouri')].replace(0.0, 29095.0)

## % change in cases over a week
df['cases 7 days ago'] = df.groupby('fips')['cases'].shift(7)
df['cases roc 7 days'] = round(((df['cases'] - df['cases 7 days ago'])/df['cases 7 days ago'].fillna(0))*100, 2)
# df1 = df[df['county'] == 'New York City']

df_latest = df[df['date'] == max(df['date'])]
df_latest = df_latest.dropna()
df_latest['fips'] = df_latest['fips'].apply(lambda x: str(int(x)).zfill(5))

## Choropleth Map
criteria = 'cases roc 7 days'
bins = [-5, 0, 5, 10, 15, 20, 25, 30]
fig = go.Figure()
for i, n in enumerate(bins):
    if i == 0:
        df = df_latest[df_latest[criteria] <= n]
        print('range 0 - {}'.format(n))
    elif i == len(bins) - 1:
        df = df_latest[df_latest[criteria] >= n]
        print('range 10000+')
    else:
        n_last = bins[i-1]
        df = df_latest[(df_latest[criteria] <= n) & (df_latest[criteria] > n_last)]
        print('range {} - {}'.format(n_last, n))
    print(list(df['county']))
    df['z'] = n
    fig.add_trace(go.Choroplethmapbox(
        geojson=counties,
        locations=df.fips,
        z=df.z,
        zmin = min(bins),
        zmax = max(bins),
        text = df.county,
        colorscale="Viridis"
    ))

fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                  mapbox_zoom=3, dragmode = 'lasso', mapbox_center = {"lat": 37.0902, "lon": -95.7129})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
				html.H4(children='US COVID-19 County Map')			
            ])
        ]),
        html.Div([
            dcc.Graph(
                id = 'county-choropleth',
                figure=fig
            )
        ]),
        html.Div([
            html.Pre(
                id = 'drag-data'
            )
        ])
    ])
])


@app.callback(
    Output('drag-data', 'children'),
    [Input('county-choropleth', 'selectedData')]
)
def display_selected_data(selectedData):
    if selectedData is None:
        return None
    else:
        return str(selectedData)







if __name__ == '__main__':
	app.run_server(debug=True)
    

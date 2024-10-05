import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

ARONDALE_LAT = 38.223
ARONDALE_LONG = -104.343
DEFAULT_LAT_RANGE = 5
DEFAULT_LONG_RANGE = 20

# Load data
df = pd.read_parquet('moisture.parquet')

print(f"Total rows: {len(df)}")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Global Soil Moisture Map"),
    dcc.Graph(id='soil-moisture-map'),
    html.Div([
        html.Div([
            html.Label("Latitude Range:"),
            dcc.Input(id='lat-min-input', type='number', placeholder='Min Latitude', debounce=True, value=round(ARONDALE_LAT - DEFAULT_LAT_RANGE / 2, 3)),
            dcc.Input(id='lat-max-input', type='number', placeholder='Max Latitude', debounce=True, value=round(ARONDALE_LAT + DEFAULT_LAT_RANGE / 2, 3))
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Longitude Range:"),
            dcc.Input(id='lon-min-input', type='number', placeholder='Min Longitude', debounce=True, value=round(ARONDALE_LONG - DEFAULT_LONG_RANGE / 2, 3)),
            dcc.Input(id='lon-max-input', type='number', placeholder='Max Longitude', debounce=True, value=round(ARONDALE_LONG + DEFAULT_LONG_RANGE / 2, 3))
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        html.Button('Update Map', id='submit-button', n_clicks=0, style={'margin-top': '20px'}),
    ], style={'margin-bottom': '20px'}),
    dcc.Dropdown(
        id='moisture-type-dropdown',
        options=[
            {'label': 'Surface Soil Moisture', 'value': 'surface_soil_moisture'},
            {'label': 'Root Zone Soil Moisture', 'value': 'root_zone_soil_moisture'}
        ],
        value='surface_soil_moisture',
        style={'width': '50%'}
    ),
    dcc.Slider(
        id='datetime-slider',
        min=df['date_time'].min().timestamp(),
        max=df['date_time'].max().timestamp(),
        value=df['date_time'].min().timestamp(),
        marks={int(date.timestamp()): date.strftime('%m-%d')
               for date in pd.date_range(start=df['date_time'].min(),
                                         end=df['date_time'].max(),
                                         freq='D')},  # Daily marks for readability
        step=None
    ),
    html.Div(id='datetime-display')
])

@app.callback(
    [Output('soil-moisture-map', 'figure'),
     Output('datetime-display', 'children')],
    [Input('submit-button', 'n_clicks'),  # Button click triggers the update
     Input('datetime-slider', 'value'),
     Input('moisture-type-dropdown', 'value')],
    [State('lat-min-input', 'value'),
     State('lat-max-input', 'value'),
     State('lon-min-input', 'value'),
     State('lon-max-input', 'value')]
)
def update_map(n_clicks, selected_timestamp, moisture_type, lat_min, lat_max, lon_min, lon_max):
    # Convert selected timestamp to datetime
    selected_datetime = pd.to_datetime(selected_timestamp, unit='s')

    # Filter DataFrame based on selected datetime and lat/lon ranges
    filtered_df = df[
        (df['date_time'] == selected_datetime) &
        (df['latitude'].between(lat_min, lat_max)) &
        (df['longitude'].between(lon_min, lon_max))
    ]

    # Create scatter mapbox figure
    fig = px.scatter_mapbox(filtered_df,
                            lat="latitude",
                            lon="longitude",
                            color=moisture_type,
                            zoom=5,
                            opacity=0.3,
                            center={"lat": ARONDALE_LAT,
                                    "lon": ARONDALE_LONG})
    fig.update_layout(mapbox_style="open-street-map")

    return fig, f"Selected DateTime: {selected_datetime}"

if __name__ == '__main__':
    app.run_server(debug=True)

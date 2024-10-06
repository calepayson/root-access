###########
# IMPORTS #
###########

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

#########
# SETUP #
#########

# Info message
INFO_MESSAGE = [
    "Welcome to Root Access.",
    "We use open source data from NASA to predict crop stress.",
    "Use the controls above to explore the tool or check out some examples with the buttons below.",
]

# Examples
EXAMPLES = [
    {'name': 'Example 1', 'id': 'example-button-1'},
    {'name': 'Example 2', 'id': 'example-button-2'},
    {'name': 'Example 2', 'id': 'example-button-3'},
]

# Turn on debounce to improve performance
DEBOUNCE = False

# Load data
df = pd.read_parquet('data/sif_moisture/sif_moisture.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Log number of rows
print(f"Total rows: {len(df)}")

# Initialize the app object
app = dash.Dash(__name__)

def presentation_info() -> html.Div:
    result = html.Div([
        *[html.P(line) for line in INFO_MESSAGE],
        html.Div([], className='presentation-info-separator'),
        *[html.Button(example['name'], id=example['id']) for example in EXAMPLES]
    ], className='presentation-info')
    return result

def latitude_controls(lat_min: float=-90.0, lat_max: float=90.0) -> html.Div:
    result = html.Div([
        html.Label("Latitude Range:"),
        html.Div([
            dcc.Input(
                id='lat-min-input',
                type='number',
                debounce=True,
                value=round(lat_min, 3),
                placeholder='Min Latitude',
                className='input-field'
            ),
            dcc.Input(
                id='lat-max-input',
                type='number',
                debounce=True,
                value=round(lat_max, 3),
                placeholder='Max Latitude',
                className='input-field'
            ),
        ], className='input-pair'),
    ], className='input-group')
    return result

def longitude_controls(long_min: float=-180.0, long_max: float=180.0) -> html.Div:
    result = html.Div([
        html.Label("Longitude Range:"),
        html.Div([
            dcc.Input(
                id='lon-min-input',
                type='number',
                debounce=True,
                value=round(long_min, 3),
                placeholder='Min Longitude',
                className='input-field'
            ),
            dcc.Input(
                id='lon-max-input',
                type='number',
                debounce=True,
                value=round(long_max, 3),
                placeholder='Max Longitude',
                className='input-field'
            ),
        ], className='input-pair'),
    ], className='input-group')
    return result

def data_type_dropdown() -> html.Div:
    result = html.Div([
        html.Label("Data Type:"),
        dcc.Dropdown(
            id='data-type-dropdown',
            options=[
                {'label': 'Surface Soil Moisture', 'value': 'water_prev1'},
                {'label': 'Root Zone Soil Moisture', 'value': 'root_water_prev1'},
                {'label': 'Solar-Induced Fluorescence', 'value': 'sif_value'}
            ],
            value='sif_value',
            clearable=False,
            className='dropdown-field'
        )
    ], className='input-group')
    return result

def date_time_slider() -> dcc.Slider:
    first_date = df['date'].min()
    last_date = df['date'].max()

    result = dcc.Slider(
        id='date-time-slider',
        min=first_date.timestamp(),
        max=last_date.timestamp(),
        value=first_date.timestamp(),
        marks={
            int(date.timestamp()): date.strftime('%Y-%m-%d')
            for date in pd.date_range(start=first_date, end=last_date, freq='D')
        },
        step=None
    )
    return result

# Build the app's HTML
app.layout = html.Div([
    # Title
    html.H1("Root Access", className='app-title'),

    html.Div([
        # Controls container
        html.Div([
            data_type_dropdown(),
            latitude_controls(),
            longitude_controls(),
            presentation_info(),
        ], className='controls-container'),

        # Map container
        html.Div([
            dcc.Graph(id='data-map', className='data-map')
        ], className='map-container'),
    ], className='content-container'),

    # Slider container
    html.Div([
        date_time_slider(),
    ], className='slider-container'),
], className='main-container')

@app.callback(
    Output('data-map', 'figure'),
    [Input('data-type-dropdown', 'value'),
     Input('lat-min-input', 'value'),
     Input('lat-max-input', 'value'),
     Input('lon-min-input', 'value'),
     Input('lon-max-input', 'value'),
     Input('date-time-slider', 'value')],
)
def update_map(
    selected_data_type: str, lat_min: float, lat_max: float, lon_min: float,
    lon_max: float, selected_timestamp: str
) -> go.Figure:

    # Convert selected_timestamp to datetime
    selected_datetime = pd.to_datetime(selected_timestamp, unit='s')

    # Filter the data frame based on user-input
    filtered_df = df[
        (df['sif_lat'].between(lat_min, lat_max)) &
        (df['sif_lon'].between(lon_min, lon_max)) &
        (df['date'] == selected_datetime)
    ]

    # Build the figure
    figure = px.scatter_mapbox(
        filtered_df,
        lat="sif_lat",
        lon="sif_lon",
        color=selected_data_type,
        zoom=3,
        opacity=0.3,
    )
    figure.update_layout(mapbox_style="open-street-map")
    return figure

# Run the server
if __name__ == "__main__":
    app.run_server(port=8051, debug=True)

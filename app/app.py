###########
# IMPORTS #
###########

from typing import Tuple
import dash
from dash import callback_context, dcc, html, Input, Output, no_update
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
    {
        'name': 'Example 1', 
        'id': 'example-button-1',
        'lat_min': 30.0,
        'lat_max': 40.0,
        'lon_min': -100.0,
        'lon_max': -90.0
    },
    {
        'name': 'Example 2', 
        'id': 'example-button-2',
        'lat_min': 40.0,
        'lat_max': 50.0,
        'lon_min': -80.0,
        'lon_max': -70.0
    },
    {
        'name': 'Example 3', 
        'id': 'example-button-3',
        'lat_min': -90.0,
        'lat_max': 90.0,
        'lon_min': -180.0,
        'lon_max': -70.0
    },
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

# Build the info specific for the presentation
def presentation_info() -> html.Div:
    result = html.Div([
        *[html.P(line) for line in INFO_MESSAGE],
        html.Div([], className='presentation-info-separator'),
        *[html.Button(
            example['name'], 
            id=example['id'],
            n_clicks=0,
        ) for example in EXAMPLES]
    ], className='presentation-info')
    return result

# Build the latitude controls
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

# Build the longitude controls
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

# Build the data-type dropdown
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

# Build the date-slider
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
            dcc.Graph(id='data-map', className='data-map'),
            dcc.Store(id='map-zoom-store', data={'zoom': 3})
        ], className='map-container'),
    ], className='content-container'),

    # Slider container
    html.Div([
        date_time_slider(),
    ], className='slider-container'),
], className='main-container')

# The main callback function to update the map upon user input
@app.callback(
    Output('data-map', 'figure'),
    [Input('data-type-dropdown', 'value'),
     Input('lat-min-input', 'value'),
     Input('lat-max-input', 'value'),
     Input('lon-min-input', 'value'),
     Input('lon-max-input', 'value'),
     Input('date-time-slider', 'value'),
     Input('map-zoom-store', 'data')],
)
def update_map(
    selected_data_type: str, lat_min: float, lat_max: float, lon_min: float,
    lon_max: float, selected_timestamp: str, zoom_state: dict
) -> go.Figure:

    # Convert selected_timestamp to datetime
    selected_datetime = pd.to_datetime(selected_timestamp, unit='s')

    # Filter the data frame based on user-input
    filtered_df = df[
        (df['sif_lat'].between(lat_min, lat_max)) &
        (df['sif_lon'].between(lon_min, lon_max)) &
        (df['date'] == selected_datetime)
    ]

    # Extract zoom from zoom_state
    current_zoom = zoom_state.get('zoom', 3)

    # Build the figure
    figure = px.scatter_mapbox(
        filtered_df,
        lat="sif_lat",
        lon="sif_lon",
        color=selected_data_type,
        zoom=current_zoom,
        opacity=0.3,
    )
    figure.update_layout(mapbox_style="open-street-map")
    return figure

# Callback to track changes in the map's zoom level
@app.callback(
    Output('map-zoom-store', 'data'),
    [Input('data-map', 'relayoutData')]
)
def update_zoom(relayout_data):
    if relayout_data and 'mapbox.zoom' in relayout_data:
        return {'zoom': relayout_data['mapbox.zoom']}
    return no_update

# A callback button to handl examples
@app.callback(
    [Output('lat-min-input', 'value'),
     Output('lat-max-input', 'value'),
     Output('lon-min-input', 'value'),
     Output('lon-max-input', 'value')],
    [Input('example-button-1', 'n_clicks'),
     Input('example-button-2', 'n_clicks'),
     Input('example-button-3', 'n_clicks')],
)
def update_coordinates(
    btn1_clicks: int, btn2_clicks: int, btn3_clicks: int
) -> Tuple[float, float, float, float]:
    # Default coordinates
    lat_min, lat_max = -90.0, 90.0
    lon_min, lon_max = -180.0, 180.0

    # Use callback_context to find out which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return lat_min, lat_max, lon_min, lon_max  # No button was clicked

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Map the button ID to the corresponding example
    for example in EXAMPLES:
        if example['id'] == button_id:
            lat_min, lat_max = example['lat_min'], example['lat_max']
            lon_min, lon_max = example['lon_min'], example['lon_max']
            break  # Exit the loop once the matching example is found

    return lat_min, lat_max, lon_min, lon_max


# Run the server
if __name__ == "__main__":
    app.run_server(port=8051, debug=True)

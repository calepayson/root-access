###########
# IMPORTS #
###########

import dash
from dash import dcc, html
import pandas as pd

#########
# SETUP #
#########

# Load data
df = pd.read_parquet('moisture.parquet')

# Log number of rows
print(f"Total rows: {len(df)}")

# Initialize the app object
app = dash.Dash(__name__)

def latitude_controls(lat_min: float, lat_max: float) -> html.Div:
    result =  html.Div([
        # Title
        html.Label("Latitude Range:"),

        # Minimum latitude input
        dcc.Input(
            id='lat-min-input',
            type='number',
            debounce=True,              # Only updates after a pause in input
            value=round(lat_min, 3)
        ),

        # Maximum latitude input
        dcc.Input(
            id='lat-max-input',
            type='number',
            debounce=True,              # Only updates after a pause in input
            value=round(lat_max, 3)
        ),
    ])
    return result

def longitude_controls(long_min: float, long_max: float) -> html.Div:
    result = html.Div([
        # Title
        html.Label("Longitude Range:"),

        # Minimum longitude input
        dcc.Input(
            id='long-min-input',
            type='number',
            debounce=True,
            value=round(long_min, 3)
        ),

        # Maximum longitude input
        dcc.Input(
            id='long-max-input',
            type='number',
            debounce=True,
            value=round(long_max, 3)
        ),
    ])
    return result

# Build the app's HTML
app.layout = html.Div([
    # Title
    html.H1("Root Access"),

    # Initialize the object that will become the map
    dcc.Graph(id='data-map'),

    # Initialize the controls
    html.Div([
        
    ]),
])

# Run the server
if __name__ == "__main__":
    app.run_server(port=8051, debug=True)

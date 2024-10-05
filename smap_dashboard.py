# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import pandas as pd

# # Load and filter data for California
# df = pd.read_parquet('moisture.parquet')


# print(f"Total rows: {len(df)}")

# app = dash.Dash(__name__)

# app.layout = html.Div([
#     html.H1("California Soil Moisture Map"),
#     dcc.Graph(id='soil-moisture-map'),
#     dcc.Dropdown(
#         id='moisture-type-dropdown',
#         options=[
#             {'label': 'Surface Soil Moisture', 'value': 'surface_soil_moisture'},
#             {'label': 'Root Zone Soil Moisture', 'value': 'root_zone_soil_moisture'}
#         ],
#         value='surface_soil_moisture',
#         style={'width': '50%'}
#     ),
#     dcc.Slider(
#         id='datetime-slider',
#         min=df['date_time'].min().timestamp(),
#         max=df['date_time'].max().timestamp(),
#         value=df['date_time'].min().timestamp(),
#         marks={int(date.timestamp()): date.strftime('%Y-%m-%d %H:%M')
#                for date in pd.date_range(start=df['date_time'].min(),
#                                          end=df['date_time'].max(),
#                                          freq='D')},  # Daily marks for readability
#         step=None
#     ),
#     html.Div(id='datetime-display')
# ])


# @app.callback(
#     [Output('soil-moisture-map', 'figure'),
#      Output('datetime-display', 'children')],
#     [Input('datetime-slider', 'value'),
#      Input('moisture-type-dropdown', 'value')]
# )
# def update_map(selected_timestamp, moisture_type):
#     selected_datetime = pd.to_datetime(selected_timestamp, unit='s')
#     filtered_df = df[df['date_time'] == selected_datetime]
    
#     fig = px.scatter_mapbox(filtered_df, 
#                             lat="latitude", 
#                             lon="longitude", 
#                             color=moisture_type,
#                             zoom=5, 
#                             center={"lat": 37.2, "lon": -119.3})
#     fig.update_layout(mapbox_style="open-street-map")
    
#     return fig, f"Selected DateTime: {selected_datetime}"


# if __name__ == '__main__':
#     app.run_server(debug=True)
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_parquet('moisture.parquet')

print(f"Total rows: {len(df)}")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("California Soil Moisture Map"),
    dcc.Graph(id='soil-moisture-map'),
    html.Div([
        html.Div([
            html.Label("Latitude Range:"),
            dcc.RangeSlider(
                id='lat-range-slider',
                min=df['latitude'].min(),
                max=df['latitude'].max(),
                value=[df['latitude'].min(), df['latitude'].max()],
                marks={i: f'{i:.1f}' for i in range(int(df['latitude'].min()), int(df['latitude'].max()) + 1, 2)},
                step=0.1
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Longitude Range:"),
            dcc.RangeSlider(
                id='lon-range-slider',
                min=df['longitude'].min(),
                max=df['longitude'].max(),
                value=[df['longitude'].min(), df['longitude'].max()],
                marks={i: f'{i:.1f}' for i in range(int(df['longitude'].min()), int(df['longitude'].max()) + 1, 2)},
                step=0.1
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
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
        marks={int(date.timestamp()): date.strftime('%Y-%m-%d %H:%M')
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
    [Input('datetime-slider', 'value'),
     Input('moisture-type-dropdown', 'value'),
     Input('lat-range-slider', 'value'),
     Input('lon-range-slider', 'value')]
)
def update_map(selected_timestamp, moisture_type, lat_range, lon_range):
    selected_datetime = pd.to_datetime(selected_timestamp, unit='s')
    filtered_df = df[
        (df['date_time'] == selected_datetime) &
        (df['latitude'].between(lat_range[0], lat_range[1])) &
        (df['longitude'].between(lon_range[0], lon_range[1]))
    ]

    fig = px.scatter_mapbox(filtered_df,
                            lat="latitude",
                            lon="longitude",
                            color=moisture_type,
                            zoom=5,
                            center={"lat": (lat_range[0] + lat_range[1]) / 2,
                                    "lon": (lon_range[0] + lon_range[1]) / 2})
    fig.update_layout(mapbox_style="open-street-map")

    return fig, f"Selected DateTime: {selected_datetime}"

if __name__ == '__main__':
    app.run_server(debug=True)

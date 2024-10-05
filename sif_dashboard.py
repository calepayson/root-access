import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_parquet('oco3_sif.parquet')

print(f"Total rows: {len(df)}")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("OCO-3 Solar-Induced Fluorescence (SIF) Map"),
    dcc.Graph(id='sif-map'),
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
        id='data-type-dropdown',
        options=[
            {'label': 'SIF', 'value': 'sif'},
            {'label': 'SIF Uncertainty', 'value': 'sif_uncertainty'}
        ],
        value='sif',
        style={'width': '50%'}
    ),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        initial_visible_month=df['date'].min(),
        date=df['date'].min()
    ),
    html.Div(id='date-display')
])

@app.callback(
    [Output('sif-map', 'figure'),
     Output('date-display', 'children')],
    [Input('date-picker', 'date'),
     Input('data-type-dropdown', 'value'),
     Input('lat-range-slider', 'value'),
     Input('lon-range-slider', 'value')]
)
def update_map(selected_date, data_type, lat_range, lon_range):
    selected_date = pd.to_datetime(selected_date)
    filtered_df = df[
        (df['date'] == selected_date) &
        (df['latitude'].between(lat_range[0], lat_range[1])) &
        (df['longitude'].between(lon_range[0], lon_range[1]))
    ]

    fig = px.scatter_mapbox(filtered_df,
                            lat="latitude",
                            lon="longitude",
                            color=data_type,
                            zoom=3,
                            center={"lat": (lat_range[0] + lat_range[1]) / 2,
                                    "lon": (lon_range[0] + lon_range[1]) / 2})
    fig.update_layout(mapbox_style="open-street-map")

    return fig, f"Selected Date: {selected_date.date()}"

if __name__ == '__main__':
    app.run_server(debug=True)

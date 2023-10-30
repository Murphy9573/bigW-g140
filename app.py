import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dcc


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#fig.update_layout(autosize=True)
app.layout = html.Div([
    dcc.Dropdown(
        id='filter-dropdown',
        options=[{'label': f'Store ID {i}', 'value': i} for i in data_merge['store_id'].unique()],
        value=data_merge['store_id'].unique()[0]
    ),
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[
            dcc.Graph(id='line-plot'
            )
        ]),
        dcc.Tab(label='Tab two', children=[
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [dcc.Graph(id='histogram-plot', className="h-100")],
                                width=6,
                                className="h-100",
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        dbc.Col(
                                            dcc.Graph(figure={'data': [{'x': [1, 2, 3], 'y': [4, 1, 2],'type': 'bar', 'name': 'SF'},{'x': [1, 2, 3], 'y': [2, 4, 5],'type': 'bar', 'name': 'Montréal'},]}, className="h-100"),
                                            className="h-100",
                                        ),
                                        className="h-50",
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            dcc.Graph(id='map-graph', className="h-100"),
                                            className="h-100",
                                        ),
                                        className="h-50",
                                    ),
                                ],
                                width=6,
                                className="h-100",
                            ),
                        ],
                        className="h-100",
                    )
                ],
                fluid=True,
                className="vh-100",
            )
        ]),
    ])
])

@app.callback(
    Output('line-plot', 'figure'),
    [Input('filter-dropdown', 'value')]
)
def update_line_plot(selected_store_id):
    unique_dates = data_merge['financial_week_end_date'].unique()
    grouped = data_merge.groupby(['financial_week_end_date', 'store_id'])['total_sale_value'].sum().reset_index()
    fig = px.line(grouped, x='financial_week_end_date', y='total_sale_value', color='store_id')

    for trace in fig.data:
        if trace.name == str(selected_store_id):
            trace.line.color = 'rgba(0, 0, 255, 2)' 
        else:
            trace.line.color = 'rgba(192, 192, 192, 0.08)'  
    
    return fig

@app.callback(
    Output('map-graph', 'figure'),
    Input('filter-dropdown', 'value')
)
def update_map(store_id):

    fig = px.scatter_mapbox(data_merge, lat="store_latitude", lon="store_longitude", hover_name="store_state",
                            hover_data=["store_postcode", "population", 'Median income'],
                            color_discrete_sequence=["gold"], zoom=3, height=300)
    
    if store_id:
        selected_store = data_merge[data_merge['store_id'] == store_id]
        fig.add_trace(px.scatter_mapbox(selected_store, lat="store_latitude", lon="store_longitude",
                                        hover_name="store_state", hover_data=["store_postcode", "population", 'Median income']).data[0])

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

@app.callback(
    Output("histogram-plot", "figure"),
    [Input('filter-dropdown', 'value')]
)
def update_histogram(store_id):
    selected_data = data_merge[data_merge['store_id'] == store_id]
    fig = px.histogram(selected_data, x="sales_channel", y="total_sale_value",
                       color='price_stage', barmode='group', height=400)
    
    colors = ['blue', 'grey', 'gold']
    for i, trace in enumerate(fig.data):
        trace.marker.color = colors[i]
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)

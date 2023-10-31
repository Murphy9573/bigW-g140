import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dcc

data_merge=pd.read_csv('data_merge.csv')

external_stylesheets = [
    dbc.themes.BOOTSTRAP, 
    "style.css"  
]

app = Dash(external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(
        children="Big W Sales Analysis",
        style={
            "textAlign": "center",
            "font-size": "70px",
            "font-weight": "600",
            "background-image": "linear-gradient(to right, #0000FF 45%, #FFD700)",
            "color": "transparent",
            "background-clip": "text",
            "-webkit-background-clip": "text",
        },
    ),
    dcc.Dropdown(
        id='filter-dropdown',
        options=[{'label': f'Store ID {i}', 'value': i} for i in data_merge['store_id'].unique()],
        value=data_merge['store_id'].unique()[0]
    ),
    html.Div(
        style={"margin-top": "10px", 'display': 'flex', 'justify-content': 'space-between'},
        children=[
            html.Div('', id='total_sales', className="top-item", style={'margin-right': '20px', 'height': '35px'}),
            html.Div('', id='promotion_sales', className="top-item", style={'margin-right': '20px', 'height': '35px'}),
            html.Div('', id='media_spend', className="top-item", style={'height': '35px'}),
        ]
    ),
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[
            dcc.Graph(id='line-plot')
        ]),
        dcc.Tab(label='Tab two', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(id='histogram-plot', className="h-100"),
                        width=6,
                        #className="h-100"
                    ),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(
                                html.Div(style={'margin-top': '100px'}, children=[
                                    html.Div(style={'display': 'flex'}, children=[
                                        html.Span(className="distance-title", children='Distance To:')
                                    ]),
                                    html.Div(id="kmart_div", style={'margin-top': '20px', 'display': 'flex'}),
                                    html.Div(id="target_div", style={'margin-top': '20px', 'display': 'flex'}),
                                    html.Div(style={'margin-top': '20px', 'display': 'flex'}, children=[
                                        html.Span(className="distance-item-title", children='Woolworth'),
                                        html.Span(id="woolworth_state", className="distance-item-title", style={"margin-left": "0px"})
                                    ])
                                ], 
                            className="h-50"),
                            )
                        ]),
                        dbc.Row(
                            dbc.Col(
                                dcc.Graph(id='map-graph', className="h-100"),
                                className="h-100"
                            ),
                            className="h-50",
                        )
                    ],
                        width=6,
                        #className="h-100"
                    )
                ])
            ])
        ])
    ])
])







@app.callback(
    Output('line-plot', 'figure'),
    Input('filter-dropdown', 'value')
)
def update_line_plot(selected_store_id):
    unique_dates = data_merge['financial_week_end_date'].unique()
    grouped = data_merge.groupby(['financial_week_end_date', 'store_id'])['total_sale_value'].sum().reset_index()
    fig = px.line(grouped, x='financial_week_end_date', y='total_sale_value', color='store_id',title="Sales Value Changing by Time")
    fig.update_traces(showlegend=False)
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
    fig.update_layout(title="<b>Store Locations Around Australia</b>",title_x=0.5,title_y=0.95,title_font=dict(size=24))
    return fig

@app.callback(
    Output("histogram-plot", "figure"),
    Input('filter-dropdown', 'value')
)
def update_histogram(store_id):
    selected_data = data_merge[data_merge['store_id'] == store_id]
    fig = px.histogram(selected_data, x="sales_channel", y="total_sale_value",
                       color='price_stage', barmode='group', height=400,title="Customers Segementation")
    
    colors = ['blue', 'grey', 'gold']
    for i, trace in enumerate(fig.data):
        trace.marker.color = colors[i]
    
    return fig

def get_distance_item(title,content,width,color):
    return [
                html.Span(className="distance-item-title", children=title),
                html.Div(style={"background-color": f"{color}","height":"20px","width":f"{width}","align-items": "center",'display': 'flex'}, children=[
                    html.Span(className="distance-item-title",style={"margin-left":"0px","width":"200px"}, children=content),
                ])
            ]
@app.callback(
    [Output('total_sales', 'children'),
     Output('promotion_sales', 'children'),
     Output('media_spend', 'children'),
     Output('kmart_div', 'children'),
     Output('target_div', 'children'),
     Output('woolworth_state', 'children')
    ],
    Input('filter-dropdown', 'value')
)

def updata_store_data(store):
    store_df = data_merge[data_merge.store_id == store].copy()
    total_sale_value = store_df.total_sale_value.sum()
    total_promotional_sales_value = store_df.total_promotional_sales_value.sum()
    media_spend = store_df.media_spend.sum()
    
    kmart_discount = str(store_df["distance_to_kmart"].values[0])
    kmart_width = "240px"
    if kmart_discount == "<1 KM":
        kmart_width = "60px"
    elif kmart_discount == "1-3 KM":
        kmart_width = "120px"
    elif kmart_discount == "3-5 KM":
        kmart_width = "180px"
    elif kmart_discount == ">5 KM":
        kmart_width = "240px"
    kmart_color = "white"
    if kmart_discount != "Same Centre":
        kmart_color = "orange"
        
    target_discount = str(store_df["distance_to_target"].values[0])
    target_width = "240px"
    if target_discount == "<1 KM":
        target_width = "60px"
    elif target_discount == "1-3 KM":
        target_width = "120px"
    elif target_discount == "3-5 KM":
        target_width = "180px"
    elif target_discount == ">5 KM":
        target_width = "240px"
    target_color = "white"
    if target_discount != "Same Centre":
        target_color = "orange"
    
    woolworth = store_df["co_location_flag"].values[0]
    woolworth_str = "✓"
    if woolworth == False:
        woolworth_str = "✗"
    
        
    return [f'Total Sales : {str(round(total_sale_value,2))}',
            f"Promotion Sales : {str(round(total_promotional_sales_value,2))}",
            f"Media Spend : {str(round(media_spend,2))}",
            get_distance_item("Kmart",kmart_discount,kmart_width,kmart_color),
            get_distance_item("Target",target_discount,target_width,target_color),
            woolworth_str]


if __name__ == "__main__":
    app.run_server(debug=True, port=8061)

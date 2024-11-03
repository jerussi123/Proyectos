import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import tensorflow as tf
import keras
import math  

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

model = keras.models.load_model('proyecto2/Ciencia_de_Datos/modelo_proyecto2f.keras')

home_layout = html.Div([html.H1("Home"), html.P("Welcome to the Home page!")])
data_exploration_layout = html.Div([html.H1("Data Exploration"), html.P("Explore your data here!")])
predictions_layout = html.Div([html.H1("Predictions"), html.P("Make predictions with your data!")])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/home", active=True)),
            dbc.NavItem(dbc.NavLink("Data Exploration", href="/data-exploration")),
            dbc.NavItem(dbc.NavLink("Predictions", href="/predictions")),
            dbc.Form(className="d-flex me-2", children=[
                dcc.Input(type="search", placeholder="Search", className="form-control me-2"),
                dbc.Button("Search", color="secondary", className="my-2 my-sm-0"),
            ])
        ],
        brand="Bank Data Analytics",
        brand_href="#",
        color="primary",
        dark=True,
        expand="lg",
        className="mb-4",
    ),
    html.Div(id='page-content') #
])

# Callback de la barra de navegacion
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/home':
        return home_layout
    elif pathname == '/data-exploration':
        return data_exploration_layout
    elif pathname == '/predictions':
        return predictions_layout
    else:
        return home_layout  # Home si no funciona
    
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
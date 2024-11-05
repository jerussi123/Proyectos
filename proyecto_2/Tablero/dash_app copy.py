import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv # pip install python-dotenv
import os
import psycopg2
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde
import numpy as np
import tensorflow as tf
import keras
import math  

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)

env_path="c:/Users/jorru/OneDrive - Universidad de los andes/Maestria/Analítica_computacional/Talleres/Taller_10/env/app.env"
# load env 
load_dotenv(dotenv_path=env_path)
# extract env variables
USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')
DBHOST=os.getenv('DBHOST')
PORT=os.getenv('PORT')
DBNAME=os.getenv('DBNAME')

#connect to DB
print(DBNAME)
print(USER)
print(PASSWORD)
print(DBHOST)
print(PORT)
engine = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=DBHOST,
    port=PORT
)

cursor = engine.cursor()

query = """
SELECT * 
FROM prodq1;"""
df = pd.read_sql(query, engine)
df

# Data limpia
df_numerico = df.select_dtypes(include=['float64', 'int64'])

# Variables x numericas
numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
df_yes = df[df['y'] == "yes"]

# Funciones para las graficas de informacion personal del cliente
# Histogramas que se usaran para las variables numericas
def create_histogram_with_kde(column_name,spanish_name,color_type):
    hist_trace = go.Histogram(
        x=df_yes[column_name],
        nbinsx=20,
        name=f'{column_name} Distribution',
        marker=dict(color=color_type, line=dict(color='black', width=1)),
        opacity=0.6
    )

    fig = go.Figure(data=[hist_trace])
    fig.update_layout(
        title=f'Aceptación del deposito según {spanish_name}',
        title_font=dict(size=20, family="Times New Roman", color='black', weight='bold'),
        xaxis_title=spanish_name,
        xaxis_title_font=dict(size=16, family="Times New Roman", color='black', weight='bold'),
        yaxis_title='Frecuencia',
        yaxis_title_font=dict(size=16, family="Times New Roman", color='black', weight='bold'),
        showlegend=False,
        template="plotly_white",
        height=550,
        width=700,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# Grafica de area normalizada para las variables categoricas
def create_stacked_area_plot(column, spanish_name, plot_width, color_type1, color_type2):
    order = df[column].unique()
    result_df = df.groupby(column)['y'].value_counts().unstack(fill_value=0)
    result_df = result_df.reindex(order, fill_value=0)
    total_responses = result_df.sum(axis=1)
    
    no_percentage = (result_df['no'] / total_responses) * 100
    yes_percentage = (result_df['yes'] / total_responses) * 100
    no_cumulative = no_percentage
    yes_cumulative = yes_percentage + no_cumulative

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=order, y=no_cumulative, fill='tonexty', mode='none',
        fillcolor=color_type1, name='No'
    ))
    fig.add_trace(go.Scatter(
        x=order, y=yes_cumulative, fill='tonexty', mode='none',
        fillcolor=color_type2, name='Yes'
    ))

    fig.update_layout(
        title=f'Porcentaje acumulado por {spanish_name}',
        title_font=dict(size=20, family="Times New Roman", color='black', weight='bold'),
        xaxis_title=spanish_name,
        xaxis_title_font=dict(size=16, family="Times New Roman", color='black', weight='bold'),
        yaxis_title="Porcentaje acumulado",
        yaxis_title_font=dict(size=16, family="Times New Roman", color='black', weight='bold'),
        template="plotly_white",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        margin=dict(t=100, b=50, l=50, r=50),
        yaxis=dict(tickformat=".1f", range=[0, 100]),
        width=plot_width
    )
    return fig

# Grafica de area normalizada, para los meses
def create_stacked_area_plot_months():
    months_order = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    result_df = df.groupby('month')['y'].value_counts().unstack(fill_value=0)
    result_df = result_df.reindex(months_order, fill_value=0)
    total_responses = result_df.sum(axis=1)
    
    no_percentage = (result_df['no'] / total_responses) * 100
    yes_percentage = (result_df['yes'] / total_responses) * 100
    no_cumulative = no_percentage
    yes_cumulative = yes_percentage + no_cumulative

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months_order, y=no_cumulative, fill='tonexty', mode='none',
        fillcolor='rgba(2, 117, 216, 0.7)', name='No'
    ))
    fig.add_trace(go.Scatter(
        x=months_order, y=yes_cumulative, fill='tonexty', mode='none',
        fillcolor='rgba(2, 117, 216, 0.3)', name='Yes'
    ))

    fig.update_layout(
        title="Porcentaje acumulado por Mes",
        xaxis_title="Mes",
        yaxis_title="Porcentaje acumulado",
        template="plotly_white",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        margin=dict(t=100, b=50, l=50, r=50),
        yaxis=dict(tickformat=".1f", range=[0, 100])
    )
    return fig

# Se trae el modelo, para poder predecir
model = keras.models.load_model('proyecto_2/Ciencia_de_Datos/modelo_proyecto2f.keras')

# Layout de la pestaña de inicio del dash
home_layout = html.Div([
    html.H1("Bank Data Analytics", style={'textAlign': 'center'}),
    html.H4("Bienvenido a la Plataforma de Análisis de Datos Bancarios!", style={'textAlign': 'center'}),
    # Texto explicatorio del tablero
    dbc.Card([
        dbc.CardBody([
            html.P(
                """En esta aplicación, podrás explorar los resultados de un trabajo realizado por un grupo de estudiantes 
                de la clase de analítica computacional para la toma de desiciones. Hemos diseñado esta plataforma para que puedas 
                acceder a un análisis profundo de nuestros datos, lo que te permitirá entender mejor las variables que tenemos 
                a nuestra disposición y cómo estas se relacionan con el comportamiento de compra de los clientes, así como su 
                interés en productos como Certificados de Depósito a Término (CDTs).
                
                Además, tendrás la oportunidad de ingresar información de un nuevo cliente en nuestra sección de 
                predicciones. A través de este proceso, podrás evaluar si este cliente tiene un alto potencial de 
                convertirse en un cliente valioso para el banco.

                Te invitamos a navegar por las diferentes secciones de la aplicación y descubrir todo lo que tenemos 
                para ofrecerte.""",
                style={
                    'textAlign': 'justify',
                    'margin': '0 auto',
                    'maxWidth': '1100px',
                    'padding': '10px'
                }
            ),
        ])
    ], className="mt-4 border-primary", style={'borderWidth': '2px', 'borderStyle': 'solid', 'marginTop': '5px'}),
    dbc.Card([
        dbc.CardBody([
            html.H5("Trabajo realizado por:", style={'textAlign': 'center'}),
            html.P("- Analista de negocios y Diseñador del tablero: Jorge Russi", style={'textAlign': 'center'}),
            html.P("- Ingeniero de datos y Científico de datos: Cristian Rincón ", style={'textAlign': 'center'}),
            html.P("- Analista de datos y Encargado del despliegue: Samuel Pedroza", style={'textAlign': 'center'})
        ])
    ], className="mt-4 border-secondary", style={'borderWidth': '2px', 'borderStyle': 'solid'}),
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('los_andes.png'), style={'width': '20%', 'margin': '1px'}),
            html.Img(src=app.get_asset_url('actd_pic.jpg'), style={'width': '80%', 'margin': '1px'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '10px'})
    ])
])

# Layout de la pestaña de exploracion de data del dash
data_exploration_layout = html.Div([
    html.H1("Exploracion de data", style={'textAlign': 'center'}),
    html.P("""Aca podran encontrar graficos que nos explicaran como cada una de las variables se relacionan 
            con con el comportamiento de compra de los clientes. Esta informacion esta repartida en 3 bloques:""", 
            style={'textAlign': 'center',
                    'margin': '0 auto',
                    'maxWidth': '1500px',
                    'padding': '10px'}),
    html.P("Informacion personal del cliente", style={'textAlign': 'center'}),
    html.P("Informacion relacionada con el ultimo contacto del cliente", style={'textAlign': 'center'}),
    html.P("Informacion adicional de la ultima campaña del cliente", style={'textAlign': 'center'}),

    # Primera caja con los grafiicos de informacion personal del cliente
    html.H2(" Información personal del cliente:", className="text-primary", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='age-histogram-with-kde',
                        figure=create_histogram_with_kde('age', 'Edad del cliente', 'rgba(0, 74, 117, 1)') 
                    ),
                ]),
                dbc.Col([
                    dcc.Graph(
                        id='balance-histogram-with-kde',
                        figure=create_histogram_with_kde('balance', 'Saldo promedio anual', 'rgba(0, 74, 117, 1)')
                    ),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='housing-stacked-area-plot',
                        figure=create_stacked_area_plot('housing', 'si tiene Hipoteca o no', 500,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
                    ),
                ], width=4),
                dbc.Col([
                    dcc.Graph(
                        id='loan-stacked-area-plot',
                        figure=create_stacked_area_plot('loan', 'si tiene Prestamos o no', 500,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
                    ),
                ], width=4),
                dbc.Col([
                    dcc.Graph(
                        id='default-stacked-area-plot',
                        figure=create_stacked_area_plot('default', 'si tiene Impagos o no', 500,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
                    ),
                ], width=4),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='marital-stacked-area-plot',
                        figure=create_stacked_area_plot('marital', 'Estado civil del cliente', 750,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
                    ),
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='education-stacked-area-plot',
                        figure=create_stacked_area_plot('education', 'Nivel educativo del cliente', 750,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
                    ),
                ], width=6),
            ]),
            dcc.Graph(
                id='job-stacked-area-plot',
                figure=create_stacked_area_plot('job', 'Ocupación del cliente', 1500,'rgba(0, 74, 117, 0.7)','rgba(0, 74, 117, 0.3)')
            )
        ])
    ], className="mt-4 border-primary", style={'borderWidth': '2px', 'borderStyle': 'solid', 'marginTop': '5px'}),
    html.Div(style={'height': '30px'}),
    # Segunda caja con la informacion relacionada con el ultimo contacto con el cliente
    html.H2(" Información relacionada con el último contacto con el cliente:", className="text-info", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='duration-histogram-with-kde',
                        figure=create_histogram_with_kde('duration', 'Duración del ultimo contacto', 'rgba(2, 117, 216, 1)')
                    ),
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='day-histogram-with-kde',
                        figure=create_histogram_with_kde('day', 'Día del mes', 'rgba(2, 117, 216, 1)') 
                    ),
                ], width=6)
            ]),
            dcc.Graph(
                id='contact-stacked-area-plot',
                figure=create_stacked_area_plot('contact', 'tipo de Comunicación', 1500,'rgba(2, 117, 216, 0.7)','rgba(2, 117, 216, 0.3)')
            ),
            dcc.Graph(
                id='months-stacked-area-plot',
                figure=create_stacked_area_plot_months()
            ),
        ])
    ], className="mt-4 border-info", style={'borderWidth': '2px', 'borderStyle': 'solid', 'marginTop': '5px'}),
    html.Div(style={'height': '30px'}),

    # Tercer caja con la informacion adicional de la ultima campaña
    html.H2(" Información adicional sobre la campaña:", className="text-success", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='campain-histogram-with-kde',
                        figure=create_histogram_with_kde('campaign', 'cantidad de Contactos durante esta campaña', 'green') 
                    ),
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='pdays-histogram-with-kde',
                        figure=create_histogram_with_kde('pdays', 'número de Días que pasaron desde una campaña anterior', 'green')
                    ),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='previous-histogram-with-kde',
                        figure=create_histogram_with_kde('previous', 'cantidad de Contactos antes de esta campaña', 'green')
                    ),
                ], width=6),
                dbc.Col([
                   dcc.Graph(
                        id='poutcome-stacked-area-plot',
                        figure=create_stacked_area_plot('poutcome', 'Resultado en la ultima campaña', 750,'rgba(0, 128, 0, 0.7)','rgba(0, 128, 0, 0.3)')
                    ), 
                ], width=6),
            ]),
        ])
    ], className="mt-4 border-info", style={'borderWidth': '2px', 'borderStyle': 'solid', 'marginTop': '5px'})
])

# Layout de la pestaña de predicciones del dash
predictions_layout = html.Div([
    html.H1("Predicciones", style={'textAlign': 'center'}),
    html.H3("Ingrese los datos del cliente:", style={'textAlign': 'center'}),
    # Primer caja, con el primer set de inputs
    html.H4(" Información personal del cliente:", className="text-primary", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            # Linea numero 1 de la caja, con age, housing, loan, default y balance
            dbc.Row([
                dbc.Col([
                    html.Label("Selecione Edad:", className="form-label"),
                    dcc.Slider(
                        id="age-slider",
                        min=18,
                        max=90,
                        step=1,
                        value=None,
                        marks={i: str(i) for i in range(10, 90, 10)},
                        className="form-range"
                    ),
                    html.Div(id='age-slider-value', className='mt-2'),
                ], width=4),

                dbc.Col([
                    html.Label("¿Tiene alguna hipoteca?", className="form-label mt-2"),
                    dcc.RadioItems(
                        id='housing-options',
                        options=[
                            {'label': ' Si', 'value': 'yes'},
                            {'label': ' No', 'value': 'no'},
                        ],
                        value=None,  
                        labelStyle={'display': 'block'} 
                    )
                ], width=2),
                dbc.Col([
                    html.Label("¿Tiene algun prestamo?", className="form-label mt-2"),
                    dcc.RadioItems(
                        id='loan-options',
                        options=[
                            {'label': ' Si', 'value': 'yes'},
                            {'label': ' No', 'value': 'no'},
                        ],
                        value=None,  
                        labelStyle={'display': 'block'} 
                    )
                ], width=2),
                dbc.Col([
                    html.Label("¿Tiene algun incumplimiento con sus pagos?", className="form-label mt-2"),
                    dcc.RadioItems(
                        id='default-options',
                        options=[
                            {'label': ' Si', 'value': 'yes'},
                            {'label': ' No', 'value': 'no'},
                        ],
                        value=None,  
                        labelStyle={'display': 'block'} 
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Ingrese el saldo promedio anual, en euros:", className="form-label mt-2"),
                    dbc.InputGroup([
                        dbc.InputGroupText("$"), 
                        dbc.Input(
                            id="balance-input",
                            type="number",
                            placeholder="Monto en euros",
                            min=1, 
                            max=100000, 
                            step=1, 
                            required=True,
                            value=""
                        ),
                        dbc.InputGroupText(".00") 
                    ]),
                ], width=2)
            ], className="mb-4"),
            # Linea 2 de la primer caja, tiene job, marital, education
            dbc.Row([
                dbc.Col([
                    html.Label("Seleccione la ocupación:", className="form-label"),
                    dcc.Dropdown(
                        id="job-dropdown",
                        options=[
                            {'label': 'Administrativo', 'value': 'admin'},
                            {'label': 'Ocupación desconocida', 'value': 'unknown'},
                            {'label': 'Desempleado', 'value': 'unemployed'},
                            {'label': 'Gerente', 'value': 'management'},
                            {'label': 'Persona de servicios', 'value': 'housemaid'},
                            {'label': 'Emprendedor', 'value': 'entrepreneur'},
                            {'label': 'Estudiante', 'value': 'student'},
                            {'label': 'Obrero', 'value': 'blue-collar'},
                            {'label': 'Independiente', 'value': 'self-employed'},
                            {'label': 'Retirado', 'value': 'retired'},
                            {'label': 'Técnico', 'value': 'technician'},
                            {'label': 'Prestador de servicios', 'value': 'services'},
                        ],
                        value=None,
                    )
                ], width=4),

                dbc.Col([
                    html.Label("Seleccione el estado civil:", className="form-label"),
                    dcc.Dropdown(
                        id="marital-dropdown",
                        options=[
                            {'label': 'Casado(a)', 'value': 'married'},
                            {'label': 'Divorciado(a)', 'value': 'divorced'},
                            {'label': 'Soltero(a)', 'value': 'single'},
                        ],
                        value=None,
                    )
                ], width=4),

                dbc.Col([
                    html.Label("Seleccione el nivel de educación:", className="form-label"),
                    dcc.Dropdown(
                        id="education-dropdown",
                        options=[
                            {'label': 'Primaria', 'value': 'primary'},
                            {'label': 'Secundaria', 'value': 'secundary'},
                            {'label': 'Educación superior', 'value': 'tertiary'},
                            {'label': 'Nivel desconocido', 'value': 'Unkown'},
                        ],
                        value=None,
                    )
                ], width=4)
            ])
        ])
    ], className="mt-4 border-primary", style={'borderWidth': '2px', 'borderStyle': 'solid'}),
    
    # Barra de progreso
    dbc.Progress(id="progress-bar1", value=0, className="mt-3", color="primary"),
    html.Div(style={'height': '30px'}),

    # Segunda caja, con el segundo set de inputs
    html.H4(" Información relacionada con el último contacto con el cliente:", className="text-info", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            # Unica linea de esta caja, tiene day, duration, month y contact
            dbc.Row([
                dbc.Col([
                    html.Label("¿Día del mes del último contacto con el cliente?", className="form-label"),
                    dcc.Slider(
                        id="day-slider",
                        min=1,
                        max=31,
                        step=1,
                        value=None,
                        marks={i: str(i) for i in range(1, 31, 5)},
                        className="form-range"
                    ),
                    html.Div(id='day-slider-value', className='mt-2'),
                ], width=4),
                dbc.Col([
                    html.Label("Duración del último contacto, en segundos:", className="form-label mt-2"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="duration-input",
                            type="number",
                            placeholder="Segundos",
                            min=1, 
                            max=4918, 
                            step=1, 
                            required=True,
                            value=""
                        ),
                    ]),
                ], width=2),
                dbc.Col([
                    html.Label("¿Mes del último contacto con el cliente?", className="form-label mt-2"),
                    dcc.Dropdown(
                        id="month-dropdown",
                        options=[
                            {'label': 'Enero', 'value': 'jan'},
                            {'label': 'Febrero', 'value': 'feb'},
                            {'label': 'Marzo', 'value': 'mar'},
                            {'label': 'Abril', 'value': 'apr'},
                            {'label': 'Mayo', 'value': 'may'},
                            {'label': 'Junio', 'value': 'jun'},
                            {'label': 'Julio', 'value': 'jul'},
                            {'label': 'Agosto', 'value': 'aug'},
                            {'label': 'Septiembre', 'value': 'sep'},
                            {'label': 'Octubre', 'value': 'oct'},
                            {'label': 'Noviembre', 'value': 'nov'},
                            {'label': 'Diciembre', 'value': 'dec'},
                        ],
                        value=None,
                    )
                ], width=3),
                dbc.Col([
                    html.Label("¿Vía por la cual se contactó al cliente?", className="form-label mt-2"),
                    dcc.Dropdown(
                        id="contact-dropdown",
                        options=[
                            {'label': 'Teléfono fijo', 'value': 'telephone'},
                            {'label': 'Celular', 'value': 'cellular'},
                            {'label': 'Desconocida', 'value': 'unknown'},
                        ],
                        value=None,
                    )
                ], width=3)
            ])
        ])
    ], className="mt-4 border-info", style={'borderWidth': '2px', 'borderStyle': 'solid'}),

    # Barra de progreso
    dbc.Progress(id="progress-bar2", value=0, className="mt-3", color="info"),
    html.Div(style={'height': '30px'}),

    # Tercer caja, con el tercer set de inputs
    html.H4(" Información adicional sobre la campaña:", className="text-success", style={'paddingLeft': '20px', 'paddingRight': '20px'}),
    dbc.Card([
        dbc.CardBody([
            # Unica linea de esta caja, tiene poutcome, campain, pdays, previous
            dbc.Row([
                dbc.Col([
                    html.Label("Resultado de la anterior campaña de marketing:", className="form-label mt-2"),
                    dcc.Dropdown(
                        id="poutcome-dropdown",
                        options=[
                            {'label': 'Triunfo', 'value': 'success'},
                            {'label': 'Fracaso', 'value': 'failure'},
                            {'label': 'Desconocido', 'value': 'unknown'},
                            {'label': 'Otro', 'value': 'other'}
                        ],
                        value=None,
                    )
                ], width=3),
                dbc.Col([
                    html.Label("¿Número de veces que se contactó este cliente durante la campaña?", className="form-label mt-2"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="campain-input",
                            type="number",
                            placeholder="Cantidad de veces",
                            min=1, 
                            max=63, 
                            step=1, 
                            required=True,
                            value=""
                        ),
                    ]),
                ], width=3),
                dbc.Col([
                    html.Label("¿Número de días que pasaron desde que el cliente había sido contactado en una campaña anterior?", className="form-label mt-2"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="pday-input",
                            type="number",
                            placeholder="Cantidad de días",
                            min=-1, 
                            max=871, 
                            step=1, 
                            required=True,
                            value=""
                        ),
                    ]),
                ], width=3),
                dbc.Col([
                    html.Label("¿Número de veces que se contactó este cliente antes de la campaña actual?:", className="form-label mt-2"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="previous-input",
                            type="number",
                            placeholder="Cantidad",
                            min=0, 
                            max=275, 
                            step=1, 
                            required=True,
                            value=""
                        ),
                    ]),
                ], width=3)
            ])
        ])
    ], className="mt-4 border-success", style={'borderWidth': '2px', 'borderStyle': 'solid'}),

    # Barra de progreso
    dbc.Progress(id="progress-bar3", value=0, className="mt-3", color="success"),

    # Aviso en forma de warning siempre
    dbc.Alert(
        [
            html.H4("¡Advertencia!", className="alert-heading"),  # Alert heading
            html.P("Por favor, complete todos los campos antes de hacer la predicción. Asegúrese de que todos los valores sean válidos.", className="mb-0"),
            html.P("Si tienes dudas, consulta la documentación o contáctanos.", className="mb-0")
        ],
        color="warning",
        is_open=True, 
        dismissable=True,
    ),
    
    # Aviso porque si no estan bien los inputs
    html.Div(id='warning-message', className="text-danger", style={'marginTop': '10px'}),

    # Boton que corre las predicciones
    html.Div(className="d-grid gap-2", style={'marginTop': '20px'}, children=[
        dbc.Button("Predecir resultado", id="predict-button", className="btn btn-lg btn-primary", n_clicks=0),

    html.Div(id='prediction-output', className="text-success", style={'marginTop': '20px'})

    ])
])
@app.callback(
    Output('age-slider-value', 'children'),
    Output('day-slider-value', 'children'),
    Input('age-slider', 'value'),
    Input('day-slider', 'value')
)
def update_output(age_value, day_value):
    age_return = "Por favor, seleccione una edad."
    if age_value is not None:
        age_return = f'{age_value} años'

    day_return = "Por favor, seleccione un día."
    if day_value is not None:
        day_return = f'Día: {day_value}'

    return age_return, day_return

@app.callback(
    Output('progress-bar1', 'value'),
    Output('progress-bar2', 'value'),
    Output('progress-bar3', 'value'),
    Input('age-slider', 'value'),
    Input('housing-options', 'value'),
    Input('loan-options', 'value'),
    Input('default-options', 'value'),
    Input('balance-input', 'value'),
    Input('job-dropdown', 'value'),
    Input('marital-dropdown', 'value'),
    Input('education-dropdown', 'value'),
    Input('day-slider', 'value'),
    Input('duration-input', 'value'),
    Input('month-dropdown', 'value'),
    Input('contact-dropdown', 'value'),
    Input('poutcome-dropdown', 'value'),
    Input('campain-input', 'value'),
    Input('pday-input', 'value'),
    Input('previous-input', 'value')
)
def update_progress(age_value, housing_value, loan_value, default_value, balance_value, job_value, marital_value, education_value, 
                    day_value, duration_value, month_value, contact_value, poutcome_value, campain_value, pday_value, previous_value):
    total_inputs1 = 8
    filled_inputs1 = sum([
        age_value is not None, 
        housing_value is not None, 
        loan_value is not None, 
        default_value is not None, 
        balance_value != "", 
        job_value is not None, 
        marital_value is not None, 
        education_value is not None
    ])
    progress_percentage1 = (filled_inputs1 / total_inputs1) * 100
    total_inputs2 = 4
    filled_inputs2 = sum([
        day_value is not None,  
        duration_value != "", 
        month_value is not None, 
        contact_value is not None,
    ])
    progress_percentage2 = (filled_inputs2 / total_inputs2) * 100
    total_inputs3 = 4
    filled_inputs3 = sum([
        poutcome_value is not None,  
        campain_value != "", 
        pday_value != "",  
        previous_value != "", 
    ])
    progress_percentage3 = (filled_inputs3 / total_inputs3) * 100
    return progress_percentage1, progress_percentage2, progress_percentage3

@app.callback(
    Output('warning-message', 'children'),
    Output('prediction-output', 'children'),
    Input('age-slider', 'value'),
    Input('housing-options', 'value'),
    Input('loan-options', 'value'),
    Input('default-options', 'value'),
    Input('balance-input', 'value'),
    Input('job-dropdown', 'value'),
    Input('marital-dropdown', 'value'),
    Input('education-dropdown', 'value'),
    Input('day-slider', 'value'),
    Input('duration-input', 'value'),
    Input('month-dropdown', 'value'),
    Input('contact-dropdown', 'value'),
    Input('poutcome-dropdown', 'value'),
    Input('campain-input', 'value'),
    Input('pday-input', 'value'),
    Input('previous-input', 'value'),
    Input('predict-button', 'n_clicks')
)
def on_predict(age_value, housing_value, loan_value, default_value, balance_value, job_value,marital_value, education_value, day_value, duration_value, 
               month_value, contact_value,poutcome_value, campain_value, pday_value, previous_value, n_clicks):
    if n_clicks > 0:  # Only run if the button was clicked
        # Check if all inputs are filled
        inputs_filled = all([
            age_value is not None, 
            housing_value is not None, 
            loan_value is not None, 
            default_value is not None, 
            balance_value != "", 
            job_value is not None, 
            marital_value is not None, 
            education_value is not None,
            day_value is not None,  
            duration_value != "", 
            month_value is not None, 
            contact_value is not None,
            poutcome_value is not None,  
            campain_value != "", 
            pday_value != "",  
            previous_value != ""
        ])
        if inputs_filled:
            # Call your prediction function here
            x = [[float(age_value),
                  float(balance_value),
                  float(day_value),
                  float(duration_value),
                  float(campain_value),
                  float(pday_value),
                  float(previous_value),
                  1 if job_value == 'blue-collar' else 0,
                  1 if job_value == 'entrepreneur' else 0,
                  1 if job_value == 'housemaid' else 0,
                  1 if job_value == 'management' else 0,
                  1 if job_value == 'retired' else 0,
                  1 if job_value == 'self-employed' else 0,
                  1 if job_value == 'services' else 0,
                  1 if job_value == 'student' else 0,
                  1 if job_value == 'technician' else 0,
                  1 if job_value == 'unemployed' else 0,
                  1 if job_value == 'unknown' else 0,
                  1 if marital_value == 'married' else 0,
                  1 if marital_value == 'single' else 0,
                  1 if education_value == 'secondary' else 0,
                  1 if education_value == 'tertiary' else 0,
                  1 if education_value == 'unknown' else 0,
                  1 if default_value == 'yes' else 0,
                  1 if housing_value == 'yes' else 0,
                  1 if loan_value == 'yes' else 0,
                  1 if contact_value == 'telephone' else 0,
                  1 if contact_value == 'unknown' else 0,
                  1 if month_value == 'aug' else 0,
                  1 if month_value == 'dec' else 0,
                  1 if month_value == 'feb' else 0,
                  1 if month_value == 'jan' else 0,
                  1 if month_value == 'jul' else 0,
                  1 if month_value == 'jun' else 0,
                  1 if month_value == 'mar' else 0,
                  1 if month_value == 'may' else 0,
                  1 if month_value == 'nov' else 0,
                  1 if month_value == 'oct' else 0,
                  1 if month_value == 'sep' else 0,
                  1 if poutcome_value == 'other' else 0,
                  1 if poutcome_value == 'success' else 0,+
                  1 if poutcome_value == 'unknown' else 0]]
            prediction_result = model.predict(x) 
            prob_yes = prediction_result[0][0] 
            prob_no = 1 - prob_yes 

            prob_no_percentage = "{:.2f}%".format(prob_no * 100)
            prob_yes_percentage = "{:.2f}%".format(prob_yes * 100)

            prediction_message = f"Probabilidad de 'No': {prob_no_percentage}, Probabilidad de 'Sí': {prob_yes_percentage}"

            return None, prediction_message
        else:
            return dbc.Alert(
                html.Div([
                    html.H4("¡Error!", className="alert-heading"),
                    html.P("Por favor, ¡complete todos los campos! Esto lo puede hacer asegurandose que las 3 barras esten completas", className="mb-0"),  # Custom warning message
                ]),    
                color="danger", 
                is_open=True,
                dismissable=True,
                duration=7000, 
            ) 
    
    return dash.no_update  # If button has not been clicked, do nothing

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Inicio", href="/home", active=True)),
            dbc.NavItem(dbc.NavLink("Exploración de data", href="/data-exploration")),
            dbc.NavItem(dbc.NavLink("Predicciones", href="/predictions")),
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
    html.Div(id='page-content')
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
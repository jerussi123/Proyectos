"""
# git checkout nombre-de-la-rama
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import math  

# Parámetros del modelo ya que el csv no funciono
coef_dict = {
    'const': 457.5830587435722,
    'Humidity(%)': -13.746610344494725,
    'Wind speed (m/s)': -1.0105730364312602,
    'Dew point temperature(C)': 26.500800279931934,
    'Solar Radiation (MJ/m2)': 78.57876852424992,
    'Rainfall(mm)': -50.6572919853053,
    'Snowfall (cm)': 32.54115898329849,
    'Hour_1': -103.8715420647231,
    'Hour_2': -195.64531974440126,
    'Hour_3': -274.27726608361013,
    'Hour_4': -328.56054267249215,
    'Hour_5': -314.6785572847332,
    'Hour_6': -159.35239331390378,
    'Hour_7': 139.2977104870937,
    'Hour_8': 485.06174202013096,
    'Hour_9': 27.215013925288183,
    'Hour_10': -216.19730239172168,
    'Hour_11': -221.14119942724275,
    'Hour_12': -197.3113476599997,
    'Hour_13': -201.70267090969642,
    'Hour_14': -184.18068015027146,
    'Hour_15': -101.25575456584173,
    'Hour_16': 44.8608077645748,
    'Hour_17': 285.7410423185654,
    'Hour_18': 762.4644288277303,
    'Hour_19': 514.2680639950346,
    'Hour_20': 426.49149959743204,
    'Hour_21': 424.1270206306511,
    'Hour_22': 331.2606566444371,
    'Hour_23': 103.41940842171543,
    'Seasons_Spring': -147.7990803219568,
    'Seasons_Summer': -186.000275336692,
    'Seasons_Winter': -343.96613252204344,
    'Holiday_No Holiday': 130.45616033852585,
    'Functioning Day_Yes': 938.2224798204375
}


app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("Análisis de Rentabilidad del Modelo de Demanda en Bicicletas Compartidas"),

    # Parámetros usuario 
    html.Div([
        html.H3("Parámetros para Predecir Demanda"),
        html.Div([
            html.Label('Punto de rocío (°C)'),
            dcc.Input(id='temp-input', type='number', value=20, placeholder="Ingrese la temperatura en °C"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Día festivo'),
            dcc.RadioItems(id='festivo-radio', options=[{'label': 'Sí', 'value': True}, {'label': 'No', 'value': False}], value=False),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label('Día de Funcionamiento'),
            dcc.RadioItems(id='funcionamiento-radio', options=[
                {'label': 'Sí', 'value': True},
                {'label': 'No', 'value': False}
            ], value=True),  
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Estación del año'),
            dcc.Dropdown(id='estacion-dropdown', options=[
                {'label': 'Primavera', 'value': 'Spring'},
                {'label': 'Verano', 'value': 'Summer'},
                {'label': 'Otoño', 'value': 'Autumn'},
                {'label': 'Invierno', 'value': 'Winter'}
            ], value='Spring'),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    
    html.Div([
        html.Div([
            html.Label('Humedad (%)'),
            dcc.Input(id='humidity-input', type='number', value=60, placeholder="Ingrese la humedad (%)"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Velocidad del viento (m/s)'),
            dcc.Input(id='wind-speed-input', type='number', value=3, placeholder="Ingrese la velocidad del viento (m/s)"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Radiación solar (MJ/m2)'),
            dcc.Input(id='solar-radiation-input', type='number', value=10, placeholder="Ingrese la radiación solar"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Nivel de Precipitación (mm)'),
            dcc.Input(id='rainfall-input', type='number', value=0, placeholder="Ingrese la precipitación (mm)"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label('Nivel de Nieve (cm)'),
            dcc.Input(id='snowfall-input', type='number', value=0, placeholder="Ingrese la cantidad de nieve (cm)"),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    # Parámetros de ingresos y costos
    html.Div([
        html.H3("Análisis financiero"),
        html.Div([
            html.Div([
                html.Label('Precio de renta por bicicleta (COP)'),
                dcc.Input(id='precio-renta-input', type='number', value=10, placeholder="Ingrese el precio de renta"),
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                html.Label('Costo de operación por bicicleta (COP)'),
                dcc.Input(id='costo-operacion-input', type='number', value=8, placeholder="Ingrese el costo de operación"),
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                html.Label('Costo de mantenimiento por bicicleta (COP)'),
                dcc.Input(id='costo-mantenimiento-input', type='number', value=5, placeholder="Ingrese el costo de mantenimiento"),
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
    ], style={'border': '1px solid #ddd', 'padding': '20px', 'margin-bottom': '20px'}),

    # Idea Boton
    html.Div([
        html.Button('Predecir Demanda', id='validar-btn', n_clicks=0)
    ], style={'padding': '20px', 'textAlign': 'center'}),

  
    dcc.Graph(id='grafico-prediccion-demandas'),
    dcc.Graph(id='grafico-ingresos-egresos'),
    dcc.Graph(id='grafico-rentabilidad'),

  
    html.Div(id='total-demanda', style={'padding': '10px', 'fontSize': '16px', 'fontWeight': 'bold'})
])

# Modelo de predicción de demanda
def predecir_demanda_con_csv(hour, temp, festivo, funcionamiento, estacion, humidity, wind_speed, solar_radiation, rainfall, snowfall):
   
    valores = {
        'Hour': hour,
        'Humidity(%)': humidity,
        'Wind speed (m/s)': wind_speed,
        'Dew point temperature(C)': temp,
        'Solar Radiation (MJ/m2)': solar_radiation,
        'Rainfall(mm)': rainfall,
        'Snowfall (cm)': snowfall,
        'Holiday_No Holiday': not festivo,
        'Seasons_Spring': 1 if estacion == 'Spring' else 0,
        'Seasons_Summer': 1 if estacion == 'Summer' else 0,
        'Seasons_Winter': 1 if estacion == 'Winter' else 0,
        'Seasons_Autumn': 1 if estacion == 'Autumn' else 0,
        'Functioning Day_Yes': 1 if funcionamiento else 0
    }

    
    prediccion = coef_dict['const']
    
    # Aplicar modelo para cada beta asociado a la hora de analisis del modelo
    if f'Hour_{hour+1}' in coef_dict:
        prediccion += coef_dict[f'Hour_{hour+1}']

    
    for var, coef in coef_dict.items():
        if var not in [f'Hour_{hour+1}', 'const']:  # Excluir la constante y la hora
            prediccion += coef * valores.get(var, 0)

    # No valores negativos ya que hay configuraciones que por los parametros dan demanda negativa en algunas horas
    return max(0, math.floor(prediccion))  

# Callback para las graficas
@app.callback(
    [Output('grafico-prediccion-demandas', 'figure'),
     Output('grafico-ingresos-egresos', 'figure'),
     Output('grafico-rentabilidad', 'figure'),
     Output('total-demanda', 'children')],
    [Input('validar-btn', 'n_clicks')],
    [State('temp-input', 'value'),
     State('humidity-input', 'value'),
     State('wind-speed-input', 'value'),
     State('solar-radiation-input', 'value'),
     State('rainfall-input', 'value'),
     State('snowfall-input', 'value'),
     State('festivo-radio', 'value'),
     State('funcionamiento-radio', 'value'),
     State('estacion-dropdown', 'value'),
     State('precio-renta-input', 'value'),
     State('costo-operacion-input', 'value'),
     State('costo-mantenimiento-input', 'value')]
)
def validar_modelo(n_clicks, temp, humidity, wind_speed, solar_radiation, rainfall, snowfall, festivo, funcionamiento, estacion, precio_renta, costo_operacion, costo_mantenimiento):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    
    horas = list(range(0, 23)) 
    predicciones = [predecir_demanda_con_csv(hora, temp, festivo, funcionamiento, estacion, humidity, wind_speed, solar_radiation, rainfall, snowfall) for hora in horas]

    # demanda total
    total_demanda = math.floor(sum(predicciones))

    # ingresos y egresos
    ingresos = total_demanda * precio_renta
    costos = total_demanda * (costo_operacion + costo_mantenimiento)

    # Garfica de la demandaa
    grafico_prediccion = px.bar(
        x=horas,
        y=predicciones,
        title='Predicción de la Demanda de Bicicletas por Hora',
        labels={'x': 'Hora del día', 'y': 'Demanda de Bicicletas'}
    )
# grafica de ingresos
    valores = [ingresos, costos]
    etiquetas = ['Ingresos', 'Costos']
    grafico_ingresos_egresos = px.pie(values=valores, names=etiquetas, title='Ingresos vs Costos')
    grafico_ingresos_egresos.update_traces(textinfo='percent+label')

    
    rentabilidad = ingresos - costos
    rentabilidad_porcentaje = (rentabilidad / ingresos) * 100 if ingresos > 0 else 0

    # Idea grafico de rentabilidad
    grafico_rentabilidad = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rentabilidad_porcentaje,
        title={'text': "Rentabilidad (%)"},
        gauge={'axis': {'range': [-100, 100]},
               'bar': {'color': "darkblue"},
               'steps': [{'range': [0, 100], 'color': "lightgreen"},
                         {'range': [-100, 0], 'color': "lightcoral"}]},
    ))

    total_texto = f"Demanda total de bicicletas durante el día: {total_demanda}"

    return grafico_prediccion, grafico_ingresos_egresos, grafico_rentabilidad, total_texto

if __name__ == '__main__':
    app.run_server(debug=True)

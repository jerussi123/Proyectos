"""
# git checkout nombre-de-la-rama
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import math  

# Coeficientes del modelo de regresión lineal (manual)
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
from dash import html, dcc
import dash_bootstrap_components as dbc
from WebApp.Components import generate_upload

forecast_probability = html.Div(
    [
        html.H1("抑郁症概率预测", className='mb-4'),
    ],
    className='mx-5 my-5'
)

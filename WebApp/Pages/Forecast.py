from dash import html, dcc
import dash_bootstrap_components as dbc
from WebApp.Components import generate_upload

forecast = html.Div(
    [
        html.H1("抑郁症预测", className='mb-4'),
        generate_upload('upload-raw'),
    ],
    className='mx-5 my-5'
)

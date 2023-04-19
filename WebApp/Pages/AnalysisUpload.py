from dash import html, dcc
import dash_bootstrap_components as dbc
from WebApp.Components import generate_upload

analysis_upload = html.Div(
    [
        html.H1("数据上传", className='mb-4'),
        html.H2("上传手环数据"),
        html.P("必要文件为：continuousrri.csv；"
               "其他支持上传文件包括：continuousbloodoxygensaturation.csv、"
               "continuousheartrate.csv、dailyworkoutdetail.csv"),
        generate_upload('upload-raw'),
        dcc.Loading(),


    ],
    className='mx-5 my-5'
)

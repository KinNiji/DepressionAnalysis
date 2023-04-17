from dash import html, dcc
import dash_bootstrap_components as dbc


def generate_toast(_id, header='提示', icon='primary'):
    return dbc.Toast(
        id=_id,
        header=header,
        icon=icon,
        duration=3000,
        is_open=False,
        dismissable=True,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    )


def generate_upload(_id):
    return dcc.Upload(
        id=_id,
        children=html.Div([
            '将文件拖拽至此',
            html.A('或选择文件上传')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    )

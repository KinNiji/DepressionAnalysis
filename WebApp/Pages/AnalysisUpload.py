from dash import dash_table
from dash import html, dcc
import dash_bootstrap_components as dbc

analysis_upload = html.Div(
    [
        dbc.Row([
            dbc.Col(
                children=[
                    html.H2("数据上传"),
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                children=[
                                    html.P(),
                                    html.P("请通过华为提供的sdk下载您的项目的数据，"
                                           "找到持续心室搏动间隔、持续血氧饱和度、"
                                           "持续心率、详细日常运动这四项数据所对应的文件，"
                                           "修改至以下的对应名称并一次性上传四个数据文件："),
                                    html.P("continuousrri.csv (RRI)", style={"color": '#78c2ad'}),
                                    html.P("continuousbloodoxygensaturation.csv (血氧)", style={"color": '#78c2ad'}),
                                    html.P("continuousheartrate.csv (心率)", style={"color": '#78c2ad'}),
                                    html.P("dailyworkoutdetail.csv (运动)", style={"color": '#78c2ad'}),
                                    dcc.Upload(
                                        id='upload',
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
                                            'margin': '0 0 10px'
                                        },
                                        multiple=True
                                    ),
                                    dbc.Spinner(
                                        html.Div(id='upload-result'),
                                        type="grow",
                                        color="primary",
                                        spinner_style={
                                            "width": "3rem",
                                            "height": "3rem",
                                            'margin': '10px 0 10px'
                                        }
                                    ),
                                ],
                                label="文件上传"
                            ),
                            dbc.Tab(
                                children=[
                                    html.P(),
                                    html.Div(
                                        [
                                            html.Div('查询上传记录后，单击某条记录以查看详情'),
                                            dbc.Button(
                                                id='upload-record-search',
                                                children="查询"
                                            ),
                                        ],
                                        className="my-2 d-flex align-items-center justify-content-md-between",
                                    ),
                                    dash_table.DataTable(
                                        id='upload-record-table',
                                        fixed_rows={'headers': True},
                                        style_table={'overflowX': 'auto'},
                                        page_size=10
                                    ),

                                ],
                                label="上传记录"
                            )
                        ]
                    )
                ],
                width=4
            ),
            dbc.Col(
                children=[
                    html.H2("数据处理"),
                    dash_table.DataTable(
                        id='upload-detail-table',
                        fixed_rows={'headers': True},
                        style_table={'overflowX': 'auto'},
                    ),
                    html.Div(
                        [
                            html.Div('选中左侧某条上传记录后，单击右侧按钮可重采样该次上传中的所有数据'),
                            dbc.Button(
                                id='upload-detail-resample',
                                children="重采样数据",
                                disabled=True
                            ),
                        ],
                        className="my-2 d-flex align-items-center justify-content-md-between",
                    ),
                    dbc.Spinner(
                        html.Div(id='resample-result'),
                        type="grow",
                        color="primary",
                        spinner_style={
                            "width": "3rem",
                            "height": "3rem",
                            'margin': '10px 0 10px'
                        }
                    ),
                ],
                width=8
            ),
        ]),
    ],
    className='mx-5 my-5'
)

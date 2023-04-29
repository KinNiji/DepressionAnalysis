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
                                    dbc.Spinner(html.Div(id='upload-result'), type="grow"),
                                ],
                                label="文件上传"
                            ),
                            dbc.Tab(
                                children=[

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
                    html.H2("数据操作"),
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                children=[

                                ],
                                label="有效信息抽取"
                            ),
                            dbc.Tab(
                                children=[

                                ],
                                label="数据预处理"
                            )
                        ]
                    )
                ],
                width=8
            ),
        ]),
    ],
    className='mx-5 my-5'
)

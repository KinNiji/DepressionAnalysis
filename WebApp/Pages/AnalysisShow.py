from dash import html, dcc
import dash_bootstrap_components as dbc

from datetime import date

import Config
import Utils

BEGIN_TIME = Utils.timestr2time(Config.BEGIN_TIME_STR)
END_TIME = Utils.timestr2time(Config.END_TIME_STR)


def generate_timepicker(_id):
    return dcc.DatePickerSingle(
        id=_id,
        min_date_allowed=date(BEGIN_TIME.year, BEGIN_TIME.month, BEGIN_TIME.day),
        max_date_allowed=date(END_TIME.year, END_TIME.month, END_TIME.day),
        date=date(BEGIN_TIME.year, BEGIN_TIME.month, BEGIN_TIME.day)
    )


def generate_timepicker_range(_id):
    return dcc.DatePickerRange(
        id=_id,
        min_date_allowed=date(BEGIN_TIME.year, BEGIN_TIME.month, BEGIN_TIME.day),
        max_date_allowed=date(END_TIME.year, END_TIME.month, END_TIME.day),
        start_date=date(BEGIN_TIME.year, BEGIN_TIME.month, BEGIN_TIME.day),
        end_date=date(END_TIME.year, END_TIME.month, END_TIME.day)
    )


analysis_show = html.Div(
    [
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.P("选择展示的人"),
                                dcc.Dropdown(
                                    id='figure-sequence-pid',
                                    style={'height': '48px'},
                                    optionHeight=50
                                ),
                            ], width=6),
                            dbc.Col([
                                html.P("选择展示的日期"),
                                generate_timepicker('figure-sequence-date'),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.P("选择展示的文件类型"),
                                dcc.Dropdown(
                                    id='figure-sequence-filetype',
                                    options=Config.OPTIONS['file_type'],
                                    value=Config.OPTIONS['file_type'][0]['value']
                                ),
                            ], width=6),
                            dbc.Col([
                                html.P("选择展示的文件"),
                                dcc.Dropdown(id='figure-extracted-filename'),
                            ], width=6),
                        ]),
                        dbc.Spinner(
                            dcc.Graph(id='figure-sequence-graph'),
                            type="grow",
                            color="primary",
                            spinner_style={
                                "width": "3rem",
                                "height": "3rem",
                                'margin': '10px 0 10px'
                            }
                        ),
                    ],
                    title="序列数据",
                ),
                dbc.AccordionItem(
                    [
                        html.P("选择统计方式"),
                        dcc.Dropdown(
                            id='figure-statistics-counting',
                            options=Config.OPTIONS['counting'],
                            value=Config.OPTIONS['counting'][0]['value']
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.P("选择展示的人"),
                                dcc.Dropdown(
                                    id='figure-statistics-pid',
                                    style={'height': '48px'},
                                    optionHeight=50
                                ),
                            ], width=6),
                            dbc.Col([
                                html.P("选择展示的日期"),
                                generate_timepicker_range('figure-statistics-date'),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.P("选择展示的文件类型"),
                                dcc.Dropdown(
                                    id='figure-statistics-filetype',
                                    options=Config.OPTIONS['file_type'],
                                    value=Config.OPTIONS['file_type'][0]['value']
                                ),
                            ], width=4),
                            dbc.Col([
                                html.P("选择展示的文件"),
                                dcc.Dropdown(id='figure-statistics-filename'),
                            ], width=4),
                            dbc.Col([
                                html.P("选择展示的列"),
                                dcc.Dropdown(id='figure-statistics-col'),
                            ], width=4),
                        ]),
                        html.P('选择聚合方式或选择展示图表'),
                        dcc.Dropdown(id='figure-statistics-mode'),
                        dbc.Spinner(
                            dcc.Graph(id='figure-statistics-graph'),
                            type="grow",
                            color="primary",
                            spinner_style={
                                "width": "3rem",
                                "height": "3rem",
                                'margin': '10px 0 10px'
                            }
                        ),
                    ],
                    title="统计数据",
                )
            ],
            id="analysis-show-accordion",
            always_open=True,
        ),
    ],
    className='analysis-show-container mx-5 my-5'
)

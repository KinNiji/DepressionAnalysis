from dash import html, dcc
import dash_bootstrap_components as dbc

login = html.Div(
    className="login-container-outer",
    children=html.Div(
        className="login-container",
        id="login-container",
        children=[
            html.Div(
                className="form-container sign-in-container",
                children=[
                    html.Div(
                        children=[
                            html.H1("登录"),
                            dbc.Input(
                                id='sign-in-email',
                                type='email',
                                placeholder='example@host.com'
                            ),
                            dbc.Input(
                                id='sign-in-password',
                                type='password',
                                placeholder='请输入密码'
                            ),
                            dbc.Button('登录', id='sign-in-button'),
                            html.A("忘记密码？", href=""),
                        ]
                    )
                ]
            ),
            html.Div(
                className="form-container sign-up-container",
                children=[
                    html.Div(
                        children=[
                            html.H1("注册"),
                            dbc.Input(
                                id='sign-up-user-name',
                                type='text',
                                placeholder='请输入用户名'
                            ),
                            dbc.Input(
                                id='sign-up-email',
                                type='email',
                                placeholder='example@host.com'
                            ),
                            dbc.Input(
                                id='sign-up-password',
                                type='password',
                                placeholder='请输入密码'
                            ),
                            dbc.Input(
                                id='sign-up-password-confirm',
                                type='password',
                                placeholder='请二次输入确认密码'
                            ),
                            dbc.Button('注册', id='sign-up-button'),
                        ]
                    )
                ]
            ),
            html.Div(
                className="overlay-container",
                children=[
                    html.Div(
                        className="overlay",
                        children=[
                            html.Div(
                                className="overlay-panel overlay-left",
                                children=[
                                    html.H1("已有账号！"),
                                    html.P("点击此处输入账号密码登录系统"),
                                    html.Button(className="ghost", id="sign-in", children="登录")
                                ]
                            ),
                            html.Div(
                                className="overlay-panel overlay-right",
                                children=[
                                    html.H1("没有账号？"),
                                    html.P("点击此处输入基本信息注册账号"),
                                    html.Button(className="ghost", id="sign-up", children="注册")
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )
)

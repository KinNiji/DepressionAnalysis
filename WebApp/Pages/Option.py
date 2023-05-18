from dash import html, dcc
import dash_bootstrap_components as dbc

import Utils


def generate_option(user_info):
    return html.Div(
        [
            html.H1("配置", className='mb-4'),
            html.Div([
                html.H2(f"欢迎您，{'管理员' if user_info['is_admin'] else '用户'} {user_info['user_name']}"),
                html.P(f"上次登录：{Utils.timestamp2timestr(user_info['last_login'])}")
            ])
        ],
        className='mx-5 my-5'
    )

import datetime
import time

import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import Utils
from WebApp.Pages.Index import generate_index
from WebApp.Logic.User import User
from WebApp.Pages.Login import login
from WebApp.Pages.OverviewData import overview_data
from WebApp.Pages.OverviewModel import overview_model
from WebApp.Pages.AnalysisUpload import analysis_upload
from WebApp.Pages.AnalysisShow import analysis_show
from WebApp.Pages.ForecastScale import forecast_scale
from WebApp.Pages.ForecastProbability import forecast_probability
from WebApp.Pages.Option import generate_option
from WebApp.Pages.PathError import path_error
from WebApp.Components import generate_toast

user = User()

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavbarToggler(id="navbar-toggle", n_clicks=0),
        dbc.Collapse(
            id="navbar-collapse",
            children=[
                dbc.NavItem(dbc.NavLink("首页", href="/index")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("数据", href="/overview/data"),
                        dbc.DropdownMenuItem("模型", href="/overview/model"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="概览",
                ),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("数据上传", href="/analysis/upload"),
                        dbc.DropdownMenuItem("可视化分析", href="/analysis/show"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="分析",
                ),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("量表填写", href="/forecast/scale"),
                        dbc.DropdownMenuItem("抑郁症概率", href="/forecast/probability"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="预测",
                ),
                dbc.NavItem(id='navbar-login', children=dbc.NavLink("登录", href="/login")),
            ],
            is_open=False,
            navbar=True,
        ),
    ],
    brand="抑郁症行为数据分析系统",
    brand_href="index",
    color="primary",
    dark=True
)

app = dash.Dash(
    __name__,
    title="",
    update_title=None,
    external_stylesheets=[
        dbc.themes.MINTY,
        dbc.icons.BOOTSTRAP
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    dcc.Store(id='login-history', storage_type='local'),
    dcc.Store(id='user-info', storage_type='session'),
    navbar,
    # dcc.Geolocation(id="geolocation"),
    dcc.Location(id='location', refresh=True),
    html.Div(id='content'),
    generate_toast('sign-in-toast'),
    generate_toast('sign-up-toast'),
])


# region 回调函数

# url路由
@app.callback(
    Output('content', "children"),
    Input("location", "pathname"),
    State("user-info", "data")
)
def url_route(pathname, user_info):
    print('路由切换', pathname, user_info)
    path_list = pathname.split('/')[1:]

    if user_info:
        if path_list[0] == "":
            return generate_index(user_info)
        elif path_list[0] == "index":
            return generate_index(user_info)
        elif path_list[0] == "login":
            return login
        elif path_list[0] == "overview":
            if len(path_list) == 2:
                if path_list[1] == "data":
                    return overview_data
                elif path_list[1] == "model":
                    return overview_model
        elif path_list[0] == "analysis":
            if len(path_list) == 2:
                if path_list[1] == "upload":
                    return analysis_upload
                elif path_list[1] == "show":
                    return analysis_show
        elif path_list[0] == "forecast":
            if len(path_list) == 2:
                if path_list[1] == "scale":
                    return forecast_scale
                elif path_list[1] == "probability":
                    return forecast_probability
        elif path_list[0] == "option":
            return generate_option(user_info)
    else:
        if path_list[0] == "":
            return generate_index(user_info)
        elif path_list[0] == "index":
            return generate_index(user_info)
        elif path_list[0] in ["login", "overview", "analysis", "forecast", "option"]:
            return login
    return path_error


# 导航栏移动端折叠
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggle", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# 登录界面切换注册功能
@app.callback(
    Output('login-container', "className"),
    Input("sign-up", "n_clicks"),
    Input("sign-in", "n_clicks"),
    State("login-container", "className")
)
def _(sign_up, sign_in, class_name):
    if sign_up or sign_in:
        button_clicked = ctx.triggered_id
        if button_clicked == "sign-up":
            return class_name + " right-panel-active"
        else:
            return class_name.split(" ")[0]
    else:
        raise PreventUpdate


# 用户注册
@app.callback(
    [Output('sign-up-toast', 'is_open'),
     Output('sign-up-toast', 'children'),
     Output('sign-up-toast', 'icon')],
    [Input('sign-up-button', 'n_clicks')],
    [State('sign-up-user-name', 'value'),
     State('sign-up-email', 'value'),
     State('sign-up-password', 'value'),
     State('sign-up-password-confirm', 'value')],
    prevent_initial_call=True
)
def _(n, user_name, email, password, password_confirm):
    print('用户注册', n, user_name, email, password, password_confirm)
    if n:
        if not user_name or not email or not password or not password_confirm:
            return True, '请填写注册必要信息！', 'danger'
        if password != password_confirm:
            return True, '两次输入的密码不一致！', 'danger'
        flag = user.user_create(user_name, email, password)
        if flag:
            return True, '注册成功，请切换到登录页面进行登录！', 'primary'
        else:
            return True, '注册失败，该邮箱已经注册账号！', 'danger'
    else:
        raise PreventUpdate


# 用户登录
@app.callback(
    [Output('user-info', 'data'),
     Output('login-history', 'data')],
    [Input('sign-in-button', 'n_clicks')],
    [State('sign-in-email', 'value'),
     State('sign-in-password', 'value'),
     State('login-history', 'data')],
    prevent_initial_call=True
)
def _(n, email, password, login_history):
    print('用户登录', n, email, password, login_history)
    if n:
        flag = user.login_check(email, password)
        if flag:
            user_info = {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin,
                "last_login": login_history["last_login"] if login_history else datetime.datetime.now().timestamp()
            }
            login_history = user_info.copy()
            login_history['last_login'] = datetime.datetime.now().timestamp()
            return user_info, login_history
        else:
            return {}, login_history
    else:
        raise PreventUpdate


# 用户信息更新
@app.callback(
    [Output('navbar-login', 'children'),
     Output('location', 'pathname'),
     Output('sign-in-toast', 'is_open'),
     Output('sign-in-toast', 'children'),
     Output('sign-in-toast', 'icon')],
    Input('user-info', 'data'),
    prevent_initial_call=True
)
def _(user_info):
    print('用户登录后', user_info)
    if user_info:
        return dbc.NavLink(user_info['user_name'], href="/option"), '/index', True, '登陆成功，欢迎使用！', 'primary'
    elif user_info == {}:
        return dbc.NavLink("登录", href="/login"), '/login', True, '登陆失败，请检查用户名和密码！', 'danger'
    else:
        raise PreventUpdate


# endregion


if __name__ == "__main__":
    app.run_server(debug=False)

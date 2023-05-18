import base64
import datetime
import io
import json
import os

import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

import Config
import Utils
from WebApp.Pages.Index import generate_index
from WebApp.Logic.User import User
from WebApp.Logic.DataManager import DataManager
from WebApp.Logic.DataShow import DataShow
from WebApp.Pages.Login import login
from WebApp.Pages.AnalysisUpload import analysis_upload
from WebApp.Pages.AnalysisShow import analysis_show
from WebApp.Pages.ForecastProbability import forecast_probability
from WebApp.Pages.Option import generate_option
from WebApp.Pages.PathError import path_error
from WebApp.Components import generate_toast

user = User()
data_manager = DataManager()
data_show = DataShow()

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavbarToggler(id="navbar-toggle", n_clicks=0),
        dbc.Collapse(
            id="navbar-collapse",
            children=[
                dbc.NavItem(dbc.NavLink("首页", href="/index")),
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

blank_figure = go.Figure().update_layout(
    plot_bgcolor='white',
    yaxis=dict(showgrid=True, gridcolor='lightgray')
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
        elif path_list[0] == "analysis":
            if len(path_list) == 2:
                if path_list[1] == "upload":
                    return analysis_upload
                elif path_list[1] == "show":
                    return analysis_show
        elif path_list[0] == "forecast":
            if len(path_list) == 2:
                if path_list[1] == "probability":
                    return forecast_probability
        elif path_list[0] == "option":
            return generate_option(user_info)
    else:
        if path_list[0] == "":
            return generate_index(user_info)
        elif path_list[0] == "index":
            return generate_index(user_info)
        elif path_list[0] in ["login", "analysis", "forecast", "option"]:
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
    State('location', 'pathname'),
    prevent_initial_call=True
)
def _(user_info, pathname):
    print('用户登录后', user_info, pathname)
    if user_info:
        if pathname == '/login':
            return dbc.NavLink(user_info['user_name'], href="/option"), '/index', True, '登陆成功，欢迎使用！', 'primary'
        else:
            return dbc.NavLink(user_info['user_name'], href="/option"), pathname, False, '登陆成功，欢迎使用！', 'primary'
    elif user_info == {}:
        return dbc.NavLink("登录", href="/login"), '/login', True, '登陆失败，请检查用户名和密码！', 'danger'
    else:
        raise PreventUpdate


# 上传文件
@app.callback(
    Output('upload-result', 'children'),
    Input('upload', 'contents'),
    State('upload', 'filename'),
    State('user-info', 'data'),
    prevent_initial_call=True
)
def _(list_of_contents, list_of_names, user_info):
    print('文件上传', list_of_names)
    if list_of_names is not None:
        if 'continuousrri.csv' in list_of_names \
                and 'continuousbloodoxygensaturation.csv' in list_of_names \
                and 'continuousheartrate.csv' in list_of_names \
                and 'dailyworkoutdetail.csv' in list_of_names:
            current_time = int(datetime.datetime.now().timestamp() * 1000)
            data_manager.insert_upload(current_time, user_info['user_id'])
            os.makedirs(f"{Config.APP_DATA_FILE_PATH}/{current_time}/raw", exist_ok=True)
            os.makedirs(f"{Config.APP_DATA_FILE_PATH}/{current_time}/extracted", exist_ok=True)
            for contents, file_name in zip(list_of_contents, list_of_names):
                content_type, content_string = contents.split(',')
                content_base64 = base64.b64decode(content_string)
                file_name = file_name.split('.')[0]
                try:
                    df = pd.read_csv(io.StringIO(content_base64.decode('utf-8')), dtype=str)
                    df.to_csv(
                        f"{Config.APP_DATA_FILE_PATH}/{current_time}/raw/{file_name}.csv",
                        encoding="utf-8", index=False)
                    data_manager.extract_raw(file_name, current_time, user_info['user_id'], df=df)
                except Exception as err:
                    return dbc.Alert(f"上传失败：{err}", color="secondary")

            return dbc.Alert("上传成功，请在上传记录中查看详细信息！", color="primary")
        else:
            return dbc.Alert("文件缺失，请重新选择上传！", color="secondary")
    else:
        return dbc.Alert("未选择文件或文件类型不符！", color="secondary")


# 查询上传记录
@app.callback(
    Output('upload-record-table', 'data'),
    Output('upload-record-table', 'columns'),
    Input('upload-record-search', 'n_clicks'),
    prevent_initial_call=True
)
def _(n):
    if n:
        df = data_manager.select_upload_all()
        return df.to_dict('records'), [{'id': c, 'name': c} for c in df.columns]

    else:
        raise PreventUpdate


# 上传记录详情
@app.callback(
    Output('upload-detail-table', 'data'),
    Output('upload-detail-table', 'columns'),
    Output('upload-detail-resample', 'disabled'),
    Input('upload-record-table', 'active_cell'),
    State('upload-record-table', 'data'),
    prevent_initial_call=True
)
def _(active_cell, data):
    if active_cell:
        data = pd.DataFrame(data)
        df = pd.DataFrame(json.loads(data.iloc[active_cell['row']]['upload_info']))
        return df.to_dict('records'), [{'id': c, 'name': c} for c in df.columns], False
    else:
        raise PreventUpdate


# 重采样数据
@app.callback(
    Output('resample-result', 'children'),
    Input('upload-detail-resample', 'n_clicks'),
    State('upload-record-table', 'active_cell'),
    State('upload-record-table', 'data'),
    prevent_initial_call=True
)
def _(n, active_cell, data):
    if n:
        print("重采样")
        data = pd.DataFrame(data)
        upload_time = data.iloc[active_cell['row']]['upload_time']
        upload_user_id = data.iloc[active_cell['row']]['upload_user_id']
        upload_info = json.loads(data.iloc[active_cell['row']]['upload_info'])
        os.makedirs(f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/minute", exist_ok=True)
        os.makedirs(f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/continuousrri", exist_ok=True)
        try:
            data_manager.resample_extracted(upload_time, upload_user_id, upload_info)
        except Exception as err:
            return dbc.Alert(f"重采样失败：{err}", color="secondary")
        return dbc.Alert("重采样成功！", color="primary")
    else:
        raise PreventUpdate


# 加载pid列表
@app.callback(
    Output('figure-sequence-pid', 'options'),
    Output('figure-statistics-pid', 'options'),
    Input('analysis-show-accordion', 'active_item'),
)
def _(item):
    upload_info_all = data_show.select_pid_all()
    options_sequence = []
    options_statistics = []
    for pid, upload_info in upload_info_all.items():
        options_sequence.append({
            'label': f'pid: {pid} '
                     f'上传时间: {Utils.timestamp2timestr(upload_info["upload_time"])} '
                     f'外部编号: {upload_info["external_id"]}',
            'value': pid
        })
        options_statistics.append({
            'label': f'pid: {pid}',
            'value': pid
        })
    return options_sequence, options_statistics


# 加载文件相关下拉框
@app.callback(
    Output('figure-extracted-filename', 'options'),
    Output('figure-extracted-filename', 'value'),
    Input('figure-sequence-filetype', 'value'),
)
def _(value):
    return Config.OPTIONS[value], Config.OPTIONS[value][0]['value']


@app.callback(
    Output('figure-statistics-filename', 'options'),
    Output('figure-statistics-filename', 'value'),
    Input('figure-statistics-filetype', 'value'),
)
def _(value):
    return Config.OPTIONS[value], Config.OPTIONS[value][0]['value']


@app.callback(
    Output('figure-statistics-col', 'options'),
    Output('figure-statistics-col', 'value'),
    Input('figure-statistics-filename', 'value'),
)
def _(value):
    return Config.OPTIONS[value], Config.OPTIONS[value][0]['value']


@app.callback(
    Output('figure-statistics-mode', 'options'),
    Output('figure-statistics-mode', 'value'),
    Output('figure-statistics-pid', 'multi'),
    Input('figure-statistics-counting', 'value'),
)
def _(value):
    return Config.OPTIONS[value], Config.OPTIONS[value][0]['value'], True if value == 'multiple' else False


# 绘图
@app.callback(
    Output('figure-sequence-graph', 'figure'),
    Input('figure-sequence-pid', 'value'),
    Input('figure-sequence-date', 'date'),
    Input('figure-extracted-filename', 'value'),
    State('figure-sequence-filetype', 'value'),
    prevent_initial_call=True
)
def _(pid, date, file_name, file_type):
    if pid and date and file_name and file_type:
        date = Utils.timestr2time(f'{date} 00:00:00')
        if file_type == 'extracted_file':
            return data_show.generate_figure_extracted(pid, date, file_name)
        elif file_type == 'resampled_file':
            return data_show.generate_figure_resampled(pid, date, file_name)
    else:
        return blank_figure


@app.callback(
    Output('figure-statistics-graph', 'figure'),
    Input('figure-statistics-pid', 'value'),
    Input('figure-statistics-date', 'start_date'),
    Input('figure-statistics-date', 'end_date'),
    Input('figure-statistics-col', 'value'),
    Input('figure-statistics-mode', 'value'),
    State('figure-statistics-counting', 'value'),
    State('figure-statistics-filetype', 'value'),
    State('figure-statistics-filename', 'value'),
    prevent_initial_call=True
)
def _(pid, date_from, date_to, col_name, mode, counting, file_type, file_name):
    if pid and date_from and date_to and col_name and mode and counting and file_type and file_name:
        date_from = Utils.timestr2time(f'{date_from} 00:00:00')
        date_to = Utils.timestr2time(f'{date_to} 00:00:00')
        if counting == 'single':
            return data_show.generate_figure_statistics_single(
                pid, date_from, date_to, file_type, file_name, col_name, mode)
        elif counting == 'multiple':
            if type(pid) is int:
                pid = [pid]
            return data_show.generate_figure_statistics_multiple(
                pid, date_from, date_to, file_type, file_name, col_name, mode)
    else:
        return blank_figure

# endregion


if __name__ == "__main__":
    app.run_server(debug=False)

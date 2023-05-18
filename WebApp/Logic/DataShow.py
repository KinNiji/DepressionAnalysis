import datetime

import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import Config
import Utils
from WebApp.Logic.DbSession import DbSession

BEGIN_TIME = Utils.timestr2time(Config.BEGIN_TIME_STR)
DAY = datetime.timedelta(days=1)
HOUR = datetime.timedelta(hours=1)


def filter_day(df, date, timestamp_col_name):
    begin_timestamp_day = Utils.time2timestamp(date)
    end_timestamp_day = Utils.time2timestamp(date + DAY)
    df_day = df[(begin_timestamp_day <= df[timestamp_col_name]) & (df[timestamp_col_name] < end_timestamp_day)]
    return df_day


def filter_day_section(df, date_from, date_to, timestamp_col_name):
    begin_timestamp_day = Utils.time2timestamp(date_from)
    end_timestamp_day = Utils.time2timestamp(date_to + DAY)
    df_days = df[(begin_timestamp_day <= df[timestamp_col_name]) & (df[timestamp_col_name] < end_timestamp_day)]
    return df_days


def get_hour(timestamp):
    return int((Utils.timestamp2time(timestamp) - BEGIN_TIME).total_seconds() // 3600)


def get_day(timestamp):
    return (Utils.timestamp2time(timestamp) - BEGIN_TIME).days + 1


def get_week(timestamp):
    return (Utils.timestamp2time(timestamp) - BEGIN_TIME).days // 7 + 1


def generate_col_statistics(df, col_name, pid, groupby):
    if 'record_time' in df.columns:
        df['timestamp'] = df['record_time']
    df['record_time'] = df['timestamp'].apply(Utils.timestamp2time)
    df['hour'] = df['timestamp'].apply(get_hour)
    df['day'] = df['timestamp'].apply(get_day)
    df['week'] = df['timestamp'].apply(get_week)

    df_features_by_day = df.groupby(groupby)[col_name].agg(
        ['mean', 'median', 'min', 'max', Utils.quantile_25, Utils.quantile_75, 'std', 'skew', 'count']
    ).reset_index().dropna()

    df_features_by_day['pid'] = pid
    return df_features_by_day


def generate_col_statistics_single_fun(df, col_name, pid, groupby, fun_name):
    if 'record_time' in df.columns:
        df['timestamp'] = df['record_time']
    df['record_time'] = df['timestamp'].apply(Utils.timestamp2time)
    df['hour'] = df['timestamp'].apply(get_hour)
    df['day'] = df['timestamp'].apply(get_day)
    df['week'] = df['timestamp'].apply(get_week)

    if fun_name == 'quantile_25':
        fun_name = Utils.quantile_25
    elif fun_name == 'quantile_75':
        fun_name = Utils.quantile_75

    df_features_by_day = df.groupby(groupby)[col_name].agg(
        [fun_name]
    ).reset_index().dropna()

    df_features_by_day['pid'] = pid
    return df_features_by_day


class DataShow:
    def __init__(self):
        self.mysql = DbSession(Config.HOST, Config.USER, Config.PASSWORD, Config.DATABASE, Config.PORT)

    def generate_figure_extracted(self, pid, date, file_name):
        upload_info = self.select_by_pid(pid)
        upload_time = upload_info['upload_time']
        external_id = upload_info['external_id']

        extract_info = Config.EXTRACT_INFO[file_name]
        df = filter_day(pd.read_csv(
            f"{Config.APP_DATA_FILE_PATH}/{upload_time}/extracted/{file_name}/{external_id}.csv",
            encoding="utf-8"
        ).astype(extract_info['dtype']), date, 'record_time').sort_values(by=['record_time'])
        df['record_time'] = df['record_time'].apply(Utils.timestamp2timestr)
        fig = go.Figure()
        for col_name in df.columns:
            if col_name in ['record_time', 'external_id', 'activity_name', 'sqi']:
                continue
            fig.add_trace(go.Scattergl(
                x=df['record_time'],
                y=df[col_name],
                mode='lines+markers',
                name=f"{col_name}({extract_info['processor']['detail_unit'][col_name]})",
            ))
            if file_name == 'continuousrri':
                fig.add_trace(go.Scattergl(
                    x=df['record_time'].loc[df['sqi'] == 0],
                    y=df['rri'].loc[df['sqi'] == 0],
                    mode='markers',
                    name='rri(ms)(sqi=0)',
                ))
            if len(df.columns) <= 4:
                fig.update_yaxes(title_text=f"{col_name}({extract_info['processor']['detail_unit'][col_name]})")
        fig.update_xaxes(title_text='record_time')
        fig.update_layout(
            plot_bgcolor='white',
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        return fig

    def generate_figure_resampled(self, pid, date, file_name):
        upload_info = self.select_by_pid(pid)
        upload_time = upload_info['upload_time']
        external_id = upload_info['external_id']

        df = filter_day(pd.read_csv(
            f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/{file_name}/{external_id}.csv",
            encoding="utf-8"
        ), date, 'timestamp').sort_values(by=['timestamp'])
        df['record_time'] = df['timestamp'].apply(Utils.timestamp2time)
        fig = go.Figure()
        if file_name == 'minute':
            for col_name in df.columns:
                if col_name in ['timestamp', 'record_time']:
                    continue
                fig.add_trace(go.Scattergl(
                    x=df['record_time'],
                    y=df[col_name],
                    mode='lines+markers',
                    name=col_name,
                ))
        elif file_name == 'continuousrri':
            fig.add_trace(go.Scattergl(
                x=df['record_time'],
                y=df['rri'],
                mode='lines+markers',
                name="rri(ms)",
            ))
            fig.add_trace(go.Scattergl(
                x=df['record_time'].loc[df['sqi'] < 50],
                y=df['rri'].loc[df['sqi'] < 50],
                mode='markers',
                name='rri(ms)(sqi<50)',
            ))
            fig.update_yaxes(title_text="rri(ms)")
        fig.update_xaxes(
            title_text='record_time',
            range=[df.iloc[0]['record_time'], df.iloc[int(df.shape[0] / 9)]['record_time']]
        )
        fig.update_layout(
            plot_bgcolor='white',
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        return fig

    def generate_figure_statistics_single(self, pid, date_from, date_to, file_type, file_name, col_name, groupby):
        upload_info = self.select_by_pid(pid)
        upload_time = upload_info['upload_time']
        external_id = upload_info['external_id']

        df = pd.DataFrame()
        extract_info = {}
        if file_type == 'extracted_file':
            extract_info = Config.EXTRACT_INFO[file_name]
            df = filter_day_section(pd.read_csv(
                f"{Config.APP_DATA_FILE_PATH}/{upload_time}/extracted/{file_name}/{external_id}.csv",
                encoding="utf-8"
            ).astype(extract_info['dtype']), date_from, date_to, 'record_time').sort_values(by=['record_time'])
        elif file_type == 'resampled_file':
            df = filter_day_section(pd.read_csv(
                f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/{file_name}/{external_id}.csv",
                encoding="utf-8"
            ), date_from, date_to, 'timestamp').sort_values(by=['timestamp'])
            df = df[~(df[col_name] == 0)]
        df_agg = generate_col_statistics(df, col_name, 0, groupby)

        fig = go.Figure()
        for agg_col in df_agg.columns:
            if agg_col in [groupby, 'pid']:
                continue
            fig.add_trace(go.Scatter(
                x=df_agg[groupby],
                y=df_agg[agg_col],
                mode='lines+markers',
                name=agg_col,
            ))
        fig.update_xaxes(
            title_text=groupby,
            tickmode='array',
            tickvals=df_agg[groupby],
            range=[
                df_agg.iloc[0][groupby],
                df_agg.iloc[10][groupby] if df_agg.shape[0] >= 10 else df_agg.iloc[-1][groupby]
            ]
        )
        fig.update_yaxes(
            title_text=f"{col_name}({extract_info['processor']['detail_unit'][col_name]})"
            if file_type == 'extracted' else col_name
        )
        fig.update_layout(
            plot_bgcolor='white',
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        return fig

    def generate_figure_statistics_multiple(self, pid_list, date_from, date_to, file_type, file_name, col_name, mode):
        df = pd.DataFrame()
        for pid in pid_list:
            upload_info = self.select_by_pid(pid)
            upload_time = upload_info['upload_time']
            external_id = upload_info['external_id']
            if file_type == 'extracted_file':
                df_ex = filter_day_section(pd.read_csv(
                    f"{Config.APP_DATA_FILE_PATH}/{upload_time}/extracted/{file_name}/{external_id}.csv",
                    encoding="utf-8"
                ).astype(Config.EXTRACT_INFO[file_name]['dtype']), date_from, date_to, 'record_time').sort_values(by=['record_time'])
                df_ex['pid'] = pid
                df_ex['day'] = df_ex['record_time'].apply(get_day)
                df = pd.concat([df, df_ex], axis=0)
            elif file_type == 'resampled_file':
                df_ex = filter_day_section(pd.read_csv(
                    f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/{file_name}/{external_id}.csv",
                    encoding="utf-8"
                ), date_from, date_to, 'timestamp').sort_values(by=['timestamp'])
                df_ex = df_ex[~(df_ex[col_name] == 0)]
                df_ex['pid'] = pid
                df_ex['day'] = df_ex['timestamp'].apply(get_day)
                df = pd.concat([df, df_ex], axis=0)

        fig = go.Figure()
        if mode == 'violin':
            fig = px.violin(df, x='pid', y=col_name, color='pid', color_discrete_sequence=px.colors.qualitative.Set3)
        elif mode == 'box':
            fig = px.box(df, x='pid', y=col_name, color='pid', color_discrete_sequence=px.colors.qualitative.Set3)
        elif mode == 'hist':
            fig = px.histogram(
                df, x='pid',
                color_discrete_sequence=px.colors.qualitative.Set3,
                category_orders=dict(x=pid_list)
            ).update_layout(bargap=0.2)
        elif mode == 'heat':
            if file_type == 'extracted_file':
                df['day'] = df['record_time'].apply(get_day)
            elif file_type == 'resampled_file':
                df['day'] = df['timestamp'].apply(get_day)
            fig = px.density_heatmap(df, x='pid', y='day', color_continuous_scale='mint')
        fig.update_layout(
            plot_bgcolor='white',
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        return fig

    def select_by_pid(self, pid):
        sql = self.mysql.get_sql('App.AnalysisShow.SelectByPid')
        result = self.mysql.select(sql, pid)
        if result and result[0]:
            return {
                'upload_time': result[0][0],
                'upload_user_id': result[0][1],
                'external_id': result[0][2]
            }
        else:
            return None

    def select_pid_all(self):
        sql = self.mysql.get_sql('App.AnalysisShow.SelectPidAll')
        result = self.mysql.select(sql)
        if result:
            upload_info_all = {}
            for line in result:
                upload_info_all[line[0]] = {
                    'upload_time': line[1],
                    'upload_user_id': line[2],
                    'external_id': line[3]
                }
            return upload_info_all
        else:
            return None

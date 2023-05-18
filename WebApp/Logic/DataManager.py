import datetime

import pandas as pd
import json
import jsonpath
import os

from tqdm import tqdm

import Config
import Utils
from WebApp.Logic.DbSession import DbSession

BEGIN_TIMESTAMP = str(Utils.timestr2timestamp(Config.BEGIN_TIME_STR))
END_TIMESTAMP = str(Utils.timestr2timestamp(Config.END_TIME_STR))
BEGIN_TIME = Utils.timestr2time(Config.BEGIN_TIME_STR)
END_TIME = Utils.timestr2time(Config.END_TIME_STR)
DAY = datetime.timedelta(days=1)
HOUR = datetime.timedelta(hours=1)


class DataManager:
    def __init__(self):
        self.mysql = DbSession(Config.HOST, Config.USER, Config.PASSWORD, Config.DATABASE, Config.PORT)

    def extract_raw(self, file_name, current_time, user_id, file_path=None, df=None):
        try:
            print(file_name)
            extract_info = Config.EXTRACT_INFO[file_name]
            processor = extract_info['processor']
            if file_path:
                df = pd.read_csv(f"{file_path}/{file_name}.csv", encoding="utf-8", dtype=str)[
                    extract_info['useful_cols']]
            # 对时间进行筛选
            df = df[(BEGIN_TIMESTAMP <= df['recordtime']) & (df['recordtime'] < END_TIMESTAMP)].drop_duplicates()
            os.makedirs(f"{Config.APP_DATA_FILE_PATH}/{current_time}/extracted/{file_name}", exist_ok=True)

            external_id_list = df['externalid'].unique()
            line_count = 0
            data_count = 0
            for external_id in tqdm(external_id_list):
                df_ex = df[df['externalid'] == external_id]
                external_id = int(external_id)
                useful_data = []
                for index, line in df_ex.iterrows():
                    json_data = json.loads(line[processor['col_name']].replace("'", '"'))
                    sampling_unit = processor['sampling_unit']
                    detail_path = processor['detail_path']
                    if sampling_unit == 'minute':
                        extracted_line = {
                            'record_time': line['recordtime'],
                            'external_id': int(line['externalid']),
                            # 'upload_time': current_time
                        }
                        for detail_name, path in detail_path.items():
                            extracted_line[detail_name] = jsonpath.jsonpath(json_data, path)[0]
                        useful_data.append(extracted_line)
                        data_count += 1
                    elif sampling_unit == 'second':
                        for json_data_line in json_data:
                            extracted_line = {
                                'record_time': json_data_line['timeFrame']['timestamp'],
                                'external_id': int(line['externalid']),
                                'rri': json_data_line['rri']['value'],
                                'sqi': json_data_line['sqi'],
                                # 'upload_time': current_time
                            }
                            # for detail_name, path in detail_path.items():
                            #     extracted_line[detail_name] = jsonpath.jsonpath(json_data_line, path)[0]
                            useful_data.append(extracted_line)
                            data_count += 1
                    line_count += 1
                    # if count % 100000 == 0 or count == len(df):
                    #     df_useful = pd.DataFrame(useful_data).astype(extract_info['dtype'])
                    #     dict_to_db = {_: list(df_useful[_]) for _ in extract_info['dtype']}
                    #     self.mysql.quick_insert(extract_info['table_name'], dict_to_db, many=True, ignore=True)
                    #     useful_data = []
                df_useful = pd.DataFrame(useful_data).astype(extract_info['dtype'])
                df_useful.to_csv(
                    f"{Config.APP_DATA_FILE_PATH}/{current_time}/extracted/{file_name}/{external_id}.csv",
                    encoding="utf-8", index=False)
                result = self.select_pid(current_time, user_id, external_id)
                extract_info_sql = json.loads(result[4])
                extract_info_sql[file_name] = True
                self.update_pid_extract(current_time, user_id, external_id, json.dumps(extract_info_sql))

            result = self.select_upload(current_time, user_id)
            upload_info = json.loads(result[2])
            external_id_list = [int(_) for _ in external_id_list]
            external_id_list = list(set(external_id_list))
            external_id_list.sort()
            upload_info.append({
                'file_name': file_name,
                'upload': True,
                'resample': False,
                'external_ids': ','.join('%d' % external_id_list[j] for j in range(len(external_id_list))),
                'line_count': line_count,
                'data_count': data_count
            })
            self.update_upload(current_time, user_id, json.dumps(upload_info))

        except Exception as err:
            format_err = f"data extract from {file_name} failed: {err}"
            Utils.Logger().error(format_err)
            raise Exception(format_err)

    def resample_extracted(self, upload_time, upload_user_id, upload_info):
        try:
            external_id_list = set()
            for info in upload_info:
                for i in info['external_ids'].split(','):
                    external_id_list.add(int(i))
            external_id_list = list(external_id_list)

            for external_id in tqdm(external_id_list):
                df_resampled_person = pd.DataFrame()
                for info in upload_info:
                    file_name = info['file_name']
                    extract_info = Config.EXTRACT_INFO[file_name]
                    processor = extract_info['processor']
                    df = pd.DataFrame(columns=extract_info['dtype'].keys())
                    if os.path.exists(
                            f"{Config.APP_DATA_FILE_PATH}/{upload_time}/extracted/{file_name}/{external_id}.csv"):
                        df = pd.read_csv(
                            f"{Config.APP_DATA_FILE_PATH}/{upload_time}/extracted/{file_name}/{external_id}.csv",
                            encoding="utf-8").astype(extract_info['dtype']).sort_values(by=['record_time'])
                    sampling_unit = processor['sampling_unit']
                    if sampling_unit == 'minute':
                        for col_name in processor['detail_unit'].keys():
                            if extract_info['dtype'][col_name] == 'str':
                                continue
                            df_resampled_person_col = self.resample_minute_col(
                                df, col_name, extract_info['dtype'][col_name])
                            df_resampled_person = pd.concat([df_resampled_person, df_resampled_person_col], axis=1)
                    elif sampling_unit == 'second':
                        df_resampled_person_second = self.resample_second(df)
                        df_resampled_person_second.to_csv(
                            f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/second/{external_id}.csv",
                            encoding="utf-8", index=False)
                    result = self.select_pid(upload_time, upload_user_id, external_id)
                    resample_info_sql = json.loads(result[5])
                    resample_info_sql[file_name] = True
                    self.update_pid_resample(upload_time, upload_user_id, external_id, json.dumps(resample_info_sql))

                minute_data = []
                for day in range((END_TIME - BEGIN_TIME).days):
                    begin_time_day = BEGIN_TIME + day * DAY + 6 * HOUR
                    end_time_day = BEGIN_TIME + (day + 1) * DAY
                    begin_timestamp_day = Utils.time2timestamp(begin_time_day)
                    for minute in range((end_time_day - begin_time_day).seconds // 60):
                        timestamp = begin_timestamp_day + minute * 60000
                        minute_data.append({'timestamp': int(timestamp)})
                df_minute = pd.DataFrame(minute_data).astype('int64')

                df_resampled_person = pd.concat([df_minute, df_resampled_person], axis=1)
                df_resampled_person.to_csv(
                    f"{Config.APP_DATA_FILE_PATH}/{upload_time}/resampled/minute/{external_id}.csv",
                    encoding="utf-8", index=False)

            result = self.select_upload(upload_time, upload_user_id)
            upload_info = json.loads(result[2])
            for i in range(len(upload_info)):
                upload_info[i]['resample'] = True
            self.update_upload(upload_time, upload_user_id, json.dumps(upload_info))

        except Exception as err:
            format_err = f"data resample failed: {err}"
            Utils.Logger().error(format_err)
            raise Exception(format_err)

    @staticmethod
    def resample_minute_col(df, col_name, dtype):
        df = df[['record_time', col_name]]
        df = Utils.abnormal_processing(df, col_name, Utils.mask_over_3std, Utils.fill_nearest)
        df_resampled = pd.DataFrame()
        for day in range((END_TIME - BEGIN_TIME).days):
            begin_time_day = BEGIN_TIME + day * DAY + 6 * HOUR
            end_time_day = BEGIN_TIME + (day + 1) * DAY
            begin_timestamp_day = Utils.time2timestamp(begin_time_day)
            end_timestamp_day = Utils.time2timestamp(end_time_day)
            df_day = df[(begin_timestamp_day <= df['record_time']) & (df['record_time'] < end_timestamp_day)]
            df_head = pd.DataFrame({col_name: [0], "record_time": [begin_timestamp_day]})
            df_tail = pd.DataFrame({col_name: [0], "record_time": [end_timestamp_day]})
            df_day = pd.concat([df_head, df_day, df_tail], axis=0, ignore_index=True)

            resampled_data = []
            for minute in range((end_time_day - begin_time_day).seconds // 60):
                timestamp = begin_timestamp_day + minute * 60000
                resampled_data.append({col_name: 0, 'record_time': int(timestamp)})
            df_day_resampled = pd.DataFrame(resampled_data)

            resampled_data = []
            for i in range(len(df_day) - 1):
                line = df_day.iloc[i]
                next_line = df_day.iloc[i + 1]
                period_length = next_line['record_time'] - line['record_time']
                # 两次采样时间间隔大于等于5分钟视为数据缺失时段
                if period_length > 5 * 60000:
                    continue
                else:
                    # 两次采样时间所在分钟
                    line_minute = int(line['record_time'] // 60000)
                    next_line_minute = int(next_line['record_time'] // 60000)
                    # 第二次采样时间为整分钟时视作上一分钟
                    if next_line['record_time'] % 60000 == 0:
                        next_line_minute -= 1
                    # 两次采样时间在同一分钟内，不重采样
                    if period_length < 60000 - 1 and line_minute == next_line_minute:
                        continue
                    # 不在同一分钟内，线性插值的方式进行重采样
                    else:
                        # 第一次采样时间为整分钟时对该分钟进行一次重采样
                        if line['record_time'] % 60000 == 0 and line['record_time'] != begin_timestamp_day:
                            resampled_data.append({
                                col_name: line[col_name],
                                'record_time': int(line['record_time']),
                            })
                        # 两次采样时间中的每一分钟进行一次重采样
                        for j in range(next_line_minute - line_minute):
                            resample_timestamp = (line_minute + j + 1) * 60000
                            resampled_data.append({
                                col_name: Utils.linear_interpolation(
                                    resample_timestamp,
                                    line['record_time'], line[col_name],
                                    next_line['record_time'], next_line[col_name]),
                                'record_time': int(resample_timestamp),
                            })
            # 将初始化的数据中已经重采样过的去除，然后拼接上重采样的数据
            df_day_resampled2 = pd.DataFrame(resampled_data)
            if resampled_data:
                df_day_resampled = df_day_resampled[-df_day_resampled['record_time'].isin(
                    df_day_resampled2['record_time'].to_list())]
            df_day_resampled = pd.concat(
                [df_day_resampled, df_day_resampled2],
                axis=0, ignore_index=True
            ).sort_values(by=['record_time']).drop_duplicates()

            df_resampled = pd.concat([df_resampled, df_day_resampled], axis=0, ignore_index=True)
        return df_resampled.drop('record_time', axis=1).fillna(0).astype(dtype)

    @staticmethod
    def resample_second(df):
        df = Utils.abnormal_processing(df, 'rri', Utils.mask_over_3std, Utils.fill_nearest)
        df_resampled = pd.DataFrame()
        for day in tqdm(range((END_TIME - BEGIN_TIME).days)):
            # 每天6:00~次日0:00
            begin_time_day = BEGIN_TIME + day * DAY + 6 * HOUR
            end_time_day = BEGIN_TIME + (day + 1) * DAY
            begin_timestamp_day = Utils.time2timestamp(begin_time_day)
            end_timestamp_day = Utils.time2timestamp(end_time_day)
            df_day = df[(begin_timestamp_day <= df['record_time']) & (df['record_time'] < end_timestamp_day)]
            df_head = pd.DataFrame({"rri": [0], "sqi": [0], "record_time": [begin_timestamp_day]})
            df_tail = pd.DataFrame({"rri": [0], "sqi": [0], "record_time": [end_timestamp_day]})
            # df_tail.columns = df_day.columns
            df_day = pd.concat([df_head, df_day, df_tail], axis=0, ignore_index=True)

            # 重采样每天6:00~次日0:00的每一秒，全部初始化为missing
            resampled_data = []
            for second in range((end_time_day - begin_time_day).seconds):
                timestamp = begin_timestamp_day + second * 1000
                resampled_data.append({'rri': 0, 'sqi': 0, 'record_time': int(timestamp)})
            df_day_resampled = pd.DataFrame(resampled_data)

            resampled_data = []
            for i in range(len(df_day) - 1):
                line = df_day.iloc[i]
                next_line = df_day.iloc[i + 1]
                period_length = next_line['record_time'] - line['record_time']
                # 两次采样时间间隔大于等于5000毫秒视为数据缺失时段
                if period_length >= 5000:
                    continue
                else:
                    # 两次采样时间所在秒数
                    line_second = int(line['record_time'] / 1000)
                    next_line_second = int(next_line['record_time'] / 1000)
                    # 第二次采样时间为整秒时视作上一秒
                    if next_line['record_time'] % 1000 == 0:
                        next_line_second -= 1
                    # 两次采样时间在同一秒内，不重采样
                    if period_length < 999 and line_second == next_line_second:
                        continue
                    # 不在同一秒内，线性插值的方式进行重采样
                    else:
                        # 第一次采样时间为整秒时对该秒进行一次重采样
                        if line['record_time'] % 1000 == 0 and line['record_time'] != begin_timestamp_day:
                            resampled_data.append({
                                'rri': int(line['rri']),
                                'sqi': int(line['sqi']),
                                'record_time': int(line['record_time']),
                            })
                        # 两次采样时间中的每一秒进行一次重采样
                        for j in range(next_line_second - line_second):
                            resample_timestamp = (line_second + j + 1) * 1000
                            resampled_data.append({
                                'rri': int(Utils.linear_interpolation(
                                    resample_timestamp,
                                    line['record_time'], line['rri'],
                                    next_line['record_time'], next_line['rri'])),
                                'sqi': int(Utils.linear_interpolation(
                                    resample_timestamp,
                                    line['record_time'], line['sqi'],
                                    next_line['record_time'], next_line['sqi'])),
                                'record_time': int(resample_timestamp),
                            })
            # 将初始化的数据中已经重采样过的去除，然后拼接上重采样的数据
            df_day_resampled2 = pd.DataFrame(resampled_data)
            if resampled_data:
                df_day_resampled = df_day_resampled[-df_day_resampled['record_time'].isin(
                    df_day_resampled2['record_time'].to_list())]
            df_day_resampled = pd.concat(
                [df_day_resampled, df_day_resampled2],
                axis=0, ignore_index=True
            ).sort_values(by=['record_time']).drop_duplicates()

            df_resampled = pd.concat([df_resampled, df_day_resampled], axis=0, ignore_index=True)

        return df_resampled.astype({'record_time': 'int64',
                                    'rri': 'int',
                                    'sqi': 'int'}).rename(columns={'record_time': 'timestamp'})

    def insert_upload(self, timestamp, user_id):
        self.mysql.quick_insert('app_upload',
                                {'upload_time': timestamp,
                                 'upload_user_id': user_id,
                                 'upload_info': json.dumps([])}
                                )

    def select_upload(self, timestamp, user_id):
        sql = self.mysql.get_sql('App.AnalysisUpload.Select')
        result = self.mysql.select(sql, timestamp, user_id)
        if result:
            return result[0]
        else:
            return None

    def select_upload_all(self):
        sql = self.mysql.get_sql('App.AnalysisUpload.SelectAll')
        result = self.mysql.select(sql)
        if result:
            df = pd.DataFrame(result, columns=['upload_time', 'upload_user_id', 'upload_info'])
            return df
        else:
            return pd.DataFrame(columns=['upload_time', 'upload_user_id', 'upload_info'])

    def update_upload(self, timestamp, user_id, upload_info):
        sql = self.mysql.get_sql('App.AnalysisUpload.Update')
        return self.mysql.update(sql, upload_info, timestamp, user_id)

    def insert_pid(self, timestamp, user_id, external_id):
        empty_info = {
            "continuousbloodoxygensaturation": False,
            "continuousheartrate": False,
            "dailyworkoutdetail": False,
            "continuousrri": False
        }
        self.mysql.quick_insert('app_data_pid',
                                {'upload_time': timestamp,
                                 'upload_user_id': user_id,
                                 'external_id': external_id,
                                 'extract_info': json.dumps(empty_info),
                                 'resample_info': json.dumps(empty_info)}
                                )

    def select_pid(self, timestamp, user_id, external_id):
        sql = self.mysql.get_sql('App.AnalysisUpload.SelectPid')
        result = self.mysql.select(sql, timestamp, user_id, external_id)
        if result:
            return result[0]
        else:
            empty_info = {
                "continuousbloodoxygensaturation": False,
                "continuousheartrate": False,
                "dailyworkoutdetail": False,
                "continuousrri": False
            }
            self.insert_pid(timestamp, user_id, external_id)
            return ['', timestamp, user_id, external_id, json.dumps(empty_info), json.dumps(empty_info)]

    def update_pid_extract(self, timestamp, user_id, external_id, extract_info):
        sql = self.mysql.get_sql('App.AnalysisUpload.UpdatePidExtract')
        return self.mysql.update(sql, extract_info, timestamp, user_id, external_id)

    def update_pid_resample(self, timestamp, user_id, external_id, resample_info):
        sql = self.mysql.get_sql('App.AnalysisProcess.UpdatePidResample')
        return self.mysql.update(sql, resample_info, timestamp, user_id, external_id)


    # def select_extracted(self, file_name, timestamp):
    #     extract_info = Config.EXTRACT_INFO[file_name]
    #     sql = self.mysql.get_sql('App.AnalysisProcess.Select').format(extract_info['table_name'])
    #     result = self.mysql.select(sql, timestamp)
    #     if result:
    #         df = pd.DataFrame(result, columns=list(extract_info['dtype'].keys())).astype(extract_info['dtype'])
    #         return df
    #     else:
    #         return pd.DataFrame(columns=list(extract_info['dtype'].keys()))


if __name__ == '__main__':
    dm = DataManager()
    # for fn in ['continuousbloodoxygensaturation', 'continuousheartrate', 'dailyworkoutdetail', 'continuousrri']:
    #     dm.extract_raw(fn, '1683703843555', '1', file_path='data/1683703843555/raw')

    jstr = '[{"file_name": "continuousbloodoxygensaturation", "upload": true, "resample": false, "external_ids": "1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59", "line_count": 198737, "data_count": 198737}, {"file_name": "continuousheartrate", "upload": true, "resample": false, "external_ids": "1,2,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59", "line_count": 1215714, "data_count": 1215714}, {"file_name": "dailyworkoutdetail", "upload": true, "resample": false, "external_ids": "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59", "line_count": 247947, "data_count": 247947}, {"file_name": "continuousrri", "upload": true, "resample": false, "external_ids": "1,2,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59", "line_count": 930995, "data_count": 61721360}]'
    dm.resample_extracted('1683703843555', '1', json.loads(jstr))


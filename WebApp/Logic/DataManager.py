import pandas as pd
import json
import jsonpath
import os

from tqdm import tqdm
import Config
import Utils
from WebApp.Logic.DbSession import DbSession

BEGIN_TIME = str(Utils.timestr2timestamp(Config.BEGIN_TIME))
END_TIME = str(Utils.timestr2timestamp(Config.END_TIME))


class DataManager:
    def __init__(self):
        self.mysql = DbSession(Config.HOST, Config.USER, Config.PASSWORD, Config.DATABASE, Config.PORT)

    def extract_raw(self, file_name, current_time, user_id, file_path=None, df=None):
        try:
            extract_info = Config.EXTRACT_INFO[file_name]
            processor = extract_info['processor']
            if file_path:
                df = pd.read_csv(f"{file_path}/{file_name}.csv", encoding="utf-8", dtype=str)[
                    extract_info['useful_cols']]
            print('loading data complete')
            # 对时间进行筛选
            df = df[(BEGIN_TIME <= df['recordtime']) & (df['recordtime'] < END_TIME)].drop_duplicates()
            external_id_list = [int(_) for _ in df['externalid'].unique()]
            useful_data = []
            count = 0
            sql_count = 0
            for index, line in df.iterrows():
                json_data = json.loads(line[processor['col_name']].replace("'", '"'))
                sampling_unit = processor['sampling_unit']
                detail_path = processor['detail_path']
                if sampling_unit == 'minute':
                    extracted_line = {
                        'record_time': line['recordtime'],
                        'external_id': f"{current_time}{int(line['externalid'])}"
                    }
                    for detail_name, path in detail_path.items():
                        extracted_line[detail_name] = jsonpath.jsonpath(json_data, path)[0]
                    useful_data.append(extracted_line)
                    sql_count += 1
                elif sampling_unit == 'second':
                    for json_data_line in json_data:
                        extracted_line = {
                            'record_time': line['recordtime'],
                            'external_id': f"{current_time}{int(line['externalid'])}",
                            'rri': json_data_line['rri']['value'],
                            'sqi': json_data_line['sqi'],
                            'timestamp': json_data_line['timeFrame']['timestamp']
                        }
                        # for detail_name, path in detail_path.items():
                        #     extracted_line[detail_name] = jsonpath.jsonpath(json_data_line, path)[0]
                        useful_data.append(extracted_line)
                        sql_count += 1
                count += 1
                if count % 100000 == 0 or count == len(df):
                    print(f'{count}/{len(df)} {sql_count}')
                    df_useful = pd.DataFrame(useful_data).astype(extract_info['dtype'])
                    # print(df_useful.info())
                    # print(df_useful.head())
                    dict_to_db = {_: list(df_useful[_]) for _ in extract_info['dtype']}
                    # print(dict_to_db)
                    # print(list(zip(*dict_to_db.values())))
                    self.mysql.quick_insert(extract_info['table_name'], dict_to_db, many=True, ignore=True)
                    useful_data = []
                    # break

            result = self.select_upload(current_time, user_id)
            if not result:
                self.mysql.quick_insert('app_upload',
                                        {'timestamp': current_time,
                                         'user_id': user_id,
                                         'upload_info': json.dumps({file_name: {
                                             'upload': True,
                                             'external_ids': external_id_list,
                                             'count': count,
                                             'sql_count': sql_count
                                         }})})
            else:
                upload_info = json.loads(result[2])
                upload_info[file_name] = {
                    'upload': True,
                    'external_ids': external_id_list,
                    'count': count,
                    'sql_count': sql_count
                }
                self.update_upload(current_time, user_id, json.dumps(upload_info))

        except Exception as err:
            format_err = f"data extract from {file_name} failed: {err}"
            Utils.Logger().error(format_err)
            raise Exception(format_err)

    def select_upload(self, timestamp, user_id):
        sql = self.mysql.get_sql('App.AnalysisUpload.Select')
        result = self.mysql.select(sql, timestamp, user_id)
        if result:
            return result[0]
        else:
            return None

    def update_upload(self, timestamp, user_id, upload_info):
        sql = self.mysql.get_sql('App.AnalysisUpload.Update')
        print(type(upload_info), timestamp, user_id, sql, upload_info)
        return self.mysql.update(sql, upload_info, timestamp, user_id)

    def resample_extracted(self, file_name, df):
        try:
            extract_info = Config.EXTRACT_INFO[file_name]
            processor = extract_info['processor']
            df = df.astype(extract_info['dtype']).sort_values(by=['timestamp'])
        except Exception as err:
            format_err = f"data resample from {file_name} failed: {err}"
            Utils.Logger().error(format_err)
            raise Exception(format_err)


def generate_test_raw():
    for file_name in Config.EXTRACT_INFO.keys():
        df = pd.read_csv(f"{DATA_FILE_PATH}/{file_name}.csv", encoding="utf-8", dtype=str)
        df_ex = df[(df['externalid'] == '1') | (df['externalid'] == '02')]
        df_ex.to_csv(f"{DATA_FILE_PATH}/{file_name}_test.csv", encoding="utf-8", index=False)


if __name__ == '__main__':
    DATA_FILE_PATH = Config.DATA_FILE_PATH_CONTINUOUS_RAW
    # generate_test_raw()
    # 1682597426005
    # int(datetime.datetime.now().timestamp() * 1000)
    dm = DataManager()
    dm.extract_raw('continuousrri', 1682597426000, 1, file_path=DATA_FILE_PATH)
    # resample_extracted()

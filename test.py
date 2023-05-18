# import WebApp.Logic.User

# user = WebApp.Logic.User.User()
# # print(user.encrypt_sha1('123456'), len(user.encrypt_sha1('123456')))
# # print(user.encrypt_sha1('jahsfosahklfhaks'), len(user.encrypt_sha1('jahsfosahklfhaks')))
# # print(user.user_create('test', '123456'))
# # print(user.update_password('admin', '123456'))
# # print(user.login_check('admin', '123456'))


# def temp(*args):
#     print(args)


# temp(1, 2, 3, 4)
#
# import Utils
#
# print(Utils.timestr2timestamp('2021-12-09 00:00:00'))
# import json
#
# import pandas as pd
#
# temp = '{"continuousbloodoxygensaturation": {"upload": true, "external_ids": [1], "count": 1567, "sql_count": 1567}, "dailyworkoutdetail": {"upload": true, "external_ids": [1], "count": 5945, "sql_count": 5945}, "continuousheartrate": {"upload": true, "external_ids": [1, 2], "count": 22914, "sql_count": 22914}, "continuousrri": {"upload": true, "external_ids": [1, 2], "count": 23480, "sql_count": 1632031}}'
#
# t = json.loads(temp)
#
# df = pd.DataFrame(t)
#
# print(df.T)
import pandas as pd

import Config
import Utils

DATA_FILE_PATH = Config.DATA_FILE_PATH_CONTINUOUS_RAW


# for file_name in Config.EXTRACT_INFO.keys():
#     df = pd.read_csv(f"{DATA_FILE_PATH}/{file_name}.csv", encoding="utf-8", dtype=str)
#     df_ex = df[(df['externalid'] == '58') | (df['externalid'] == '59')]
#     df_ex.to_csv(f"{DATA_FILE_PATH}/{file_name}_test.csv", encoding="utf-8", index=False)

BEGIN_TIME = Utils.timestr2time(Config.BEGIN_TIME_STR)
END_TIME = Utils.timestr2time(Config.END_TIME_STR)
minute_data = []
for minute in range((END_TIME - BEGIN_TIME).days * 18 * 60):
    timestamp = Utils.time2timestamp(BEGIN_TIME) + minute * 60000
    minute_data.append({'timestamp': int(timestamp)})
df_minute = pd.DataFrame(minute_data)
print(BEGIN_TIME, END_TIME, END_TIME - BEGIN_TIME, int((END_TIME - BEGIN_TIME).days))
print((END_TIME - BEGIN_TIME).days * 18 * 60)
print(minute_data)
print(df_minute, df_minute.info())

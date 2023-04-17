from hiresearchsdk import BridgeClient
from hiresearchsdk.config import BridgeConfig, HttpClientConfig
from hiresearchsdk.model import AuthRequest
from hiresearchsdk.model.table import SearchTableDataRequest, FilterCondition, FilterOperatorType, FilterLogicType

import pandas as pd

import os


# 初始化BridgeConfig类
bridge_config = BridgeConfig("ilqzwbks", "product")
# 连接超时时间，单位s，不设置则默认30s
connect_timeout = 20
# 等待接口返回超时时间，单位s，不设置则默认30s
read_timeout = 20
# 是否失败重试，默认不重试
retry_on_fail = True
# 初始化HttpClientConfig类
http_config = HttpClientConfig(connect_timeout, read_timeout, retry_on_fail)
bridge_client = BridgeClient(bridge_config, http_config)
# 获取SDK鉴权
request = AuthRequest("268bbf555d25486c91d293978744fed8",
                      "efea0336b53351e99b63725bfc1a0272c00b4aa9d584a8c4325d4e0078e5c4b5")
auth_response = bridge_client.get_authenticate_provider().auth(request)
access_token = auth_response.get_accessToken()
access_token_durationIn_millis = auth_response.get_accessTokenDurationInMillis()
refresh_token = auth_response.get_refreshToken()
refresh_token_duration_in_millis = auth_response.get_refreshTokenDurationInMillis()


def get_table_data(table_id, file_path, condition=None, name=None, sort_fields=None):
    req = SearchTableDataRequest(access_token, table_id, desired_size=2000)

    # 构造回调函数
    def rows_processor(rows, total_cnt):
        print("total_cnt: ", total_cnt, "len(rows): ", len(rows))
        df = pd.DataFrame(rows)
        if not os.path.isfile(file_path):
            df.to_csv(file_path, index=False, header=True)
        else:
            df.to_csv(file_path, index=False, header=False, mode='a')

    # 查询数据结果
    bridge_client.get_bridgedata_provider().query_table_data(req, callback=rows_processor)


if __name__ == "__main__":

    table_id_list = [
        't_ilqzwbks_sleepepisode_system',
        't_ilqzwbks_continuousheartrate_system',
        't_ilqzwbks_dailyheartrate_system',
        't_ilqzwbks_dailyworkout_system',
        't_ilqzwbks_continuousbloodoxygensaturation_system',
        't_ilqzwbks_dailyworkoutdetail_system',
        't_ilqzwbks_dailybloodoxygensaturation_system',
        't_ilqzwbks_continuousrri_system',
        't_ilqzwbks_userfeedback_system',
        't_ilqzwbks_motion_system',
        't_ilqzwbks_rri_system',
        't_ilqzwbks_heartrate_system',
        't_ilqzwbks_bloodoxygensaturation_system',
        't_ilqzwbks_singleworkoutdetail_system',
        't_ilqzwbks_singleworkout_system',
        't_ilqzwbks_ppg_system',
        't_ilqzwbks_acceleration_system',
        't_ilqzwbks_atrialfibrillationmeasureresult_system',
    ]

    try:
        os.makedirs('data/data')
    except:
        ...
    for table_id in table_id_list:
        print(f'#### getting {table_id}')
        table_name = table_id.split('_')[-2]
        get_table_data(table_id, os.path.join('data/data', f'{table_name}.csv'))

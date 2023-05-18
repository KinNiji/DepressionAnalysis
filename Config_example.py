## 文件路径
# 数据文件路径
DATA_FILE_PATH_CONTINUOUS_RAW = "data/data/continuous/raw"
DATA_FILE_PATH_CONTINUOUS_EXTRACTED = "data/data/continuous/extracted"
DATA_FILE_PATH_CONTINUOUS_RESAMPLED = "data/data/continuous/resampled"
# 标签路径
LABEL_FILE_PATH_BEFORE = "data/scale/raw/scale_before.xlsx"
LABEL_FILE_PATH_AFTER = "data/scale/raw/scale_after.xlsx"
LABEL_FILE_PATH_EMA = "data/scale/raw/ema.csv"
LABEL_FILE_PATH = "data/scale"
# app文件路径
APP_DATA_FILE_PATH = "data"

## 数据抽取条件
# 开始时间
BEGIN_TIME_STR = "2021-11-15 00:00:00"
# 结束时间
END_TIME_STR = "2021-12-16 00:00:00"

# 抽取条件 {颗粒度：{文件名：{条件}}}
# region 数据结构详情

## continuousrri
# recordtime    ?
# _index        useless
# rriData       !useful
#   [{'rri': {'unit': 'ms', 'value': 2306}, 'sqi': 0, 'timeFrame': {'timestamp': 1637073168306}},
#    {'rri': {'unit': 'ms', 'value': 974}, 'sqi': 100, 'timeFrame': {'timestamp': 1637073169280}},
#    ...
#   ]
# externalid    !useful
# healthid      useless
# recordschema  always 1
# uniqueid      useless
# uploadtime    ?

## continuousbloodoxygensaturation
#     *recordtime
#     _index
#     *externalid
#     healthid
#     *avgOxygenSaturation
#         {'oxygenSaturation': {'unit': '%', 'value': 99.77},
#          'timeFrame': {'timestamp': 1637002035650}
#         }
#     recordschema
#     uniqueid
#     uploadtime

## continuousheartrate
#     *recordtime
#     _index
#     *externalid
#     healthid
#     recordschema
#     uniqueid
#     *avgHeartRate
#         {'heartRate': {'unit': 'beats/min', 'value': 51},
#          'timeFrame': {'timestamp': 1637013300000}
#         }
#     uploadtime

## dailyworkoutdetail
#     *recordtime
#     _index
#     *externalid
#     healthid
#     recordschema
#     *physicalActivity
#         {'caloriesBurned': {'unit': 'cal', 'value': 2931.0},
#          'climbHeight': {'unit': 'm', 'value': 0.0},
#          'distance': {'unit': 'm', 'value': 54.0},
#          'heartRate': {'unit': 'beats/min', 'value': 116},
#          'activityName': 'walking',
#          'step': {'unit': 'steps', 'value': 79}
#         }
#     uniqueid
#     uploadtime
# endregion

EXTRACT_INFO_COMMON = {

}

EXTRACT_INFO = {
    'continuousrri': {
        'useful_cols': ['recordtime', 'externalid', 'rriData'],
        'processor': {
            'col_name': 'rriData',
            'sampling_unit': 'second',
            'detail_path': {
                'rri': '$.rri.value',
                'sqi': '$.sqi',
                'timestamp': '$.timeFrame.timestamp'
            },
            'detail_unit': {
                'rri': 'ms',
                'sqi': '',
                'timestamp': ''
            }
        },
        'dtype': {
            # 'upload_time': 'int64',
            'external_id': 'int',
            'record_time': 'int64',
            'rri': 'int',
            'sqi': 'int',
        },
        # 'table_name': 'app_data_rri'
    },
    'continuousbloodoxygensaturation': {
        'useful_cols': ['recordtime', 'externalid', 'avgOxygenSaturation'],
        'processor': {
            'col_name': 'avgOxygenSaturation',
            'sampling_unit': 'minute',
            'detail_path': {
                'blood_oxygen_saturation': '$.oxygenSaturation.value'
            },
            'detail_unit': {
                'blood_oxygen_saturation': '%'
            }
        },
        'dtype': {
            # 'upload_time': 'int64',
            'external_id': 'int',
            'record_time': 'int64',
            'blood_oxygen_saturation': 'float',
        },
        # 'table_name': 'app_data_blood_oxygen'
    },
    'continuousheartrate': {
        'useful_cols': ['recordtime', 'externalid', 'avgHeartRate'],
        'processor': {
            'col_name': 'avgHeartRate',
            'sampling_unit': 'minute',
            'detail_path': {
                'heart_rate': '$.heartRate.value'
            },
            'detail_unit': {
                'heart_rate': 'beat'
            }
        },
        'dtype': {
            # 'upload_time': 'int64',
            'external_id': 'int',
            'record_time': 'int64',
            'heart_rate': 'int',
        },
        # 'table_name': 'app_data_heart_rate'
    },
    'dailyworkoutdetail': {
        'useful_cols': ['recordtime', 'externalid', 'physicalActivity'],
        'processor': {
            'col_name': 'physicalActivity',
            'sampling_unit': 'minute',
            'detail_path': {
                'dailyworkoutdetail': '$.caloriesBurned.value',
                'climb_height': '$.climbHeight.value',
                'distance': '$.distance.value',
                'heart_rate_workout': '$.heartRate.value',
                'activity_name': '$.activityName',
                'step': '$.step.value',
            },
            'detail_unit': {
                'calories_burned': 'calorie',
                'climb_height': 'm',
                'distance': 'm',
                'heart_rate_workout': 'beat',
                'activity_name': 'str',
                'step': 'step',
            }
        },
        'dtype': {
            # 'upload_time': 'int64',
            'external_id': 'int',
            'record_time': 'int64',
            'calories_burned': 'float',
            'climb_height': 'float',
            'distance': 'float',
            'heart_rate_workout': 'int',
            'activity_name': 'str',
            'step': 'int',
        },
        # 'table_name': 'app_data_workout'
    }
}

# 抽取后数据类型
OPTIONS = {
    'counting': [
        {'label': '单人统计——通过`时/日/周`对数据进行某人的数据进行聚合', 'value': 'single'},
        {'label': '多人统计——通过不同的图表对数据进行多人的数据进行聚合', 'value': 'multiple'},
    ],
    'file_type': [
        {'label': '抽取数据', 'value': 'extracted_file'},
        {'label': '重采样数据', 'value': 'resampled_file'},
    ],
    'extracted_file': [
        {'label': '持续血氧', 'value': 'continuousbloodoxygensaturation'},
        {'label': '持续心率', 'value': 'continuousheartrate'},
        {'label': '持续RRI', 'value': 'continuousrri'},
        {'label': '运动细节', 'value': 'dailyworkoutdetail'},
    ],
    'resampled_file': [
        {'label': '分钟', 'value': 'minute'},
        {'label': '秒', 'value': 'second'},
    ],
    'continuousbloodoxygensaturation': [
        {'label': '血氧饱和度', 'value': 'blood_oxygen_saturation'}
    ],
    'continuousheartrate': [
        {'label': '心率', 'value': 'heart_rate'}
    ],
    'continuousrri': [
        {'label': 'RRI', 'value': 'rri'}
    ],
    'dailyworkoutdetail': [
        {'label': '消耗卡路里', 'value': 'calories_burned'},
        {'label': '攀爬高度', 'value': 'climb_height'},
        {'label': '距离', 'value': 'distance'},
        {'label': '期间心率', 'value': 'heart_rate_workout'},
        {'label': '步数', 'value': 'step'},
    ],
    'minute': [
        {'label': '血氧饱和度', 'value': 'blood_oxygen_saturation'},
        {'label': '心率', 'value': 'heart_rate'},
        {'label': '消耗卡路里', 'value': 'calories_burned'},
        {'label': '攀爬高度', 'value': 'climb_height'},
        {'label': '距离', 'value': 'distance'},
        {'label': '期间心率', 'value': 'heart_rate_workout'},
        {'label': '步数', 'value': 'step'},
    ],
    'second': [
        {'label': 'RRI', 'value': 'rri'}
    ],
    'single': [
        {'label': '小时', 'value': 'hour'},
        {'label': '日', 'value': 'day'},
        {'label': '周', 'value': 'week'},
    ],
    'multiple': [
        {'label': '小提琴图', 'value': 'violin'},
        {'label': '箱型图', 'value': 'box'},
        {'label': '直方图', 'value': 'hist'},
        {'label': '热图', 'value': 'heat'},
    ]
}


## 数据库配置
# 数据库连接
HOST = "localhost"
PORT = 3306
USER = "root"
PASSWORD = "your_password"
DATABASE = "your_database"

# 数据库密码加密KEY
SECRET_KEY = 'your_key'



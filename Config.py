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


## 数据抽取条件
# 开始时间 
BEGIN_TIME = "2021-11-15 00:00:00"
# 结束时间
END_TIME = "2021-12-16 00:00:00"
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
            'record_time': 'int64',
            'external_id': 'int64',
            'rri': 'int',
            'sqi': 'int',
            'timestamp': 'int64',
        },
        'table_name': 'app_data_rri'
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
            'record_time': 'int64',
            'external_id': 'int64',
            'blood_oxygen_saturation': 'float',
        },
        'table_name': 'app_data_blood_oxygen'
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
            'record_time': 'int64',
            'external_id': 'int64',
            'heart_rate': 'int',
        },
        'table_name': 'app_data_heart_rate'
    },
    'dailyworkoutdetail': {
        'useful_cols': ['recordtime', 'externalid', 'physicalActivity'],
        'processor': {
            'col_name': 'physicalActivity',
            'sampling_unit': 'minute',
            'detail_path': {
                'calories_burned': '$.caloriesBurned.value',
                'climb_height': '$.climbHeight.value',
                'distance': '$.distance.value',
                'heart_rate': '$.heartRate.value',
                'activity_name': '$.activityName',
                'step': '$.step.value',
            },
            'detail_unit': {
                'calories_burned': 'calorie',
                'climb_height': 'm',
                'distance': 'm',
                'heart_rate': 'beat',
                'activity_name': '',
                'step': 'step',
            }
        },
        'dtype': {
            'record_time': 'int64',
            'external_id': 'int64',
            'calories_burned': 'float',
            'climb_height': 'float',
            'distance': 'float',
            'heart_rate': 'int',
            'activity_name': 'str',
            'step': 'int',
        },
        'table_name': 'app_data_workout'
    }
}

# 抽取后数据类型
EXTRACTED_DTYPE = {
    'continuousrri': {
        'rri': 'int',
        'sqi': 'int',
        'timestamp': 'int64',
    },
    'continuousbloodoxygensaturation': {
        'oxygenSaturation(%)': 'float',
        'timestamp': 'int64'
    },
    'continuousheartrate': {
        'heartRate(beats/min)': 'int',
        'timestamp': 'int64'
    },
    'dailyworkoutdetail': {
        'caloriesBurned(cal)': 'float',
        'climbHeight(m)': 'float',
        'distance(m)': 'float',
        'heartRate(beats/min)': 'int',
        'activityName': 'str',
        'step(steps)': 'int',
        'timestamp': 'int64',
    }
}


## 数据库配置
# 数据库连接
HOST = "localhost"
PORT = 3307
USER = "root"
PASSWORD = "123456"
DATABASE = "depression"

# 数据库密码加密KEY
SECRET_KEY = '&depression_2023#'



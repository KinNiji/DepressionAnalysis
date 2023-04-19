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


EXTRACT_INFO = {
    "second": {
        'continuousrri': {
            'useful_cols': ['recordtime', 'externalid', 'rriData'],
            'processer': {
                'col_name': 'rriData',
                'df_col_name': ['rri(ms)', 'sqi', 'timestamp'],
                'df_col_path': [
                    ['rri', 'value'],
                    ['sqi'],
                    ['timeFrame', 'timestamp']
                ]
            }
        }
    },
    "minute": {
        'continuousbloodoxygensaturation': {
            'useful_cols': ['recordtime', 'externalid', 'avgOxygenSaturation'],
            'processer': {
                'col_name': 'avgOxygenSaturation',
                'df_col_name': ['oxygenSaturation(%)'],
                'df_col_path': [
                    ['oxygenSaturation', 'value']
                ]
            }
        },
        'continuousheartrate': {
            'useful_cols': ['recordtime', 'externalid', 'avgHeartRate'],
            'processer': {
                'col_name': 'avgHeartRate',
                'df_col_name': ['heartRate(beats/min)'],
                'df_col_path': [
                    ['heartRate', 'value']
                ]
            }
        },
        'dailyworkoutdetail': {
            'useful_cols': ['recordtime', 'externalid', 'physicalActivity'],
            'processer': {
                'col_name': 'physicalActivity',
                'df_col_name': ['caloriesBurned(cal)', 'climbHeight(m)', 'distance(m)', 'heartRate(beats/min)',
                                'activityName', 'step(steps)'],
                'df_col_path': [
                    ['caloriesBurned', 'value'],
                    ['climbHeight', 'value'],
                    ['distance', 'value'],
                    ['heartRate', 'value'],
                    ['activityName'],
                    ['step', 'value']
                ],
            }
        }
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
PORT = 3306
USER = "root"
PASSWORD = "your_password"
DATABASE = "your_database"

# 数据库密码加密KEY
SECRET_KEY = 'your_key'



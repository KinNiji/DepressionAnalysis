import time
import datetime
import logging
import pandas as pd


# region 时间格式转换方法
def time2timestamp(time_obj: datetime.datetime) -> int:
    return int(time.mktime(time_obj.timetuple()) * 1000)


def timestamp2time(timestamp):
    if len(str(timestamp)) == 13:
        timestamp = int(timestamp) / 1000
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def timestr2time(timestr: str) -> datetime.datetime:
    return datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")


def timestr2timestamp(timestr: str) -> int:
    return time2timestamp(timestr2time(timestr))


# endregion

# region 异常值处理
def abnormal_processing(df: pd.DataFrame, col_name: str, mask_fun, fill_fun=None) -> pd.DataFrame:
    df_copy = mask_fun(df.copy(), col_name)
    # print('masked line count:', df_copy[col_name].isna().sum())
    if fill_fun:
        return fill_fun(df_copy, col_name)
    else:
        return df_copy

def mask_low_sqi(df, col_name):
    df[col_name] = df[col_name].mask(df['sqi'] == '0')
    return df

def mask_over_3std(df, col_name):
    df[col_name] = df[col_name].mask((df[col_name] - df[col_name].mean()) >= 3 * df[col_name].std())
    return df

def fill_nearest(df, col_name):
    df[col_name] = df[col_name].interpolate(method='nearest')
    return df


def linear_interpolation(X, x1, y1, x2, y2):
    return y1 + (y2 - y1) * (X - x1) / (x2 - x1)
# endregion



class Logger(object):
    def __init__(self, file_name='app'):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        # handler = logging.StreamHandler()
        handler = logging.FileHandler(f'logs/{file_name}.log', mode='a+')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
        # sys.exit(1)

    def critical(self, msg):
        self.logger.critical(msg)
        # sys.exit(1)


if __name__ == '__main__':
    Logger().debug('this is an debug')
    Logger().info('this is an info')
    Logger().warning('this is an warning')
    Logger().error('this is an error')
    Logger().critical('this is an critical')

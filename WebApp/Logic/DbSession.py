import pymysql

from Utils import Logger


# 兼容MySQLdb
# pymysql.install_as_MySQLdb()


class DbSession(object):
    # 初始化对象，产生一个mysql连接
    def __init__(self, host, user, password, database, port, charset='utf8'):
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._charset = charset
        self._conn = None
        try:
            self._conn = pymysql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._database,
                port=self._port,
                charset=self._charset,
                autocommit=True
            )
        except Exception as err:
            format_err = f"{self._host} session init failed: {err}"
            Logger().error(format_err)
            raise Exception(format_err)

    # 调用with方法的入口
    def __enter__(self):
        return self

    # 调用with方法结束时启动
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    @staticmethod
    def list2tuple_str(value_list):
        tuple_str = ''
        for i in value_list:
            tuple_str += (i + ', ')
        return '({})'.format(tuple_str[:-2])

    def quick_insert(self, table_name: str, data: dict, many=False, ignore=False) -> int:
        """
        通过表名和字典插入数据
        :param table_name: 数据库表名
        :param data: 字典，键为数据库表的列名，值为这一列值的列表
        :param many: 是否插入大量数据
        :param ignore: 是否忽略数据库警告
        :return: int 返回影响的行数
        """
        cursor = self._conn.cursor()
        sql = f"insert {'ignore' if ignore else ''} into {table_name} {self.list2tuple_str(list(data.keys()))} " \
              f"values {self.list2tuple_str(['%s' for _ in range(len(data.keys()))])}"
        try:
            if many:
                row_count = cursor.executemany(sql, [data[_] for _ in data.keys()])
            else:
                row_count = cursor.execute(sql, list(data.values()))
        except Exception as err:
            format_err = f"{self._host} insert failed: {err} - {sql}"
            Logger().error(format_err)
            raise Exception(format_err)
        finally:
            cursor.close()
        return row_count

    def execute(self, sql: str, many=False, *args) -> int:
        """
        执行一条sql语句
        :param sql: sql语句
        :param many: 是否执行大量语句
        :param args: 参数
        :return: int 返回影响的行数
        """
        cursor = self._conn.cursor()
        try:
            if many:
                row_count = cursor.executemany(sql, args)
            else:
                row_count = cursor.execute(sql, args)
        except Exception as err:
            format_err = f"{self._host} execute failed: {err} - {sql}"
            Logger().error(format_err)
            raise Exception(format_err)
        finally:
            cursor.close()
        return row_count

    def insert(self, sql: str, many=False, *args) -> int:
        """
        执行一条插入sql语句
        :param sql: sql语句
        :param many: 是否执行大量语句
        :param args: 参数
        :return: int 返回影响的行数
        """
        return self.execute(sql, many, *args)

    def delete(self, sql: str, many=False, *args) -> int:
        """
        执行一条删除sql语句
        :param sql: sql语句
        :param many: 是否执行大量语句
        :param args: 参数
        :return: int 返回影响的行数
        """
        return self.execute(sql, many, *args)

    def update(self, sql: str, many=False, *args) -> int:
        """
        执行一条更新sql语句
        :param sql: sql语句
        :param many: 是否执行大量语句
        :param args: 参数
        :return: int 返回影响的行数
        """
        return self.execute(sql, many, *args)

    def select(self, sql: str, *args) -> list:
        """
        执行一条查询sql语句
        :param sql: sql语句
        :param args: 参数
        :return: list 查询的结果
        """
        cursor = self._conn.cursor()
        try:
            result = []
            if cursor.execute(sql, list(args)):
                result = cursor.fetchall()
        except Exception as err:
            format_err = f"{self._host} select failed: {err} - {sql}"
            Logger().error(format_err)
            raise Exception(format_err)
        finally:
            cursor.close()
        return result

    def get_sql(self, sql_id):
        result = self.select('SELECT * FROM COM_SQL WHERE ID = %s', sql_id)
        if result:
            return result[0][2]
        else:
            format_err = f"get sql id failed:  - {sql_id}"
            Logger().error(format_err)
            raise Exception(format_err)


# if __name__ == "__main__":
#     with DbSession(HOST="xxxx", USER="xxxx", PASSWORD="xxxx", DATABASE="xxxx") as session:
#         sql_insert_many = 'insert into test.test (name) values (%s)'
#         value_list = ["chen", "zc"]
#
#         row = session.change_many(sql_insert_many, value_list)
#
#         r1 = session.sql("select * from test.test")
#         print(r1)
#
#         row2 = session.change(f"insert into test (name) values ('zhang')")
#         print(row2)
#
#         r2, row3 = session.sql("select * from test.test")
#         print(r2)

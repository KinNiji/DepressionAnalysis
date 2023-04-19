import hashlib

from WebApp.Logic.DbSession import DbSession
import Config

mysql = DbSession(Config.HOST, Config.USER, Config.PASSWORD, Config.DATABASE, Config.PORT)


class User:
    def __init__(self):
        self.user_id = None
        self.user_name = None
        self.email = None
        self.role = None
        self.is_admin = None

    @staticmethod
    def encrypt_sha1(password: str):
        return hashlib.sha1(f'$password=${password}$key=${Config.SECRET_KEY}'.encode('utf-8')).digest()

    def login_check(self, email, password):
        sql = mysql.get_sql('App.Login.LoginCheck')
        result = mysql.select(sql, email, self.encrypt_sha1(password))
        if result:
            result = result[0]
            self.user_id = result[0]
            self.user_name = result[1] if result[1] else 'user_' + result[0]
            self.email = result[2]
            self.role = result[3]
            self.is_admin = result[4]
            return True
        else:
            return False

    @staticmethod
    def user_exist(user_name):
        sql = mysql.get_sql('App.Login.UserExist')
        result = mysql.select(sql, user_name)
        if result and result[0][0]:
            return True
        else:
            return False

    def user_create(self, user_name, email, password, role=None, is_admin=False):
        if not self.user_exist(user_name):
            return mysql.quick_insert('app_user',
                                      {'user_name': user_name,
                                       'email': email,
                                       'password': self.encrypt_sha1(password),
                                       'role': 'user' if role is None else role,
                                       'is_admin': is_admin})
        return False

    def update_password(self, user_name, password):
        sql = mysql.get_sql('App.Login.UpdatePassword')
        return mysql.update(sql, self.encrypt_sha1(password), user_name)

"""
    dict 所有数据库操作
    提供数据库连接,以及功能交互
"""
import pymysql
import hashlib
salt = b"*#06#" # 加密专用盐


def encryption(passwd):
    # 对密码进行加密处理
    hash = hashlib.md5(salt)
    hash.update(passwd.encode())
    passwd = hash.hexdigest()  # 获取存储密码
    return passwd

class DataBase:
    def __init__(self):
        # 连接数据库
        self.db = pymysql.connect(host = "localhost",
                                  port = 3306,
                                  user = "root",
                                  passwd = "123456",
                                  database = "dict",
                                  charset = "utf8")
        # 创建游标 (操作数据库语句,获取查询结果)
        self.cur = self.db.cursor()

    def close(self):
        # 关闭游标和数据库
        self.cur.close()
        self.db.close()

    def register(self,name,passwd):
        sql = "select * from user where name = '%s'"%name
        self.cur.execute(sql)
        resule = self.cur.fetchone()
        if resule:
            return True

        # 加密
        passwd = encryption(passwd)

        # 插入用户
        try:
            sql = "insert into user (name,passwd) values (%s,%s)"
            self.cur.execute(sql,[name,passwd])
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    # 登录
    def login(self,name,passwd):
        passwd = encryption(passwd) # 加密转换
        sql = "select * from user where name = %s and passwd = %s"
        self.cur.execute(sql,[name,passwd])
        result = self.cur.fetchone()
        if result:
            return True
        else:
            return False

    def query(self,word):
        sql = "select mean from words where word = '%s'"%word
        self.cur.execute(sql)
        result = self.cur.fetchone()
        if result:
            return result[0]

    def insert_history(self,name,word):
        sql = "insert into hist (name,word) values (%s,%s)"
        try:
            self.cur.execute(sql,[name,word])
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)

        self.read_history(name)

    def read_history(self, name):
        sql = "select name,word,time from hist where name = '%s' order by time desc limit 10"%name
        self.cur.execute(sql)
        result = self.cur.fetchall()
        if result:
            return result



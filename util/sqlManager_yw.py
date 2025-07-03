import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
path = os.path.dirname(sys.path[0])
if path not in sys.path:
    sys.path.append(path)
import pymysql
from config_helper import IniFileHelper
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from util.logutil import *

class SQLManagers(object):

    __pool = None

    def __init__(self,dbName="",type=1):  # 实例化后自动执行此函数
        self.config = IniFileHelper(curPath + '/config.ini')
        self.host = self.config.get_val('DBClientInfo_yw.host')
        self.port = self.config.get_val('DBClientInfo_yw.port')
        self.pwd = self.config.get_val('DBClientInfo_yw.password')
        self.user = self.config.get_val('DBClientInfo_yw.user')
        self.db = dbName
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        if type==1:
            self.conn = self.connect()
            self.cursor = self.conn.cursor()
        else:
            self.conn = self.connect_dict()
            self.cursor = self.conn.cursor()

    def connect(self):  # 此时进入数据库，游标也已经就绪
        if SQLManagers.__pool is None:
            POOL = PooledDB(
                creator=pymysql,
                mincached=3,
                maxcached=30,
                host=self.host,
                port=int(
                    self.port),
                user=self.user,
                passwd=self.pwd,
                db=self.db,
                connect_timeout=60,
                blocking=True,
                use_unicode=True,
                charset="utf8mb4",
                autocommit=True)

        return POOL.connection()

    def connect_dict(self):  # 此时进入数据库，游标也已经就绪
        if SQLManagers.__pool is None:
            POOL = PooledDB(
                creator=pymysql,
                mincached=3,
                maxcached=30,
                host=self.host,
                port=int(
                    self.port),
                user=self.user,
                passwd=self.pwd,
                db=self.db,
                blocking=True,
                connect_timeout=60,
                use_unicode=True,
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=True)

        return POOL.connection()

    def select_data(self, sql):
        resultTuple = None
        self.cursor.execute(sql)
        resultTuple = self.cursor.fetchall()
        return resultTuple

    def update_data(self, sql):
        resultDict = {}
        self.cursor.execute(sql)
        resultDict["rowCnt"] = self.cursor.rowcount
        return resultDict

    # 数据插入，返回主键Id
    def insert_data(self, sql):
        resultDict = {}
        self.cursor.execute(sql)
        rowId = int(self.cursor.lastrowid)
        resultDict["rowCnt"] = self.cursor.rowcount
        resultDict["rowId"] = rowId
        return resultDict

    def run(self, sql, args=None):
        self.cursor.execute(sql, args)

    # 批量插入数据, 第一个参数是sql语句， 第二个参数数据类型：元祖/列表
    def save_batch_data(self, sql, val):
        resultDict = {}
        self.cursor.executemany(sql, val)
        resultDict["rowCnt"] = self.cursor.rowcount
        return resultDict

    def delete(self, sql, val):
        """
        插入数据
        :param conn: 连接mysql
        :param sql: sql 语句
        :param val: 提交的数据
        :return:
        """

        self.cursor.execute(sql, val)
        self.conn.rollback()

    def insert_one(self, sql, val):
        """
        插入数据
        :param conn: 连接mysql
        :param sql: sql 语句
        :param val: 提交的数据
        :return:
        """

        self.cursor.execute(sql, val)
        self.conn.rollback()




    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

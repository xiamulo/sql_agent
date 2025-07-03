from util.sqlManager import SQLManagers
from util.logutil import *


def delete_apid(sql,*args):
    """ 删除某个平台数据 """
    with SQLManagers("csgd_yw") as db:
        try:
            db.delete(sql,args)
        except Exception as result:
            logger.debug(sql,args)
            logger.error('插入失败：%s' % (result))


def select_data_list(sql):
    """查询 sql"""
    while True:
        try:
            with SQLManagers("csgd_yw",2) as db:
                result = db.select_data(sql)
                return result
        except Exception as ex:
            logger.error("查询操作出错")
    return result

def select_data(sql):
    """查询 sql"""
    while True:
        try:
            with SQLManagers("csgd_yw") as db:
                try:
                    result = db.select_data(sql)
                    return result
                except Exception as ex:
                    logger.error("查询操作出错")
        except Exception as e:
            print(e)

    return result

def update_data(sql):
    while True:
        try:
            with SQLManagers("csgd_yw") as db:
                try:
                    db.update_data(sql)
                    break
                except Exception as result:
                    logger.debug(sql)
                    logger.error('插入失败：%s' % (result))
        except Exception as e:
            print(e)

def insert_data(sql,*args):
    while True:
        try:
            with SQLManagers("csgd_yw") as db:
                db.run(sql,args)
            break
        except Exception as e:
            print(e)
            break

def insert_data_zb(sql,*args):
    with SQLManagers("csgd") as db:
        db.run(sql,args)
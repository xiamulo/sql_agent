import sys
import os
from util.sqlManager import SQLManagers
from util.logutil import *
import datetime

def delete_apid(sql,*args):
    """ 删除某个平台数据 """
    with SQLManagers("csgd") as db:
        try:
            db.delete(sql,args)
        except Exception as result:
            logger.debug(sql,args)
            logger.error('插入失败：%s' % (result))

def select_data_list(sql):
    """查询 sql"""
    with SQLManagers("wl_demo",2) as db:
        while True:
            try:
                result = db.select_data(sql)
                result = [{k: format_datetime(v) for k, v in item.items()} for item in result]
                break
            except Exception as ex:
                return str(ex)

    return result


def select_data_sql(sql):
    """查询 sql"""
    while True:
        with SQLManagers("llm_word",2) as db:
            try:
                result = db.select_data(sql)
                break
            except Exception as ex:
                logger.error("查询操作出错")

    return result
def format_datetime(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(value)
def select_data_zb(sql):
    """查询 sql"""
    while True:
        try:
            with SQLManagers("langchain_fc",2) as db:
                while True:
                    try:
                        result = db.select_data(sql)
                        return result
                    except Exception as ex:
                        logger.error("查询操作出错")
        except Exception as e:
            print(e)


def select_data(sql):
    """查询 sql"""
    while True:
        try:
            with SQLManagers("langchain_fc") as db:
                while True:
                    try:
                        result = db.select_data(sql)
                        return result
                    except Exception as ex:
                        logger.error("查询操作出错")
        except Exception as e:
            print(e)

def update_data(sql):
    with SQLManagers("llm_word") as db:
        try:
            db.update_data(sql)
        except Exception as result:
            logger.debug(sql)
            logger.error('插入失败：%s' % (result))

def update_data_zb(sql):
    with SQLManagers("langchain_fc") as db:
        try:
            db.update_data(sql)
        except Exception as result:
            logger.debug(sql)
            logger.error('插入失败：%s' % (result))




def get_table_list():
    with SQLManagers("wl_test") as db:
        database_names =db.get_tables()
    return database_names

def insert_data_zb(sql,*args):
    while True:
        try:
            with SQLManagers("langchain_fc") as db:
                db.run(sql,args)
            break
        except Exception as e:
            if "Duplicate entry" in str(e):
                break
            print(e)


def insert_data(sql,*args):
    while True:
        try:
            with SQLManagers("llm_word") as db:
                db.run(sql,args)
            break
        except Exception as e:
            if "Duplicate entry" in str(e):
                break
            print(e)

def get_table_info(db_name):
    while True:
        try:
            strs=""
            table_list=[]
            f_names=[]
            with SQLManagers(db_name) as db:
                tables =db.list_table()  # 获取所有表，返回的是一个可迭代对象
                print(tables)
                for table in tables:
                    strs="表名："+table+" 字段名："
                    col_names = db.list_col(table,db_name)
                    st=""
                    for col in col_names:
                        f_names.append(col[0])
                        if col[1]=="":
                            st+=","+col[0]
                        else:
                            st += "," + col[0]+" 注释：("+col[1]+")"
                    strs=strs+st
                    table_list.append(strs)
            break
        except Exception as e:
            print(e)
    return table_list,f_names



# if __name__ == '__main__':


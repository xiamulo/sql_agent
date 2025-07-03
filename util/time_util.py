import time
from datetime import date, datetime, timedelta

#十位时间戳转时间
def get_time_10(date):
    timeArray = time.localtime(int(date))
    article_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return article_date


def get_time_stamp13():
    # 生成13时间戳  eg:1540281250399895
    datetime_now = datetime.now()

    # 10位，时间点相当于从UNIX TIME的纪元时间开始的当年时间编号
    date_stamp = str(int(time.mktime(datetime_now.timetuple())))

    # 3位，微秒
    data_microsecond = str("%06d" % datetime_now.microsecond)[0:3]

    date_stamp = date_stamp + data_microsecond
    return int(date_stamp)

def get_time_13(timeNum):
    timeStamp = float(timeNum/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


#时间对比算出天数
def Caltime(date1, date2):
    # %Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
    #date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    #date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = time.strptime(date1, "%Y-%m-%d %H:%M:%S")
    date2 = time.strptime(date2, "%Y-%m-%d %H:%M:%S")
    # 根据上面需要计算日期还是日期时间，来确定需要几个数组段。下标0表示年，小标1表示月，依次类推...
    # date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    # date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    date1 = datetime(date1[0], date1[1], date1[2])
    date2 = datetime(date2[0], date2[1], date2[2])
    # 返回两个变量相差的值，就是相差天数
    return (date2 - date1)

#gmt转北京时间
def gmt_bjtime(publish_time):
    GMT_FORMAT = '%a %b %d  %H:%M:%S +0800 %Y'
    publish_time = datetime.strptime(publish_time, GMT_FORMAT)
    publish_time = datetime.strftime(publish_time,"%Y-%m-%d %H:%M:%S")
    return publish_time



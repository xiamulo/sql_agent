import datetime
import json
import random
import re
import time
import sys
import os
import uuid
curPath = os.path.dirname(os.path.dirname(os.getcwd()))
path = os.path.dirname(sys.path[0])
if path not in sys.path:
    sys.path.append(path)
import pymysql
import base64
import requests
import cv2
import pathlib
import paramiko  # 用于调用scp命令
from scp import SCPClient
from faker import Factory
from util.logutil import *






def scp_file(local_path, filetype):
    print("文件开始成功")

    host = "139.196.58.220"  # 服务器ip地址
    port = 22  # 端口号
    username = "root"  # ssh 用户名
    password = "Next1995!!!"  # 密码
    remote_path = "/root/html/Csbtv/tmpfile/" + filetype
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, username, password)
    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
    try:
        scpclient.put(local_path, remote_path)
    except FileNotFoundError as e:
        logger.debug(e)
        logger.debug("系统找不到指定文件" + local_path)
    else:
        logger.debug("文件上传成功")
    ssh_client.close()


def photo_title(content):
    image_base64 = str(base64.b64encode(content), encoding='utf-8')
    data = {"img": image_base64}
    # data = json.dumps(data)
    headers = {
        "Content-Type": "application/json"
    }
    url = "http://114.115.168.204:6066/api/tr-run/"
    #url = "https://www.paddlepaddle.org.cn/paddlehub-api/image_classification/chinese_ocr_db_crnn_mobile"
    while True:
        try:
            #proxies = get_proxy_user(self.ip_server)
            res = requests.post(url=url, data=data)
            if res.status_code==200:
                break
        except Exception as e:
            print(e)
    result = res.json()
    return result



def sub_wangyi(docId, title):
    pic_url = "http://139.196.58.220/Csbtv/tmpfile/img/{}.jpg".format(docId)
    url = "http://139.196.58.220/Csbtv/tmpfile/vedio/{}.mp4".format(docId)

    body = {
        "access_token": "d45326cb47bbb524d7767940ef4a06b0",
        "title": title,
        "url": url,
        "pic_url": pic_url,
        "isoriginal": 1,
        "category_id": 1,
        "tag": "正能量,新闻现场,社会,社会百态,奇闻趣事"
    }

    # 上发三次
    for i in range(3):
        try:
            wy_url = "http://mp.163.com/wemedia/video/status/api/oauth2/publish.do"
            response = requests.post(url=wy_url, data=body)
            result = response.json()
            result["id"] = docId
            result["title"] = title
            break
        except:
            result = {
                "errno": 1,
                "title": "上发失败，网易端出现问题"
            }
            pass
    if result.get("code") == 1:
        logger.debug("\n{}--【网易号】-数据同步成功：\n{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result))
    else:
        logger.debug("\n{}--【网易号】-数据同步失败：\n{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result))


def sub_baidu(docId, title):
    cover_images = "http://139.196.58.220/Csbtv/tmpfile/img/{}.jpg".format(docId)
    video_url = "http://139.196.58.220/Csbtv/tmpfile/vedio/{}.mp4".format(docId)

    body = {
        "app_id": "1728529891142878",
        "app_token": "0bfc3c059e15002dc91e258d029fd549",
        "title": title,
        "video_url": video_url,
        "cover_images": cover_images,
        "is_original": 1,
        "tag": "正能量,新闻现场,社会,搞笑,社会百态,奇闻趣事"
    }
    # 上发三次
    for i in range(3):
        try:
            bd_url = "https://baijiahao.baidu.com/builderinner/open/resource/video/publish"
            response = requests.post(url=bd_url, data=json.dumps(body))
            result = response.json()
            result["id"] = docId
            result["title"] = title
            break
        except:
            result = {
                "errno": 1,
                "title": "上发失败，百度端出现问题"
            }
            pass
    if result.get("errno") == 0:
        logger.debug("\n{}--【百家号】数据同步成功：\n{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result))
    else:
        logger.debug("\n{}--【百家号】数据同步失败：\n{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result))


def hmac_sha256(ran_str, timestamp, appkey):
    import hashlib
    import hmac
    signature = hmac.new(appkey.encode("utf-8"), (ran_str +
                                                  timestamp).encode("utf-8"), digestmod=hashlib.sha256).digest()
    return signature.hex()


def sub_huawei(docId, title, publish_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    hw_url = "https://browserfeedss2s-drcn.cloud.huawei.com.cn/contentgateway/video/batch_publish_content?version=v1.0"
    hw_appkey = "nL1Ni76Z6nv0zMadaygME3hyfNr+EivQ4zqrEVwYTFk"
    thumbnail = "http://139.196.58.220/Csbtv/tmpfile/img/{}.jpg".format(docId)
    vedio_url = "http://139.196.58.220/Csbtv/tmpfile/vedio/{}.mp4".format(docId)

    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    secretkey = hmac_sha256(nonce, timestamp, hw_appkey)
    body = {
        "cpId": "1198",
        "secretkey": secretkey,
        "nonce": nonce,
        "timestamp": timestamp,
        "contentList": [
            {
                "docId": docId,
                "thumbnail": [
                    thumbnail
                ],
                "title": title,
                "summary": title,
                "url": vedio_url,
                "pubDate": publish_date,
                "source": {
                    "sourceID": "新知速报",
                    "sourceText": "新知速报"
                },
                "videoUrl": vedio_url,
                "category": {
                    "topcatText": "社会",
                },
                "impEX": [
                    {"key": "contentIpAddress", "value": "218.76.13.82"}
                ]
            }
        ]
    }

    hw_url = "https://browserfeedss2s-drcn.cloud.huawei.com.cn/contentgateway/video/batch_publish_content?version=v1.0"
    response = requests.post(url=hw_url, data=json.dumps(body))
    result = response.json()
    result["id"] = docId
    result["title"] = title
    if result.get("code") == '0':
        logger.debug(body)
        logger.debug("{}--【华为信息流】数据同步成功：\n{}".format(publish_date, result))
    else:
        logger.debug("{}--【华为信息流】数据同步失败：\n{}".format(publish_date, result))





# if __name__ == "__main__":
#
#     bd_url = "https://baijiahao.baidu.com/builderinner/open/resource/video/publish"
#     wy_url = "http://mp.163.com/wemedia/video/status/api/oauth2/publish.do"
#     hw_url = "https://browserfeedss2s-drcn.cloud.huawei.com.cn/contentgateway/video/batch_publish_content?version=v1.0"
#     hw_appkey = "nL1Ni76Z6nv0zMadaygME3hyfNr+EivQ4zqrEVwYTFk"
#
#     # 传文件 success_file[0]为视频文件地址，success_file[1]为图片地址
#     scp_file(success_file[0], "vedio")
#     scp_file(success_file[1], "img")
#
#     # 上发  id为.mp4文件前缀
#     sub_huawei(id, title)
#     sub_baidu(id, title)
#     sub_wangyi(id, title)
    

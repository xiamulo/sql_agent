import requests
import json
from requests_toolbelt import MultipartEncoder
import time
from requests_html import HTMLSession
from pysmx.crypto import hashlib
from urllib.parse import quote,unquote
from hashlib import md5, sha1
import base64
import os
import uuid
from moviepy.editor import *
from util.sqlutil import select_data
import random

class sph_video():


    def __init__(self,file_name,mp4_path,title,photo_path,photo_path_name,sub_account):
        self.session=HTMLSession()
        self.title=title
        self.file_name=file_name
        self.file_size = str(os.path.getsize(mp4_path))
        self.photo_file_size = str(os.path.getsize(photo_path))
        self.photo_path=photo_path
        self.mp4_path=mp4_path
        self.video_url=""
        self.task_id = str(uuid.uuid1())
        self.sub_account=sub_account
        if sub_account==1:
            self.uin = "2367948576"
            sql = """select ck from ck_info where host='channels.weixin.qq.com'"""
            result = select_data(sql)
        elif sub_account==3:
            self.uin="2026588862"
            sql = """select ck from ck_info6 where host='channels.weixin1.qq.com'"""
            result = select_data(sql)
        elif sub_account==4:
            self.uin="3042978874"
            sql = """select ck from ck_info6 where host='channels.weixin2.qq.com'"""
            result = select_data(sql)
        self.ag="apptype=251&filetype=20302&weixinnum="+self.uin+"&filekey="+self.file_name+"&filesize="+self.file_size+"&taskid="+self.task_id+"&scene=0"
        self.photo_ag="apptype=251&filetype=20304&weixinnum="+self.uin+"&filekey="+photo_path_name+"&filesize="+self.photo_file_size+"&taskid="+self.task_id+"&scene=0"

        self.cookie = result[0][0]
        self.Authorization = self.get_auth(self.cookie)
        self.raw_key='CAESIMl5fyTmvNiqDNoTVsUiBrxCdPyYHUiLBOEOs2W9Owkt'
        self.find_user_id='v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder'

    def get_auth(self,cookie):
        headers = {

            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-WECHAT-UIN": "0000000000",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            "Cookie":self.cookie

        }
        url="https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/helper/helper_upload_params"
        count =0
        while True:
            try:
                count=count+1
                if count>6:
                    return None
                res = requests.post(url,headers=headers,timeout=8)
                if res.status_code==201:
                    break
            except Exception as e:
                print(e)
        try:
            auth=res.json().get('data').get("authKey")
        except Exception as e:
            return None
        return auth


    def getBigFileMD5(self, maxbuf):
        md5().update(maxbuf)
        hash = md5().hexdigest()
        return str(hash).upper()

    def upload(self,chunk, flen, count,url,upload_id,types=1):
        content_md5=self.getBigFileMD5(chunk)
        if types==2:
            headers = {
                'Content-Length': str(len(chunk)),
                "Content-MD5": content_md5,
                "X-Arguments": self.ag,
                "Authorization": self.Authorization,
                "Content-Type": "application/octet-stream",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            }
        else:
            headers = {
                'Content-Length': str(len(chunk)),
                "Content-MD5": content_md5,
                "X-Arguments": self.photo_ag,
                "Authorization": self.Authorization,
                "Content-Type": "application/octet-stream",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            }
        while True:
            try:
                res=self.session.post(url,
                         data=chunk, headers=headers, stream=True,verify=False)
                if res.status_code==200:
                    break
            except Exception as e:
                print(e)

        res = res.json()
        ETag=res.get('ETag')
        return ETag

    def upload_check(self,push_shas, upload_id,video_width,video_height):
        times=str(int(time.time()*1000))
        headers = {
            "X-Arguments": self.ag,
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
        }
        data={"TransFlag":"0_0","PartInfo":[]}
        count=0
        finishParts = []
        for sha in push_shas:
            count = count + 1
            sha_data = {"PartNumber": count, "ETag": sha}
            finishParts.append(sha_data)
        data["PartInfo"]=finishParts
        url="https://finder-assistant.mp.video.tencent-cloud.com/completepartuploaddfs?UploadID="+upload_id
        while True:
            try:
                res = self.session.post(url,headers=headers,json=data,timeout=8)
                if res.status_code==200:
                    break
            except Exception as e:
                print(e)
        res = res.json()
        d_url=res.get('DownloadURL')
        d_url=d_url.replace("http://wxapp.tc.qq.com","https://finder.video.qq.com")
        self.video_url=d_url
        url="https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/post/post_clip_video"
        data={"url":"https://finder.video.qq.com/251/20302/stodownload?adaptivelytrans=0&bizid=1023&dotrans=2991&encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzR2voP8GCGRxOClaQV3hycSoT89HTTeMPtPuKSt74ibZqpyEA78AVh8NxovKhAPCg73UDb2mrEfSpZUVhgqufdXQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8Q51OfEbckhyjTjuSkHtLZ0tW0UAibkGYwu0ib2BKCTt0hBuRcnHFpOwLvjksDRPeTyg","timeStart":0,"cropDuration":0,"height":960,"width":560,"x":0,"y":0,"targetWidth":560,"targetHeight":960,"type":4,"timestamp":"1652238426622","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":"","scene":1}
        data["url"]=d_url
        data["timestamp"]=times
        data['height']=video_height
        data['width']=video_width
        data['targetWidth']=video_width
        data['targetHeight']=video_height
        data['rawKeyBuff']=self.raw_key
        data['_log_finder_id']=self.find_user_id
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-WECHAT-UIN": self.uin,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            "Cookie": self.cookie
        }
        while True:
            try:
                res = self.session.post(url, headers=headers, json=data, timeout=18)
                if res.status_code == 201:
                    break
            except Exception as e:
                print(e)
        res = res.json()
        try:
            c_key=res.get('data').get('clipKey')
            d_key = res.get('data').get('draftId')
            return c_key,d_key
        except Exception as e:
            return "",""


    def upload_photo(self,photo_path):
        # if "root" in photo_path:
        #     return photo_path
        photo_size=str(os.path.getsize(photo_path))
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.Authorization,
            "Content-MD5": "null",
            "X-Arguments": self.photo_ag,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
        }
        sizes =int(self.photo_file_size)
        y_size = 0
        BlockPartLength = []
        count = 1
        if sizes > 8388608:
            while True:
                y_size = y_size + 8388608
                if sizes <= 8388608:
                    BlockPartLength.append(int(sizes))
                    break
                else:
                    BlockPartLength.append(y_size)
                sizes = sizes - 8388608
                count = count + 1
        else:
            BlockPartLength = [sizes]
        data = {"BlockSum": 9,
                "BlockPartLength": [8388608, 16777216, 25165824, 33554432, 41943040, 50331648, 58720256, 67108864,
                                    71216055]}
        data["BlockSum"] = count
        data["BlockPartLength"] = BlockPartLength
        url = "https://finder-assistant.mp.video.tencent-cloud.com/applyuploaddfs"
        while True:
            try:
                res = self.session.put(url, headers=headers, json=data, timeout=6)
                if res.status_code == 200:
                    break
            except Exception as e:
                print(e)
        res = res.json()
        upload_id = res.get('UploadID')
        print(upload_id)
        with open(self.photo_path, 'rb') as f:
            f.seek(0, 2)
            flen = f.tell()
            f.seek(0, 0)
            i = 0
            count = 0
            push_shas = []
            while True:
                count = count + 1
                chunk = f.read(8388608)
                if not chunk:
                    break
                url = "https://finder-assistant.mp.video.tencent-cloud.com/uploadpartdfs?PartNumber=" + str(
                    count) + "&UploadID=" + upload_id
                types=2
                ETag = self.upload(chunk, flen, count, url, upload_id,types)
                push_shas.append(ETag)
                i += 1
        times=str(int(time.time()*1000))
        headers = {
            "X-Arguments": self.photo_ag,
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
        }
        data={"TransFlag":"0_0","PartInfo":[]}
        count=0
        finishParts = []
        for sha in push_shas:
            count = count + 1
            sha_data = {"PartNumber": count, "ETag": sha}
            finishParts.append(sha_data)
        data["PartInfo"]=finishParts
        url="https://finder-assistant.mp.video.tencent-cloud.com/completepartuploaddfs?UploadID="+upload_id
        while True:
            try:
                res = self.session.post(url,headers=headers,json=data,timeout=8)
                if res.status_code==200:
                    break
            except Exception as e:
                print(e)
        res = res.json()
        d_url=res.get('DownloadURL')
        d_url=d_url.replace("http://wxapp.tc.qq.com","https://finder.video.qq.com")
        return d_url


    def run(self):
        if self.Authorization==None:
            print("没登录")
            return False
        icon_url = self.upload_photo(self.photo_path)
        #icon_url=""
        video = VideoFileClip(self.mp4_path)
        clipSize = video.size
        video_width = clipSize[0]
        video_height = clipSize[1]
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.Authorization,
            "Content-MD5": "null",
            "X-Arguments": self.ag,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
        }
        sizes = int(self.file_size)
        y_size=0
        BlockPartLength=[]
        count=1
        if sizes>8388608:
            while True:
                y_size=y_size+8388608
                if sizes<=8388608:
                    BlockPartLength.append(int(self.file_size))
                    break
                else:
                    BlockPartLength.append(y_size)
                sizes = sizes - 8388608
                count = count+1
        else:
            BlockPartLength = [sizes]
        data={"BlockSum":9,"BlockPartLength":[8388608,16777216,25165824,33554432,41943040,50331648,58720256,67108864,71216055]}
        data["BlockSum"]=count
        data["BlockPartLength"]=BlockPartLength
        url="https://finder-assistant.mp.video.tencent-cloud.com/applyuploaddfs"
        while True:
            try:
                res = self.session.put(url,headers=headers,json=data,timeout=6)
                if res.status_code==200:
                    break
            except Exception as e:
                print(e)
        res = res.json()
        upload_id = res.get('UploadID')
        print(upload_id)
        with open(self.mp4_path, 'rb') as f:
            f.seek(0, 2)
            flen = f.tell()
            f.seek(0, 0)
            i = 0
            count=0
            push_shas=[]
            while True:
                count=count+1
                chunk = f.read(8388608)
                if not chunk:
                    break
                url="https://finder-assistant.mp.video.tencent-cloud.com/uploadpartdfs?PartNumber="+str(count)+"&UploadID="+upload_id
                ETag=self.upload(chunk, flen, count,url,upload_id)
                push_shas.append(ETag)
                i += 1
        c_key,d_key = self.upload_check(push_shas, upload_id,video_width,video_height)
        if c_key!=None and c_key!="":
            flag = self.publish(self.title, c_key,d_key,icon_url)
            return flag


    def publish(self,title, c_key,d_key,icon_url):
        times = str(int(time.time() * 1000))
        data={"clipKey":"13859980461685541257","draftId":"13859980461685541257","timestamp":"1652238437161","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":"","scene":1}
        data["clipKey"]=c_key
        data["draftId"]=d_key
        data["timestamp"]=times
        data['rawKeyBuff']=self.raw_key
        data['_log_finder_id']=self.find_user_id
        url="https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/post/post_clip_video_result"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-WECHAT-UIN": self.uin,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            "Cookie": self.cookie
        }
        count = 0
        while True:
            try:
                count = count+1
                if count>13:
                    print("视频上传失败")
                    return
                res = self.session.post(url,headers=headers,json=data,timeout=6)
                res = res.json()
                if res.get('data').get('flag')==1:
                    break
                time.sleep(13)
            except Exception as e:
                print(e)
        #video = VideoFileClip(self.mp4_path)
        #duration = video.duration
        dua = res.get('data').get('duration')
        fileSize = res.get('data').get('fileSize')
        #fileSize=13623112
        height = res.get('data').get('height')
        width = res.get('data').get('width')
        video_md5 = res.get('data').get('md5')
        video_url=res.get('data').get('url')
        vbit = res.get('data').get('vbitrate')
        vfps = res.get('data').get('vfps')
        flag=res.get('data').get('flag')
        url="https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/helper/helper_report"
        data={"data":{"routeName":"PostCreate","customCountName":"cropSuccess","href":"https://channels.weixin.qq.com/platform/post/create","stack":"","finderUsername":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","browser":"Chrome","customCount":1,"darkmode":0,"device":"desktop","engine":"Webkit","engineVersion":"537.36","isFirstReport":"","msg":"{\"duration\":10,\"vbitrate\":9917,\"vfps\":30,\"height\":720,\"width\":1080,\"md5\":\"088cfe7acd0e585d1643fb5060f81849\",\"fileSize\":13156329,\"url\":\"https://finder.video.qq.com/251/20302/stodownload?encfilekey=Cvvj5Ix3eez3Y79SxtvVL0L7CkPM6dFibFeI6caGYwFFWIg1rKIib6jCCibCtDUDBGBoS546BDtnqzaOM0BibwgrtRo7v6sia5kQQ9JiaHo1zbA1kibDhrgqCOD3PbQKvkb6lbWGgLCnCX7edyxcH9MEYonhw&token=x5Y29zUxcibB1ORCGFxKIMOI1h6PwfJfQJnVaVF0bfVcn4ibQzqXLgD6sSW31RrhzGPvvpw9GWPJY&idx=1&adaptivelytrans=0&bizid=1023&dotrans=2991&hy=SH&m=088cfe7acd0e585d1643fb5060f81849&scene=0&t=1\",\"flag\":1}","os":"Windows","osVersion":"6.1","pv":"","renderTime":"","renderTimeLevel":"","reportHostRole":"","reportIp":"","screenLv":"","time":"","browserVersion":"101.0.4951.54"},"timestamp":"1652325167721","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESIDd1TmSbggrtHygJz6jnPnNJjfDZLzKg+i7zvEs7GirQ","pluginSessionId":"","scene":1}
        data['data']['finderUsername']=self.find_user_id
        msg = data['data']['msg']
        msg = json.loads(msg)
        msg['duration']=dua
        msg['vbitrate']=vbit
        msg['vfps']=vfps
        msg['height']=height
        msg['width']=width
        msg['md5']=video_md5
        msg['fileSize']=fileSize
        msg['url']=video_url
        msg['flag']=flag
        data['data']['msg']=msg
        data['data']['timestamp']=times
        data['data']['_log_finder_id']=self.find_user_id
        data['data']['rawKeyBuff']=self.raw_key
        while True:
            try:
                res = self.session.post(url,headers=headers,json=data,timeout=6,verify=False)
                if res.status_code==201:
                    break
                time.sleep(3)
            except Exception as e:
                print(e)
        res = res.json()
        #data={"objectType":0,"longitude":0,"latitude":0,"feedLongitude":0,"feedLatitude":0,"originalFlag":0,"topics":[],"isFullPost":1,"handleFlag":1,"videoClipTaskId":"13859980461685541257","objectDesc":{"mpTitle":"","description":"测试一下","extReading":{"link":"","title":""},"mediaType":4,"location":{"latitude":28.135509490966797,"longitude":113.03555297851562,"city":"长沙市","poiClassifyId":""},"topic":{"finderTopicInfo":"<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试一下]]></value0></finder>"},"event":{},"mentionedUser":[],"media":[{"url":"https://finder.video.qq.com/251/20302/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzR2voP8GCGRxOClaQV3hycSoT89HTTeMPLp3ibzVcX5YvA7Jm09scib5MLqtTK2ibicEoTUKxsRWP1rS53PIic1cIrAw&token=x5Y29zUxcibACCv1HhNiaygOxVu5eTq0ia5ocukeljQSpiaG2s7WGD4CdWzq8YibzcOwlPsUWPpACOjc&idx=1&adaptivelytrans=0&bizid=1023&dotrans=2991&hy=SH&m=","fileSize":3395812,"thumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ","fullThumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ","mediaType":4,"videoPlayLen":12,"width":560,"height":960,"md5sum":"8cff098c-cfe4-4b14-ae9a-cc72acac5837","urlCdnTaskId":"13859980461685541257"}]},"megavideoDesc":None,"report":{"clipKey":"13859980461685541257","draftId":"13859980461685541257","timestamp":"1652238437161","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1,"height":960,"width":560,"duration":12.267,"fileSize":3395812,"uploadCost":1250},"clientid":"5cf68763-5aa8-4560-8dd2-18f0dc7ea67d","timestamp":"1652238543823","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1}
        #data={"objectType":1,"longitude":0,"latitude":0,"feedLongitude":0,"feedLatitude":0,"originalFlag":1,"topics":[],"isFullPost":1,"handleFlag":2,"videoClipTaskId":"13859980461685541257","objectDesc":{"mpTitle":"","description":"测试一下","extReading":{"link":"","title":""},"mediaType":4,"location":{"latitude":"","longitude":"","city":"","poiClassifyId":""},"topic":{"finderTopicInfo":"<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试一下]]></value0></finder>"},"event":{},"mentionedUser":[],"media":[{"url":"https://finder.video.qq.com/251/20302/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzR2voP8GCGRxOClaQV3hycSoT89HTTeMPLp3ibzVcX5YvA7Jm09scib5MLqtTK2ibicEoTUKxsRWP1rS53PIic1cIrAw&token=x5Y29zUxcibACCv1HhNiaygOxVu5eTq0ia5ocukeljQSpiaG2s7WGD4CdWzq8YibzcOwlPsUWPpACOjc&idx=1&adaptivelytrans=0&bizid=1023&dotrans=2991&hy=SH&m=","fileSize":3395812,"thumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ","fullThumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ","mediaType":4,"videoPlayLen":12,"width":560,"height":960,"md5sum":"8cff098c-cfe4-4b14-ae9a-cc72acac5837","urlCdnTaskId":"13859980461685541257"}]},"megavideoDesc":None,"report":{"clipKey":"13859980461685541257","draftId":"13859980461685541257","timestamp":"1652238437161","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1,"height":960,"width":560,"duration":12.267,"fileSize":3395812,"uploadCost":1250},"clientid":"5cf68763-5aa8-4560-8dd2-18f0dc7ea67d","timestamp":"1652238543823","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1}
        #o_type=str(random.randint(0,1))
        data={"objectType":1,"longitude":0,"latitude":0,"feedLongitude":0,"feedLatitude":0,"originalFlag":0,"topics":[],"postFlag":1,"isFullPost":1,"handleFlag":2,"videoClipTaskId":"14081768991639472355","traceInfo":{"traceKey":"FPT_1678677670_638662299","uploadCdnStart":1678677670,"uploadCdnEnd":1678677677},"objectDesc":{"mpTitle":"","description":"测试一下","extReading":{},"mediaType":4,"location":{"latitude":28.135509490966797,"longitude":113.03555297851562,"city":"长沙市","poiClassifyId":""},"topic":{"finderTopicInfo":"<finder><version>1</version><valuecount>3</valuecount><style><at></at></style><value0><![CDATA[测试一下]]></value0><value1><topic><![CDATA[#监控下的一幕#]]></topic></value1><value2><![CDATA[\n]]></value2></finder>"},"event":{},"mentionedUser":[],"media":[{"url":"https://finder.video.qq.com/251/20302/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqz58evJ45NfCSmx2vEHfmQd1RhsdOyb6ALQPF3mBTgZnkPfGVvlPjLo7fOwaKaBibH3S5VfEATmz3kw8tnYJKFg8g&token=AxricY7RBHdUPpzZTr39ibpJ5Ov2h53Skl4WhSCU4rZAr1ajp0cOorsAHLTxGKnbS9oJ062oNZKHU&idx=1&adaptivelytrans=0&bizid=1023&dotrans=0&hy=SH&m=","fileSize":7665524,"thumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzKzKicOaV5IXiaNUic8YCTQqzibsxDks592b26qa3fSsUjCDiaMdlNTyfXCG8Q4WymNq45cAvKYP4UfX98s1RCHibeEeA&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIBHYQhqqLCs9zkgNTlghdBk4CDxaTBxvyNKW33Zs2xZnxBVQ1bcjrfoOCrY1LacQ5xhuyg2KUH4g","fullThumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzKzKicOaV5IXiaNUic8YCTQqzibsxDks592b26qa3fSsUjCDiaMdlNTyfXCG8Q4WymNq45cAvKYP4UfX98s1RCHibeEeA&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIBHYQhqqLCs9zkgNTlghdBk4CDxaTBxvyNKW33Zs2xZnxBVQ1bcjrfoOCrY1LacQ5xhuyg2KUH4g","mediaType":4,"videoPlayLen":10,"width":720,"height":1280,"md5sum":"d66ecbef-0443-4c8c-85b4-4b3add470054","urlCdnTaskId":"14081768991639472355"}]},"report":{"clipKey":"14081768991639472355","draftId":"14081768991639472355","timestamp":"1678677693661","_log_finder_uin":"17Vkk1mKOathdpnJO5EvVRRE7hxvXGWLLPFGkhj5mCznAsF9lMc5QBdlAfgc6C13WPBOSInTdc6fN5zifkMOwmj0DGPTLFjWPHE5GucB2+DkAyMRUB0Q/kFgCPGH9qcEHHChjlf4","_log_finder_id":"v2_060000231003b20faec8c7ea8e1bc3d5c901e831b07762181a5944977bdb446b25a644b98814@finder","rawKeyBuff":"CAESIHKIwmAC214Ieh+CmXlgYuSa++8XJAxxCRkQ/0Q8hkqv","pluginSessionId":None,"scene":7,"reqScene":7,"height":1280,"width":720,"duration":10.82,"fileSize":7665524,"uploadCost":2384},"mode":1,
              "clientid":"54455ab8-e0e5-42b6-883e-a7e45e293837","timestamp":"1678677747879","_log_finder_uin":"17Vkk1mKOathdpnJO5EvVRRE7hxvXGWLLPFGkhj5mCznAsF9lMc5QBdlAfgc6C13WPBOSInTdc6fN5zifkMOwmj0DGPTLFjWPHE5GucB2+DkAyMRUB0Q/kFgCPGH9qcEHHChjlf4",
              "_log_finder_id":"v2_060000231003b20faec8c7ea8e1bc3d5c901e831b07762181a5944977bdb446b25a644b98814@finder","rawKeyBuff":"CAESIHKIwmAC214Ieh+CmXlgYuSa++8XJAxxCRkQ/0Q8hkqv","pluginSessionId":None,"scene":7,"reqScene":7}

        #data={{"objectType":0,"longitude":0,"latitude":0,"feedLongitude":0,"feedLatitude":0,"originalFlag":0,"topics":[],"postFlag":1,"isFullPost":1,"handleFlag":2,"videoClipTaskId":"14081782131790842101","traceInfo":{"traceKey":"FPT_1678679231_1979700997","uploadCdnStart":1678679232,"uploadCdnEnd":1678679244},"objectDesc":{"mpTitle":"","description":"测试测试测试","extReading":{},"mediaType":4,"location":{"latitude":28.135509490966797,"longitude":113.03555297851562,"city":"长沙市","poiClassifyId":""},"topic":{"finderTopicInfo":"<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试测试测试]]></value0></finder>"},"event":{},"mentionedUser":[],"media":[{"url":"https://finder.video.qq.com/251/20302/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqz58evJ45NfCSmx2vEHfmQd1RhsdOyb6ALfsb9M8VlCnQPaCypGEiaLgGJibibcXh15Ws63IsLGWYhu5RKlMpicficswA&token=x5Y29zUxcibDaxIEXpVuiaVhpSS2Deh1xMcMUao1I2oFNsPCHmD5wdQDdJAlwyTT4S8ia9Kvmm6BeU&idx=1&adaptivelytrans=0&bizid=1023&dotrans=0&hy=SH&m=","fileSize":7665524,"thumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzKzKicOaV5IXiaNUic8YCTQqzibsxDks592b2huXpOmfE0Sdth1mtxxAznWDA2fSWWbn7ZyrKZej9XePvcW5mibbOSLQ&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIBHYQhqqLCs4vxukqVsias05rdElpptpN8cDNfsReokGI6uU4eTA4Z3GCBoNY5xOEzpF6WOtq3bFw","fullThumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzKzKicOaV5IXiaNUic8YCTQqzibsxDks592b2huXpOmfE0Sdth1mtxxAznWDA2fSWWbn7ZyrKZej9XePvcW5mibbOSLQ&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIBHYQhqqLCs4vxukqVsias05rdElpptpN8cDNfsReokGI6uU4eTA4Z3GCBoNY5xOEzpF6WOtq3bFw","mediaType":4,"videoPlayLen":10,"width":720,"height":1280,"md5sum":"82a4d517-0930-4ada-aa4d-1886e9741eed","urlCdnTaskId":"14081782131790842101"}]},"report":{"clipKey":"14081782131790842101","draftId":"14081782131790842101","timestamp":"1678679254946","_log_finder_uin":"17Vkk1mKOathdpnJO5EvVRRE7hxvXGWLLPFGkhj5mCznAsF9lMc5QBdlAfgc6C13WPBOSInTdc6fN5zifkMOwmj0DGPTLFjWPHE5GucB2+DkAyMRUB0Q/kFgCPGH9qcEHHChjlf4","_log_finder_id":"v2_060000231003b20faec8c7ea8e1bc3d5c901e831b07762181a5944977bdb446b25a644b98814@finder","rawKeyBuff":"CAESIHKIwmAC214Ieh+CmXlgYuSa++8XJAxxCRkQ/0Q8hkqv","pluginSessionId":null,"scene":7,"reqScene":7,"height":1280,"width":720,"duration":10.82,"fileSize":7665524,"uploadCost":4404},"mode":1,"clientid":"94128bf5-4d65-4ab6-b318-d5a1c2969026","timestamp":"1678679261483","_log_finder_uin":"17Vkk1mKOathdpnJO5EvVRRE7hxvXGWLLPFGkhj5mCznAsF9lMc5QBdlAfgc6C13WPBOSInTdc6fN5zifkMOwmj0DGPTLFjWPHE5GucB2+DkAyMRUB0Q/kFgCPGH9qcEHHChjlf4","_log_finder_id":"v2_060000231003b20faec8c7ea8e1bc3d5c901e831b07762181a5944977bdb446b25a644b98814@finder","rawKeyBuff":"CAESIHKIwmAC214Ieh+CmXlgYuSa++8XJAxxCRkQ/0Q8hkqv","pluginSessionId":null,"scene":7,"reqScene":7}}
        data['objectType']=1
        data['report']['_log_finder_id']=self.find_user_id
        data['_log_finder_id']=self.find_user_id
        data['rawKeyBuff']=self.raw_key
        data['report']['rawKeyBuff'] = self.raw_key
        data["videoClipTaskId"]=c_key
        data["objectDesc"]["description"] = title
        topic = data["objectDesc"]["topic"]['finderTopicInfo']
        topic = topic.replace("测试一下", title)
        data["objectDesc"]["topic"]['finderTopicInfo'] = topic
        data["objectDesc"]["media"][0]["url"]=video_url
        data["objectDesc"]["media"][0]['fileSize']=fileSize
        if self.sub_account==3:
            data["objectDesc"]["location"]["latitude"]="23.129079818725586"
            data["objectDesc"]["location"]["longitude"] = "113.26435852050781"
            data["objectDesc"]["location"]["city"] = "广州市"

            #data["objectDesc"]["mentionedUser"]=[{"nickname":"掌观南粤"}]

        elif self.sub_account==1 or self.sub_account==2:
            data["objectDesc"]["location"]["latitude"] = "28.135509490966797"
            data["objectDesc"]["location"]["longitude"] = "113.03555297851562"
            data["objectDesc"]["location"]["city"] = "长沙市"
        elif self.sub_account==4:
            data["objectDesc"]["location"]["latitude"] = "34.516849517822266"
            data["objectDesc"]["location"]["longitude"] = "110.89456176757812"
            data["objectDesc"]["location"]["city"] = "三门峡市"

        data["objectDesc"]["media"][0]['thumbUrl']=icon_url
        data["objectDesc"]["media"][0]['fullThumbUrl'] = icon_url
        data["objectDesc"]["media"][0]['md5sum'] = self.task_id
        data["objectDesc"]["media"][0]['urlCdnTaskId'] = c_key
        data["objectDesc"]["media"][0]['videoPlayLen'] = dua
        data["objectDesc"]["media"][0]['width'] = width
        data["objectDesc"]["media"][0]['height'] = height
        data['report']['clipKey']=c_key
        #data["pluginSessionId"]="null"
        times2 = str(int(time.time() * 1000))
        cost = int(times2) - int(times)
        data['report']['uploadCost'] = cost
        data['report']['draftId'] = d_key
        data["clientid"]=self.task_id
        data["timestamp"] = times2
        data['report']['timestamp'] = times2
        data['report']['width'] = width
        data['report']['height'] = height
        data['report']['duration'] = dua
        data['report']['fileSize'] = fileSize
        #data={"objectType":0,"longitude":0,"latitude":0,"feedLongitude":0,"feedLatitude":0,"originalFlag":0,"topics":[],"isFullPost":1,"handleFlag":1,"videoClipTaskId":"13860164057717803407","objectDesc":{"mpTitle":"","description":"测试标题发布","extReading":{"link":"","title":""},"mediaType":4,"location":{"latitude":28.135509490966797,"longitude":113.03555297851562,"city":"长沙市","poiClassifyId":""},"topic":{"finderTopicInfo":"<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试标题发布]]></value0></finder>"},"event":{},"mentionedUser":[],"media":[{"url":"https://finder.video.qq.com/251/20302/stodownload?encfilekey=Cvvj5Ix3eez3Y79SxtvVL0L7CkPM6dFibFeI6caGYwFFWIg1rKIib6jCCibCtDUDBGBoS546BDtnqzaOM0BibwgrtRo7v6sia5kQQJ0LokRY6sKzL9rgGSyH5Mv6VAv9mQLXAtOIhEhYuciciaDwpZzP0SOJg&token=AxricY7RBHdVem6dYLZ5QL1fn6KRmQzuicwaLS2bUia1eHolTfYscNktE22CJSIicg2eIVqKwYFKQrA&idx=1&adaptivelytrans=0&bizid=1023&dotrans=2991&hy=SH&m=088cfe7acd0e585d1643fb5060f81849&scene=0&t=1","fileSize":13156329,"thumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolQX5MP7tmtiaUJpF9KIUopDbe0BMVzr9uGBiayqg2GlA6lcTS53Bs34M27PbiauQZWvxcMeVSy5icrswkDyJkOcP6icw&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIH24zmzqvxLKe8UDS5OpM8whrPl2eEq0z0a5u2W6Ra5NsayibQiaA3l0Z66HJm4BI6lzK5oHcoC8Yw","fullThumbUrl":"https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolQX5MP7tmtiaUJpF9KIUopDbe0BMVzr9uGBiayqg2GlA6lcTS53Bs34M27PbiauQZWvxcMeVSy5icrswkDyJkOcP6icw&hy=SH&idx=1&m=&scene=0&token=6xykWLEnztIH24zmzqvxLKe8UDS5OpM8whrPl2eEq0z0a5u2W6Ra5NsayibQiaA3l0Z66HJm4BI6lzK5oHcoC8Yw","mediaType":4,"videoPlayLen":10,"width":1080,"height":720,"md5sum":"78fa318a-a122-40f9-a86a-c649851eeabc","urlCdnTaskId":"13860164057717803407"}]},"megavideoDesc":None,"report":{"clipKey":"13860164057717803407","draftId":"13860164057717803407","timestamp":"1652260324634","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1,"height":720,"width":1080,"duration":10.473,"fileSize":13623112,"uploadCost":20144},"clientid":"874350f0-625b-477b-b7af-2f06b08559eb","timestamp":"1652260361946","_log_finder_id":"v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder","rawKeyBuff":"CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+","pluginSessionId":None,"scene":1}
        url="https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/post/post_create"
        headers = {

            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-WECHAT-UIN": "3156377370",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Referer": "https://channels.weixin.qq.com/platform/post/create",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,hi;q=0.7,ru;q=0.6",
            "Cookie": self.cookie

        }
        while True:
            try:
                res = requests.post(url,headers=headers,json=data,timeout=6,verify=False)
                if res.status_code!=200:
                    break
                time.sleep(3)
            except Exception as e:
                print(e)
        res = res.json()
        if res.get('errCode')==0:
            return True
        else:
            return False

# if __name__ == '__main__':
#     # t="<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试一下]]></value0></finder>"
#     # t = t.replace("测试一下","212")
#     photo_path="C:\\Users\\Administrator\\Videos\\eab8beef495c441d1ed5c1c321977da.png"
#     mp4_path_name = "202111231142.mp4"
#     mp4_path='C:\\Users\\Administrator\\Videos\\202111231142.mp4'
#     photo_path_name="da.png"
#     title="测试标题发布"
#     size = str(os.path.getsize(mp4_path))
#     sph=sph_video(mp4_path_name,size,mp4_path,title,photo_path,photo_path_name)
#     sph.run()




# if __name__ == '__main__':
#     data = {"objectType": 0, "longitude": 0, "latitude": 0, "feedLongitude": 0, "feedLatitude": 0, "originalFlag": 0,
#             "topics": [], "isFullPost": 1, "handleFlag": 1, "videoClipTaskId": "13859980461685541257",
#             "objectDesc": {"mpTitle": "", "description": "测试一下", "extReading": {"link": "", "title": ""},
#                            "mediaType": 4,
#                            "location": {"latitude": "", "longitude": "", "city": "", "poiClassifyId": ""}, "topic": {
#                     "finderTopicInfo": "<finder><version>1</version><valuecount>1</valuecount><style><at></at></style><value0><![CDATA[测试一下]]></value0></finder>"},
#                            "event": {}, "mentionedUser": [], "media": [{
#                                                                            "url": "https://finder.video.qq.com/251/20302/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzR2voP8GCGRxOClaQV3hycSoT89HTTeMPLp3ibzVcX5YvA7Jm09scib5MLqtTK2ibicEoTUKxsRWP1rS53PIic1cIrAw&token=x5Y29zUxcibACCv1HhNiaygOxVu5eTq0ia5ocukeljQSpiaG2s7WGD4CdWzq8YibzcOwlPsUWPpACOjc&idx=1&adaptivelytrans=0&bizid=1023&dotrans=2991&hy=SH&m=",
#                                                                            "fileSize": 3395812,
#                                                                            "thumbUrl": "https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ",
#                                                                            "fullThumbUrl": "https://finder.video.qq.com/251/20304/stodownload?adaptivelytrans=0&bizid=1023&dotrans=0&encfilekey=S7s6ianIic0ia4PicKJSfB8EjyjpQibPUAXolOAM0DiayhGDu9nsN5rK3rhNpvPLgqNt42sYo88ULcQxHZnSXrfpQAORqibrTIQLC42w3ibsuHhjPJjBjxluBnj4ibQ&hy=SH&idx=1&m=&scene=0&token=cztXnd9GyrEsf6j9LDQU8frRb649czvKZnFcGbxmck9F3eaXiagejeAoHFhfPPPtpoqy8ruibJwjfbSUt2eQL7AQ",
#                                                                            "mediaType": 4, "videoPlayLen": 12,
#                                                                            "width": 560, "height": 960,
#                                                                            "md5sum": "8cff098c-cfe4-4b14-ae9a-cc72acac5837",
#                                                                            "urlCdnTaskId": "13859980461685541257"}]},
#             "megavideoDesc": None, "report": {"clipKey": "13859980461685541257", "draftId": "13859980461685541257",
#                                               "timestamp": "1652238437161",
#                                               "_log_finder_id": "v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder",
#                                               "rawKeyBuff": "CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+",
#                                               "pluginSessionId": None, "scene": 1, "height": 960, "width": 560,
#                                               "duration": 12.267, "fileSize": 3395812, "uploadCost": 1250},
#             "clientid": "5cf68763-5aa8-4560-8dd2-18f0dc7ea67d", "timestamp": "1652238543823",
#             "_log_finder_id": "v2_060000231003b20faec8c7e68a10c3d7cb00ea37b0776bcc62df65d4de52c5c444ff5e415928@finder",
#             "rawKeyBuff": "CAESINiysgSkVFGtTPJo53M7baxbB7oHP281lxm7mspMxir+", "pluginSessionId": None, "scene": 1}
#
#     data["objectDesc"]["mentionedUser"] =
#     print(data)
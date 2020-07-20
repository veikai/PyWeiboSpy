from .exceptions import LoginError
import base64
import binascii
import json
import math
import random
import re
import requests
import rsa
import time


SPY_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40 "
}
SPY_LOGIN_DATA = {
    "entry": "weibo",
    "gateway": 1,
    "from": "",
    "savestate": 7,
    "qrcode_flag": False,
    "useticket": 1,
    "pagerefer": "",
    "vsnf": 1,
    "service": "miniblog",
    "pwencode": "rsa2",
    "sr": "1920*1080",
    "encoding": "UTF-8",
    "prelt": 43,
    "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
    "returntype": "META"
}


class WeiboSpy:
    def __init__(self):
        self.prelogin_url = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController" \
                            ".preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={} "
        self.login_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
        self.pin_url = "https://login.sina.com.cn/cgi/pin.php?r={}&s=0&p={}"
        self.post_blog_url = "https://weibo.com/aj/mblog/add?ajwvr=6&__rnd={}"
        self.login_data = SPY_LOGIN_DATA
        self.__session = requests.Session()
        self.headers = SPY_HEADERS

    def login(self, username: str, password: str):
        su = base64.b64encode(username.encode("utf8")).decode("utf8")
        self.login_data["su"] = su
        resp = self.__session.get(self.prelogin_url.format(su, int(time.time() * 1000)), headers=self.headers)
        if resp.status_code != 200:
            raise LoginError(f"prelogin status code: {resp.status_code}")
        resp_str = resp.content.decode("utf8")[len("sinaSSOController.preloginCallBack("):-1]
        prelogin_data = json.loads(resp_str)
        self.login_data["nonce"] = prelogin_data["nonce"]
        self.login_data["rsakv"] = prelogin_data["rsakv"]
        self.login_data["servertime"] = prelogin_data["servertime"]
        self.login_data["pcid"] = prelogin_data["pcid"]
        rsa_publickey = int(prelogin_data["pubkey"], 16)
        key = rsa.PublicKey(rsa_publickey, 65537)
        data = f"{prelogin_data['servertime']}\t{prelogin_data['nonce']}\n{password}".encode("utf8")
        sp = binascii.b2a_hex(rsa.encrypt(data, key)).decode("utf8")
        self.login_data["sp"] = sp
        resp = self.__session.get(
            self.pin_url.format(math.floor(random.random() * 100000000), prelogin_data["pcid"]), headers=self.headers)
        if resp.status_code != 200:
            raise LoginError(f"pin status code: {resp.status_code}")
        with open("pin.png", "wb") as wf:
            wf.write(resp.content)
        door = input("请输入验证码:")
        self.login_data["door"] = door
        resp = self.__session.post(self.login_url, data=self.login_data, headers=self.headers)
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        redirect_url = re.findall(pa, resp.content.decode("GBK"))[0]
        resp = self.__session.get(redirect_url, headers=self.headers)
        pa = r'setCrossDomainUrlList\((.*?)\)'
        redirect_str = re.findall(pa, resp.content.decode("GBK"))[0]
        redirect_json = json.loads(redirect_str)
        redirect_url = f"{redirect_json['arrURL'][0]}&callback=sinaSSOController.doCrossDomainCallBack&scriptId" \
                       f"=ssoscript0&client=ssologin.js(v1.4.19)&_={int(time.time()*1000)}"
        resp = self.__session.get(redirect_url, headers=self.headers)
        print(resp.text)

    def __upload_image(self, image_path):
        with open(image_path, "rb") as rf:
            image_data = base64.b64encode(rf.read())
        my_headers = {
            "Accept":           "*/*",
            "Accept-Encoding":  "gzip, deflate",
            "Accept-Language":  "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection":       "keep-alive",
            "Content-Length":   str(len(image_data)),
            "Content-Type":     "multipart/form-data",
            "Host":             "picupload.weibo.com",
            "Origin":           "https://weibo.com",
            "Referer":          "https://weibo.com/u/7459826781/home",
            "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"
        }
        post_data = {
            "b64_data": image_data
        }
        url = "http://picupload.service.weibo.com/interface/pic_upload.php?ori=1&mime=image%2Fjpeg&data=base64&url=0&markpos=1&logo=&nick=0&marks=1&app=miniblog"
        resp = self.__session.post(url, data=post_data, headers=my_headers)
        print(resp.text)

    def post_blog(self, text: str):
        my_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Content-Length": "600",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://www.weibo.com",
            "Referer": "http://www.weibo.com/u/7459826781/home?wvr=5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40",
            "X-Requested-With": "XMLHttpRequest"
        }
        url = f"http://www.weibo.com/aj/mblog/add?ajwvr=6&__rnd={int(time.time() * 1000)}"
        post_data = {
            "location": "v6_content_home",
            "text": text,
            "appkey": "",
            "stype_type": 1,
            "pic_id": "0088QFINgy1ggwavrqa7ij31c00u0keo|0088QFINgy1ggwavrk6ctj31z40u0e81"
                      "|0088QFINgy1ggwavriwj5j31c00u0qjv|0088QFINgy1ggwavreljhj31hc0u0tm8"
                      "|0088QFINgy1ggwavuqkacj31hc0u04qz|0088QFINgy1ggwavt15zij31hc0u0b2a"
                      "|0088QFINgy1ggwavtezjbj31hc0u0hdw|0088QFINgy1ggwavsm519j31hc0u04qp"
                      "|0088QFINgy1ggwavsearjj31z40u0h12",
            "tid": "",
            "pdetail": "",
            "mid": "",
            "isReEdit": False,
            "rank": 0,
            "rankid": "",
            "module": "stissue",
            "pub_source": "main_",
            "updata_img_num": 9,
            "pub_type": "dialog",
            "isPri": 0,
            "_t": 0
        }
        resp = self.__session.post(url, data=post_data, headers=my_headers)
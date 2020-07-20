from PyWeiboSpy import WeiboSpy


my_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40 "
}


if __name__ == '__main__':
    spy = WeiboSpy()
    login_info = spy.login("18362983772", "950127zvk")
    print(login_info)
    spy.post_blog("不要同情自己，同情自己是卑劣懦夫干的勾当。")
    input()


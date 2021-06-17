import re
from time import sleep
import datetime
import json
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64

from requests import post

# 此处改为自己的配置 手机号, 密码, appId
phone = '13155655031'
password = '236264'
pid = '3f31e4f31439ef1c9288878871f9b2c26859e4565f6ad9de7d30e9da11802cc11754bcd575a00c2495d4aea4359bbf87f3ccfbb9df1b85cddaab9c593f09887236c85abfc6f0306009b3d2372ce71583'
# TG配置
#TG_TOKEN = 'xxx'  # TG机器人的TOKEN
#CHAT_ID = 'xxx'  # 推送消息的CHAT_ID


class UnicomSign():

    def __init__(self):
        self.UA = None
        self.VERSION = '8.0200'
        self.request = requests.Session()
        self.resp = '联通营业厅签到通知 \n\n'
        self.pid = pid

    # 加密算法
    def rsa_encrypt(self, str):
        # 公钥
        publickey = '''-----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6
        FUGu7yO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9
        NPhQo07+uqGQgE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0Srctg
        aqGfLgKvZHOnwTjyNqjBUxzMeQlEC2czEMSwIDAQAB
        -----END PUBLIC KEY-----'''
        rsakey = RSA.importKey(publickey)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(str.encode('utf-8')))
        return cipher_text.decode('utf-8')

    # 用户登录
    def login(self, mobile, passwd):
        self.UA = 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36; unicom{version:android@' + self.VERSION + ',desmobile:' + mobile + '};devicetype{deviceBrand:Xiaomi,deviceModel:MI 6};{yw_code:}'
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        headers = {
            'Host': 'm.client.10010.com',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': 'devicedId=20be54b981ba4188a797f705d77842d6',
            'User-Agent': self.UA,
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip',
            'Content-Length': '1446'
        }
        login_url = 'https://m.client.10010.com/mobileService/login.htm'
        login_data = {
            "deviceOS": "android9",
            "mobile": self.rsa_encrypt(mobile),
            "netWay": "Wifi",
            "deviceCode": "20be54b981ba4188a797f705d77842d6",
            "isRemberPwd": 'true',
            "version": "android@" + self.VERSION,
            "deviceId": "20be54b981ba4188a797f705d77842d6",
            "password": self.rsa_encrypt(passwd),
            "keyVersion": 1,
            "provinceChanel": "general",
            "appId": self.pid,
            "deviceModel": "MI 6",
            "deviceBrand": "Xiaomi",
            "timestamp": timestamp
        }

        res1 = self.request.post(login_url, data=login_data, headers=headers)
        if res1.status_code == 200:
            print(">>>获取登录状态成功！")
            self.resp += '>>>获取登录状态成功！\n\n'

        else:
            print(">>>获取登录状态失败！")
            self.resp += '>>>获取登录状态失败！\n\n'

        sleep(3)

    # 每日签到领积分、1g流量日包
    def daysign(self):
        headers = {
            "user-agent": self.UA,
            "referer": "https://img.client.10010.com",
            "origin": "https://img.client.10010.com"
        }
        res0 = self.request.post("https://act.10010.com/SigninApp/signin/getIntegral", headers=headers)
        if res0.json()['status'] == '0000':
            print(">>>签到前积分：" + res0.json()['data']['integralTotal'])
            self.resp += ">>>签到前积分：" + res0.json()['data']['integralTotal'] + '\n\n'
        else:
            print(">>>获取积分信息失败！")
            self.resp += '获取积分信息失败' + '\n\n'

        res1 = self.request.post("https://act.10010.com/SigninApp/signin/getContinuous", headers=headers)
        sleep(3)
        if res1.json()['data']['todaySigned'] == '1':
            res2 = self.request.post("https://act.10010.com/SigninApp/signin/daySign", headers=headers)

            print('>>>签到成功！')
            self.resp += '>>>签到成功！\n\n'
        else:
            print('>>>今天已签到！')
            self.resp += '>>>今天已签到！\n\n'

        # 看视频，积分翻倍
        sleep(3)
        res3 = self.request.post("https://act.10010.com/SigninApp/signin/bannerAdPlayingLogo", headers=headers)
        if res3.json()['status'] == '0000':
            self.resp += '>>>积分翻倍成功！\n\n'
            print(">>>积分翻倍成功！")
        else:
            print(res3.json()['msg'])
            self.resp += res3.json()['msg'] + '\n\n'

        res4 = self.request.post("https://act.10010.com/SigninApp/signin/getIntegral", headers=headers)
        if res4.json()['status'] == '0000':
            print(">>>签到后积分：" + res4.json()['data']['integralTotal'])
            self.resp += ">>>签到后积分：" + res4.json()['data']['integralTotal'] + '\n\n'
        else:
            print(">>>获取积分信息失败！")
            self.resp += '>>>获取积分信息失败！\n\n'

'''        # 每日领取1G流量日包
        res5 = self.request.post("https://act.10010.com/SigninApp/doTask/finishVideo", headers=headers)
        res6 = self.request.post("https://act.10010.com/SigninApp/doTask/getTaskInfo", headers=headers)
        res7 = self.request.post("https://act.10010.com/SigninApp/doTask/getPrize", headers=headers)
        if res7.json()['status'] == '0000':
            print(">>>1G流量日包领取成功！")
            self.resp += '>>>1G流量日包领取成功！\n\n'
        else:
            print(">>>1G流量日包任务失败！")
            self.resp += '>>>1G流量日包任务失败！\n\n'
'''
def QwxPush(Qwx_message):
    corpid='ww8280dd39cd19658b'
    corpsecret='1Av3jyVBNw7zLbxspcZezclRW0vkhhJdKy9Arng-xog'
    agentid=1000003

    access_token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'
    reg = requests.get(url=access_token_url)
    access_token=json.loads(reg.text)['access_token']
    #print(reg.text)

    send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    #message='hello!'
    send_msg = {
                "touser": "@all",
                "msgtype": "text",
                "agentid": agentid,
                "text": {
                    "content": Qwx_message,
                },
            }
    requests.post(url=send_msg_url, data=json.dumps(send_msg))

'''
# TG推送
def tgPush(telegram_message):
    params = (
        ('chat_id', CHAT_ID),
        ('text', telegram_message),
        ('parse_mode', "Html"),  # 可选Html或Markdown
        ('disable_web_page_preview', "yes")
    )
    telegram_url = "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage"
    post(telegram_url, params=params)
'''
def start():
    user = UnicomSign()
    user.login(phone, password)  # 用户登录   这里需要更改
    user.daysign()  # 日常签到领积分，1g流量日包
    QwxPush(user.resp)

def main_handler(event, context):
    return start()

if __name__ == '__main__':
    start()
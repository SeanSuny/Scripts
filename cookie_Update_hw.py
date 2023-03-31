#!/usr/bin/env python
# -*- coding:utf-8 -*-
############################################################
# @Author       : Sean
# @Date         : 2023-03-31 11:08:23
# @LastEditors  : Sean
# @LastEditTime : 2023-03-31 18:07:02
# @Description  : 这是由 Sean 创建
# @FilePath     : c:/Users/Sean/Desktop/cookie_Update_hw.py
# @Copyright    : Copyright ©2019-2023 Sean,Inc
############################################################
"""
cron: 15 1,9,17 * * *
new Env('同步COOKIE到HW');
环境变量添加 hw_host hw_token ql_host ql_client_id ql_client_secret
"""

import requests
import json
import time
import sys
import os
import re


class Update():

    def __init__(self):
        #青龙和Hw面板地址、账号密码
        if "hw_host" in os.environ and "hw_token" in os.environ and "ql_host" in os.environ and "ql_client_id" in os.environ and "ql_client_secret" in os.environ:
            self.hw_host = os.environ['hw_host']
            self.hw_token = os.environ['hw_token']
            self.ql_host = os.environ['ql_host']
            self.client_id = os.environ['ql_client_id']
            self.client_secret = os.environ['ql_client_secret']
        else:
            print("环境变量未添加或填写不全！！！")
            sys.exit(0)
        self.ql_token = self.get_token()

    def get_token(self):
        url = self.ql_host + "/open/auth/token?client_id={}&client_secret={}".format(self.client_id, self.client_secret)
        try:
            response = requests.request("GET", url).json()
            if (response['code'] == 200):
                print(f"获取青龙面板的token：{response}")
                return response["data"]["token"]
            else:
                print(f"登录失败：{response['message']}")
        except Exception as e:
            print(f"登录失败：{str(e)}")

    # 获取所有的变量
    def get_all_ck(self):
        t = int(round(time.time() * 1000))
        url = self.ql_host + "/open/envs?searchValue=&t=" + str(t)
        headers = {'Authorization': 'Bearer ' + self.ql_token}
        try:
            response = requests.request("GET", url, headers=headers).json()
            if (response['code'] == 200):
                print("获取青龙面板所有的Cookie")
                cklist = response["data"]
                ptPin_list = []
                ptKey_list = []
                remarks_list = []
                for i in cklist:
                    if "app_open" in i["value"]:
                        ptPin_list.append(re.findall('pt_pin=(.+?);', i["value"])[0])
                        ptKey_list.append(re.findall('pt_key=(.+?);', i["value"])[0])
                        remarks_list.append(i["remarks"])
                return ptPin_list, ptKey_list, remarks_list
            else:
                print(f"获取环境变量失败：{response['message']}")
        except Exception as e:
            print(f"获取环境变量失败：{str(e)}")

    # 添加和更新变量
    def update_ck(self, ptPin, ptKey, remarks):
        url = self.hw_host + "/openApi/addOrUpdateAccount"
        payload = json.dumps({"ptPin": ptPin, "ptKey": ptKey, "remarks": remarks})
        headers = {'Content-Type': 'application/json', 'api-token': f'{self.hw_token}'}
        try:
            print("添加和更新变量")
            response = requests.request("POST", url, headers=headers, data=payload).json()
            if (response['code'] == 1):
                print(f"添加和更新环境变量成功！！!\n现存服务器:Cookie {response['data']['cookieCount']} 个，Wskey {response['data']['accountCount']} 个")
                return True
            else:
                print(f"添加和更新环境变量失败：{response['msg']}")
                return False
        except Exception as e:
            print(f"添加和更新环境变量失败：{str(e)}")
            return False

    # 对ck进行添加和更新
    def match_ck(self):
        (ptPin, ptKey, remarks) = self.get_all_ck()
        cookie = dict(zip(ptPin, zip(ptKey, remarks)))
        for key, value in cookie.items():
            print("-------------------")
            print("开始添加和更新 {} 的ck".format(key))
            self.update_ck(key, value[0], value[1])


if __name__ == '__main__':
    Update().match_ck()

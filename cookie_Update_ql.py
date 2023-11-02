"""
cron: 10 1,9,19 * * *
new Env('同步COOKIE到青龙');
环境变量添加 ql_host ql_client_id ql_client_secret
"""

import requests
import json
import time
import sys
import os
import re


class Update():

    def __init__(self):
        #青龙面板地址、账号密码
        if "ql_host" in os.environ and "ql_client_id" in os.environ and "ql_client_secret" in os.environ:
            self.host = os.environ['ql_host']
            self.client_id = os.environ['ql_client_id']
            self.client_secret = os.environ['ql_client_secret']
        else:
            print("环境变量未添加或填写不全！！！")
            sys.exit(0)
        self.token = self.get_token()

    def cookie(self):
        if not os.path.exists("cookie_export.sh"):
            os.system('task https://supermanito.github.io/Helloworld/scripts/cookie_export.sh now | grep -Ev "JD_COOKIE|^$" > /jd/config/cookie.txt')
        else:
            os.system('task cookie_export.sh now | grep -Ev "JD_COOKIE|^$" > /jd/config/cookie.txt')
        ck = open('/jd/config/cookie.txt', 'r')
        lines = ck.readlines()
        list = []
        for line in lines:
            line_ck = re.sub(r'\n|,|"', '', line)
            list.append(line_ck)
        return list

    def get_token(self):
        url = self.host + "/open/auth/token?client_id={}&client_secret={}".format(self.client_id, self.client_secret)
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
        url = self.host + "/open/envs?searchValue=&t=" + str(t)
        headers = {'Authorization': 'Bearer ' + self.token}
        try:
            response = requests.request("GET", url, headers=headers).json()
            if (response['code'] == 200):
                print("获取青龙面板所有的变量进行比对")
                return response["data"]
            else:
                print(f"获取环境变量失败：{response['message']}")
        except Exception as e:
            print(f"获取环境变量失败：{str(e)}")

    # 更新变量
    def update_ck(self, ck, id=None):
        t = int(round(time.time() * 1000))
        url = self.host + "/open/envs?t=" + str(t)
        payload = json.dumps({"name": "JD_COOKIE", "value": ck, "id": id})
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        try:
            print("更新变量")
            response = requests.request("PUT", url, headers=headers, data=payload).json()
            if (response['code'] == 200):
                print(f"更新环境变量成功:{response}")
                return True
            else:
                print(f"更新环境变量失败：{response['message']}")
                return False
        except Exception as e:
            print(f"更新环境变量失败：{str(e)}")
            return False

    def add_ck(self, ck):
        t = int(round(time.time() * 1000))
        url = self.host + "/open/envs?t=" + str(t)
        payload = json.dumps([{"value": ck, "name": "JD_COOKIE"}])
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        try:
            print("-------------------")
            print("添加环境变量")
            response = requests.request("POST", url, headers=headers, data=payload).json()
            if (response['code'] == 200):
                print(f"添加环境变量成功：{response}")
                return True
            else:
                print(f"添加环境变量失败：{response['message']}")
                return False
        except Exception as e:
            print(f"添加环境变量失败：{str(e)}")
            return False

    def start_ck(self, id):
        t = int(round(time.time() * 1000))
        url = self.host + "/open/envs/enable?t=" + str(t)
        list = []
        list.append(id)
        payload = json.dumps(list)
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        try:
            print("启用ck：{}".format(payload))
            response = requests.request("PUT", url, headers=headers, data=payload).json()
            if (response['code'] == 200):
                print("启用ck：{}成功".format(payload))
                return True
            else:
                print("启用ck：{}失败：".format(payload) + {response['message']})
                return False
        except Exception as e:
            print("启用ck：{}失败：".format(payload) + {str(e)})
            return False

    # 比对ck进行更新，如果未启用，进行启用
    def match_ck(self):
        cklist = self.get_all_ck()
        for ck in self.cookie():
            pt_pin = str(re.findall(r"(pt_pin=.+?);", ck)[0])
            if not cklist:
                self.add_ck(ck)
                print("新增 {} 的ck".format(pt_pin))
            else:
                for i in cklist:
                    if pt_pin in str(i["value"]):
                        print("-------------------")
                        print("匹配成功，匹配到当前变量：", i)
                        id = i["id"]
                        print("开始更新 {} 的ck".format(pt_pin))
                        self.update_ck(ck, id)
                        if i["status"] == 1:
                            print("{} 启用成功".format(pt_pin))
                            self.start_ck(id)


if __name__ == '__main__':
    Update().match_ck()

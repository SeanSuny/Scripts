# Author: lindaye
# V1.1.6
# 2023.8.31 14:00更新:
#   1.改为变量ck,一行一个ck示例
#   2.采用Wxpusher进行推送服务(手动过检测),仅需扫码获取UID,无需其他操作
#   3.企业微信机器人/Wxpusher (二选一)
# Wxpusher获取UID: https://wxpusher.zjiecode.com/demo/
# 变量名 wx_czgm Wxpusher 示例: {"ck":"这里是cookie中gfsessionid的值","ts":"这里是推送Wxpusher获取UID"}
# 变量名 wx_czgm 企业微信 示例: {"ck":"这里是cookie中gfsessionid的值","qw":"这里是推送企业微信机器人Key"}
# 入口：http://2496831.qz2hkanpfw.orut03cj0o2p.cloud/?p=2496831
import re
import time
import hashlib
import random
import requests
import os
from urllib.parse import unquote,quote


if os.getenv('wx_czgm') == None:
    print("Ck异常: 请至少填写一个账号ck!")
    exit()
ck_token = [eval(line) for line in os.getenv('wx_czgm').strip().split('\n')]

# 检测列表
check_list = ['MzkyMzI5NjgxMA==', 'MzkzMzI5NjQ3MA==', 'Mzg5NTU4MzEyNQ==', 'Mzg3NzY5Nzg0NQ==', 'MzU5OTgxNjg1Mg==', 'Mzg4OTY5Njg4Mw==', 'MzI1ODcwNTgzNA==']
# 推送TsKey
TsKey = ''
tstype = ''
# 推送域名
tsurl = 'https://linxi-send.run.goorm.app'
# 临时用户名
temp_user = ''
# 保持连接,重复利用
ss = requests.session()
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 9; V1923A Build/PQ3B.190801.06161913; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36 MMWEBID/5635 MicroMessenger/8.0.40.2420(0x28002837) WeChat/arm64 Weixin Android Tablet NetType/WIFI Language/zh_CN ABI/arm64",
}

def get_sign():
    current_time = str(int(time.time()))
    # 计算 sign
    sign_str = f"key=4fck9x4dqa6linkman3ho9b1quarto49x0yp706qi5185o&time={current_time}"
    sha256_hash = hashlib.sha256(sign_str.encode())
    sign = sha256_hash.hexdigest()
    data = f'time={current_time}&sign={sign}'
    return data

def home():
    url = "http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/share"
    response = ss.get(url, headers=headers, data=get_sign()).json()
    share_link = response["data"]["share_link"][0]
    p_value = share_link.split("=")[1].split("&")[0]
    global temp_user
    temp_user = p_value
    url = "http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/read/info"
    response = ss.get(url, headers=headers, data=get_sign()).json()
    if response["code"] == 0:
        remain = response["data"]["remain"]
        read = response["data"]["read"]
        print(f"ID:{p_value}   钢镚余额:{remain}\n今日阅读量:{read} 篇\n推广链接:{share_link}")
    else:
        print(response["message"])


def read():
    check_status = False
    while True:
        url = "http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/read/task"
        response = ss.get(url, headers=headers, data=get_sign()).json()
        if response["code"] == 1:
            if "秒" in response['message']:
                print(response["message"])
                s = re.findall('请(.*?)秒',response['message'])[0]
                time.sleep(int(s))
            else:
                print(response["message"])
                break
        else:
            try:
                s = random.randint(10,15)
                # 检测是否是检测文章
                biz = re.findall("biz=(.*?)&",response["data"]["link"])[0]
                print(f"获取文章成功---{biz}---阅读时间{s}")
                if biz in check_list:
                    if check_status == False:
                        print(f"获取到检测文章,已推送到微信,请60s内完成验证!")
                        check_status = True
                        # 过检测
                        check = test(biz,response["data"]["link"])
                        if check == True:
                            print("检测文章-过检测成功啦!")
                            time.sleep(s)
                            response = ss.post("http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/read/finish", headers=headers, data=get_sign()).json()
                            print(f'阅读文章成功---获得钢镚[{response["data"]["gain"]}]---已读{response["data"]["read"]}篇')
                        else:
                            print("检测文章-过检测失败啦!")
                            break
                    else:
                        print("获取到多次检测文章-已自动停止防止黑号,请手动去处理!")
                        break
                else:
                    time.sleep(s)
                    url = "http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/read/finish"
                    response = ss.post(url, headers=headers, data=get_sign()).json()
                    print(response)
                    if response["code"] == 0:
                        if response["data"]["check"] is False:
                            print(f'阅读文章成功---获得钢镚[{response["data"]["gain"]}]---已读{response["data"]["read"]}篇')
                        else:
                            print(f"获取到未收录检测: {biz} 将自动停止脚本")
                            break
                    else:
                        if response['message'] == "记录无效":
                            print("记录无效,重新阅读")
                        else:
                            print(response)
                            break

            except KeyError:
                if response['code'] == 801:
                    print(f"今日任务已完成: {response['message']}")
                    break
                else:
                    print(f"获取文章失败,错误未知{response}")
                    break



def get_money():
    print("============开始微信提现============")
    url = "http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud/withdraw/wechat"
    response = ss.get(url, headers=headers, data=get_sign()).json()
    if response["code"] == 0:
        print(response["message"])
    elif response["code"] == 1:
        print(response["message"])
    else:
        print(f"错误未知{response}")


def test(biz,link):
    result = ss.post(tsurl+"/task",json={"biz":temp_user+biz,"url":link}).json()
    WxSend("微信阅读-钢镚阅读", "检测文章", "请在60s内阅读当前文章",tsurl+"/read/"+temp_user+biz,link)
    check = ''
    for i in range(30):
        result = ss.get(tsurl+"/back/"+temp_user+biz).json()
        if result['status'] == True:
            check = True 
            break
        else:
            print("等待检测中...", end="\r", flush=True)
        time.sleep(2)
    if result['status'] == False:
        print("手动检测超时,验证失败!")
        check = False 
    return check


# 微信推送
def WxSend(project, status, content,turl,link):
    if tstype == "ts":
        result = requests.get(f'https://wxpusher.zjiecode.com/demo/send/custom/{TsKey}?content={status}-{project}%0A{content}%0A%3Cbody+onload%3D%22window.location.href%3D%27{quote(turl)}%27%22%3E').json()
        print(f"微信消息推送: {result['msg']}")
        print(f"手动微信阅读链接: {link}")
        print(f"手动检测链接: {unquote(turl)}")
    elif tstype == "qw":
        webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={TsKey}"
        txt = f"## `{project}`\n### 通知状态: {status}\n ### 通知备注: {content}\n### 通知链接: [点击开始检测阅读]({turl})\n### 微信原文: [点击打开文章]({link})"
        data = {"msgtype": "markdown", "markdown": {"content": txt}}
        headers = {"Content-Type": "text/plain"}
        result = ss.post(url=webhook, headers=headers, json=data).json()
        print(f"企业微信BOT推送: {result['errmsg']}")
        print(f"手动验证链接:{unquote(turl)}")


for i in ck_token:
    print(f"============当前第{ck_token.index(i)+1}个账户============")
    headers['Cookie'] = f"gfsessionid={i['ck']};"
    if 'ts' in i:
        TsKey = i['ts']
        tstype = 'ts'
    elif 'qw' in i:
        TsKey = i['qw']
        tstype = 'qw'
    else:
        print("未设置推送Tskey,请设置(企业微信'qw'/Wxpusher'ts')")
        exit()
    home()
    read()
    get_money()

# cron: 10 */30 * * * *
# new Env('微信-从零开始阅读');

# Author: lindaye
# V1.1.6
# 2023.8.31 19:00更新:
#   1.改为变量ck,一行一个ck示例
#   2.采用Wxpusher进行推送服务(手动过检测),仅需扫码获取UID,无需其他操作
#   3.企业微信机器人/Wxpusher (二选一)
# Wxpusher获取UID: https://wxpusher.zjiecode.com/demo/
# 变量名 wx_clks 示例: {"ck":"这里是cookie中authtoken的值","ts":"这里是推送Wxpusher获取UID"}
# 变量名 wx_clks 企业微信 示例: {"ck":"这里是cookie中authtoken的值","qw":"这里是推送企业微信机器人Key"}
# 入口：https://entry-1318684421.cos.ap-nanjing.myqcloud.com/cos_b.html?openId=oiDdr563TOZlmaRzrEPgBIM_n6DQ
import requests
#加密
from Crypto.Cipher import AES
import base64
# 随机值
import random
# 正则匹配
import re
# 时间
import time
import os
from urllib.parse import unquote,quote

if os.getenv('wx_clks') == None:
    print("Ck异常: 请至少填写一个账号ck!")
    exit()
ck_token = [eval(line) for line in os.getenv('wx_clks').strip().split('\n')]

# 推送域名
tsurl = 'https://linxi-send.run.goorm.app'
# 临时用户名
temp_user = ''
# 推送TsKey
TsKey = ''
tstype= ''
# 保持连接,重复利用
ss = requests.session()


headers = {
    'User-Agent':'Mozilla/5.0 (Linux; U; Android 4.1.2; zh-cn; GT-I9300 Build/JZO54K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30 MicroMessenger/5.2.380'
}

checkDict=[
'Mzg4MDU1MTc0NA==',
'MzU5MDc0NjU4Mg==',
'MzA3Njk1NzAyNA==',
'MzI2ODcwOTQzMg==',
'MzU5ODU0MzM4Mg==',
'Mzg2OTcwOTQzNQ==',
'MzI0NTgyOTYxOQ==',
'MzI3MTY2OTYyNA==',
'MjM5NTY1OTI0MQ==',
'MzU3ODEyNTgyNQ==',
'MzkyNDIxMzE4OA==',
'MzI1NjY4Njc0Mw==',
"MzU4OTg3Njg1Nw==",
"MzkyMjExNzE1Ng==",
'MzA5MzE1ODI4NQ==', # 新增
'MzAxMDEyODg2MA==',
'MzI4MTAzODE5NA==',
"Mzg3MTgyOTgyMw==",
]


def aes_encrypt(data):
    block_size = AES.block_size  # 获取AES块大小
    padding = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)  # 填充函数，使得数据长度为块大小的整数倍
    key = b'5e4332761103722eb20bb1ad53907c6e'  # 密钥，需要根据实际情况修改
    cipher = AES.new(key, AES.MODE_ECB)  # 使用ECB模式创建AES对象
    encrypted_data = cipher.encrypt(padding(data).encode())  # 对数据进行加密
    encrypted_data_base64 = base64.b64encode(encrypted_data).decode()  # 对加密后的数据进行base64编码
    return encrypted_data_base64

def get_readhome():
    url = 'https://sss.mvvv.fun/app/enter/read_home'
    result = ss.get(url,headers=headers).json()
    if result['code'] == 0:
        url = "http://" + re.findall('//(.*?)/',result['data']['location'])[0]
        get_read(url)
    else:
        print("获取阅读域名失败!")
        get_read("http://hmqulo7g9p.qqaas.fun")


def get_read(url):
    result = ss.get(url+"/app/user/myPickInfo",headers=headers).json()
    if result['code'] == 401:
        print(f"账号异常:{result['msg']}")
    else:
        data = aes_encrypt(f'{{"moneyPick":{result["data"]["goldNow"]}}}')
        result = ss.post(url+"/app/user/pickAuto",headers=headers,json=data).json()
        print(f"兑换结果: {result['msg']}")
        result = ss.get(url+"/app/user/myInfo",headers=headers).json()['data']
        print(f"用户: {result['nameNick']} 今日已读: {result['completeTodayCount']}篇  获得积分: {result['completeTodayGold']}")
        global temp_user
        temp_user = result['nameNick']
        if result['remainSec'] == 0:
            print ('当前是读文章的状态')#line:93
            get_myinfo(url)
        else :#line:94
            ttime =int (result['remainSec'] /60 )#line:95
            print ('当前不是是读文章的状态,距离下次阅读还有',ttime ,'分钟')#line:96
    
    
def get_myinfo(url):
    result = ss.get(url+"/app/read/get",headers=headers).json()['data']['location']
    u = re.findall(r'u=([^&]+)',result)[0]
    print(f"获取到KEY: {u}")
    do_read(u)


def do_read(u):
    result = ss.get(f'https://sss.mvvv.fun/app/task/doRead?u={u}&type=1',headers=headers).json()['data']
    if result['bizCode'] !=0:
        tips = {20:'文章正在补充中，稍后再试',30:'下批文章将在24小时后到来',10:'本轮阅读已完成',11:'当天达到上限'}
        print(tips[result['bizCode']])
    else:
        check_num = 0
        while True:
            if check_num <= 1:
                taskKey = result['taskKey']
                taskUrl = result['taskUrl']
                # 获取biz
                biz = re.findall("biz=(.*?)&amp;",ss.get(taskUrl).text)
                if biz == []:
                    biz = None
                    print(f"获取biz异常:{taskUrl}")
                else:
                    biz = biz[0]
                print(f"阅读任务ID({biz}): {taskKey}")
                s = random.randint (10 ,12 )
                print(f"随机阅读 {s} 秒")
                if biz in checkDict:
                    check_num += 1
                    print("阅读文章检测-已推送至微信,请60s内完成验证!")
                    check = test(biz,result['taskUrl'])
                    if check == True:
                        print("检测文章-过检测成功啦!")
                        time.sleep(5)
                        url = f'https://sss.mvvv.fun/app/task/doRead?u={u}&type=1&key={taskKey}'
                        result = ss.get(url,headers=headers).json()['data']
                    else:
                        print("检测文章-过检测失败啦!")
                        break
                else:
                    time.sleep(s)
                    url = f'https://sss.mvvv.fun/app/task/doRead?u={u}&type=1&key={taskKey}'
                    result = ss.get(url,headers=headers).json()['data']
                    if result['bizCode'] == 31:
                        print(f"未收录biz: {biz} 检测结果: {result['detail']}")
                        break
                if result['bizCode'] == 0:
                    print(f"阅读结果: {result['detail']}")
                elif result['bizCode'] == 31:
                    print(f"检测结果: {result['detail']}")
                    result = ss.get(f'https://sss.mvvv.fun/app/task/doRead?u={u}&type=1',headers=headers).json()['data']
                else:
                    tips = {20:'文章正在补充中，稍后再试',30:'下批文章将在24小时后到来',10:'本轮阅读已完成',11:'当天达到上限'}
                    print(tips[result['bizCode']])
                    break
            else:
                print("获取到多次检测文章-已自动停止防止黑号,请手动去处理!")
                break


def test(biz,link):
    result = ss.post(tsurl+"/task",json={"biz":temp_user+biz,"url":link}).json()
    WxSend("微信阅读-微信阅读",f"{temp_user}-检测文章", "请在60s内阅读当前文章",tsurl+"/read/"+temp_user+biz,link)
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
    headers['Cookie'] = f'authtoken={i["ck"]}; snapshot=0'
    if 'ts' in i:
        TsKey = i['ts']
        tstype = 'ts'
    elif 'qw' in i:
        TsKey = i['qw']
        tstype = 'qw'
    else:
        print("未设置推送Tskey,请设置(企业微信'qw'/Wxpusher'ts')")
        exit()
    get_readhome()

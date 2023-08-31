# Author: lindaye
# V1.1.6
# 2023.8.31 14:00更新:
#   1.改为变量ck,一行一个ck示例
#   2.采用Wxpusher进行推送服务(手动过检测),仅需扫码获取UID,无需其他操作
#   3.企业微信机器人/Wxpusher (二选一)
# Wxpusher获取UID: https://wxpusher.zjiecode.com/demo/
# 变量名 wx_shy 示例: {"un":"这里是cookie的un值","token":"这里是cookie的token值","ts":"这里推送Wxpusher获取UID"}
# 变量名 wx_shy 企业微信 示例: {"un":"这里是cookie的un值","token":"这里是cookie的token值","qw":"这里是推送企业微信机器人Key"}
# http://mr1693464627736.zppnplq.cn/coin/index.html?mid=CR42F6WUF 【元宝阅读】看文章赚零花钱，全新玩法，提现秒到(若链接打不开，可复制到手机浏览器里打开)
# http://mr1693464650323.rikybod.cn/ox/index.html?mid=RG7UUSYFS 【星空阅读】看文章赚零花钱，全新玩法，提现秒到(若链接打不开，可复制到手机浏览器里打开)
# http://mr1693464671933.ennvjtb.cn/user/index.html?mid=D33C7W3A3 【花花阅读】看文章赚零花钱，全新玩法，提现秒到(若链接打不开，可复制到手机浏览器里打开)
import requests
import re
import time
import os
from urllib.parse import unquote,quote

if os.getenv('wx_shy') == None:
    print("Ck异常: 请至少填写一个账号ck!")
    exit()
ck_token = [eval(line) for line in os.getenv('wx_shy').strip().split('\n')]

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX3461 Build/RKQ1.210503.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5223 MMWEBSDK/20230701 MMWEBID/7925 MicroMessenger/8.0.40.2420(0x28002851) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
    'Cookie':'',
}

# 推送域名
tsurl = 'https://linxi-send.run.goorm.app'
# 临时用户名
temp_user = ''
# 推送TsKey
TsKey = ""
tstype = ''
# 保持连接,重复使用
ss = requests.session()

data = {"pageSize":20}


def user():
    url = domain +'/info'
    result = ss.post(url,headers=headers,json=data).json()['result']
    print(f"{ydname}账号: {result['uid']} 今日已读: {result['dayCount']} 今日积分:{result['moneyCurrent']}")
    global temp_user
    temp_user = result['uid']
    if ydname == "花花":
        options = [0.3, 0.5, 1, 5]  # 可选的数字列表
    else:
        options = [0.3, 1, 5, 10]  # 可选的数字列表
    max_money = max(filter(lambda x: x < (int(result['moneyCurrent'])/10000), options), default=0.3)
    return max_money

def read():
    while True:
        result = ss.post(domain +'/read',headers=headers,json=data).json()
        if result['code'] == 0:
            if result["result"]["status"] == 10:
                biz=''.join(re.findall('__biz=(.+)&mid',result["result"]["url"]))
                if biz in ['Mzg2Mzk3Mjk5NQ==']:
                    print("检测文章: 当前为检测文章,请60s内完成验证!")
                    check = test(result["result"]["url"])
                    if check == True:
                        print("检测文章-过检测成功啦!")
                        time.sleep(10)
                        result = ss.post(domain +'/submit',headers=headers,json=data).json()
                        print(f"阅读成功: 积分{result['result']['val']} 剩余{result['result']['progress']}篇") 
                    else:
                        print("检测文章-过检测失败啦!")
                        break
                else:
                    print(f"开始阅读文章-{biz}-阅读时间 6s")
                    time.sleep(6)
                    result = ss.post(domain +'/submit',headers=headers,json=data).json()["result"]
                    print(f"阅读成功: 积分{result['val']} 剩余{result['progress']}篇")  
            else:
                tips = {30:'重新运行尝试一下',40:'文章还没有准备好',50:'阅读失效,黑号了',60:'已经全部阅读完了',70:'下一轮还未开启',}
                print(f'{ydname}账号提醒: {tips[result["result"]["status"]]}!')
                if result["result"]["status"] ==30:
                    time.sleep(1)
                    continue
                else:
                    break
        else:
            if result['msg'] == "请求频繁":
                time.sleep(1)
                continue
            else:
                print(f"异常: {result}")
                break

def get_money(max_money):
    time.sleep(2)
    print(f"=================={ydname}提现====================")
    if ydname == "花花":
        q_data = {"mid":temp_user,"un":data['un'],"token":data['token'],"pageSize":20}
        result = ss.post('http://u.cocozx.cn/api/user/psmoneyc',headers=headers,json=q_data).json()
        print(f"花花收取徒弟贡献: {result}")
        t = "/wd"
    else:
        t = "/wdmoney"
    T_data = {"val":str(int(max_money*10000)),"un":data['un'],"token":data['token'],"pageSize":20}
    response = ss.post(domain+t, headers=headers, json=T_data).json()
    if response['code'] == 0:
        print(f"提现成功: {max_money}元")
    else:
        print(f"提现失败: {response['msg']}")


def test(link):
    result = ss.post(tsurl+"/task",json={"biz":temp_user,"url":link}).json()
    WxSend(f"微信阅读-{ydname}阅读", f"{temp_user}-检测文章", "请在60s内阅读当前文章",tsurl+"/read/"+temp_user,link)
    check = ''
    for i in range(30):
        result = ss.get(tsurl+"/back/"+temp_user).json()
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


for i in ['/user','/coin','/ox']: # 删除其中不需要的即可跑单阅读
    domain = 'http://u.cocozx.cn/api'+i # 花花 /user 元宝阅读 /coin 星空阅读 /ox
    ydlist = {'/user':'花花','/coin':'元宝','/ox':'星空'}
    ydname = ydlist[i]
    print(f"=================={ydname}阅读====================")
    for u in ck_token:
        print(f"============当前第{ck_token.index(u)+1}个账户============")
        data['un'] = u['un']
        data['token'] = u['token']
        if 'ts' in u:
            TsKey = u['ts']
            tstype = 'ts'
        elif 'qw' in u:
            TsKey = u['qw']
            tstype = 'qw'
        else:
            print("未设置推送Tskey,请设置(企业微信'qw'/Wxpusher'ts')")
            exit()
        max_money = user()  # 提现金额
        read()
        max_money = user()  # 提现金额
        time.sleep(1)
        get_money(max_money)
        time.sleep(1)

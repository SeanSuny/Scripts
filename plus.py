'''
查京东PLUS综合分快速筛号

低于80的可能各种活动会开始火爆，仅供参考
cklist.txt 存放cookie，一行一个，原始内容无特殊字符
const $ = new Env('查京东PLUS综合分');
'''

import requests
import os
import sys
import time
from asyncio import run, sleep

# 自定义配置
scores = 70  # 低于此分数的会被标记为不合格
txtName = "cklist.txt"
validCookiesArr = []


def printf(text):
    print(text)
    sys.stdout.flush()


async def queryScore(ck, count, scores):
    try:
        name = ck.split('pin=')[1].split(';')[0]
        # printf(f"\n---- 账号[{count}][{name}] ----")
        headers = {
            "Host": "rsp.jd.com",
            "Connection": "keep-alive",
            "User-Agent": "JD4iPhone/168210%20(iPhone;%20iOS;%20Scale/2.00)",
            "Cookie": ck
        }
        url = f"https://rsp.jd.com/windControl/queryScore/v1?lt=m&an=plus.mobile&stamp={int(time.time()*1000)}"
        result = requests.get(url=url, headers=headers).json()
        if 'code' in result and result['code'] == '1000':
            rs = result["rs"]
            if rs['userSynthesizeScore']['totalScore'] >= scores:
                printf(f"{count}. [{name}] ➜ {rs['userSynthesizeScore']['totalScore']} ✅")
                validCookiesArr.append(ck)
            else:
                printf(f"{count}. [{name}] ➜ 不达标 ❌")
            # printf(f"{count}. [{name}] ➜ PLUS综合分: {rs['userSynthesizeScore']['totalScore']}")
            # printf(f"周期: {rs['scoreUserInfo']['calBeginDate']} ~ {rs['scoreUserInfo']['calEndDate']}")
            # printf(f"各项相对分数：")
            # printf(f"账户信息 -- {rs['userDimensionScore']['accountInfo']}/5")
            # printf(f"信用价值 -- {rs['userDimensionScore']['baiScore']}/5")
            # printf(f"购物合规 -- {rs['userDimensionScore']['active']}/5")
            # printf(f"购物历史 -- {rs['userDimensionScore']['shop']}/5")
            # printf(f"售后行为 -- {rs['userDimensionScore']['shopAfter']}/5")
        elif 'msg' in result:
            if result['msg'] == "用户未登录":
                print(f"{count}. [{name}] ➜ 账号无效 ❌")
            else:
                printf(f"{count}. [{name}] ➜ 查询出错: {result['msg']} ⚠")
        else:
            printf(f'{count}. [{name}] ➜ 查询出错 ⚠')
    except Exception as e:
        printf(e)

    await sleep(0.5)


# 加载ck
try:
    with open(os.path.join(os.path.dirname(__file__), txtName), 'r') as f:
        cks = f.read().split('\n')
except:
    cks = os.environ['JD_COOKIE'].split('&')

if __name__ == "__main__":
    count = 0
    for ck in cks:
        if ck == '' or ck == None:
            continue
        count += 1
        for char in ['\"', '\'', ',']:
            ck = ck.replace(char, "")
        # print(ck)
        run(queryScore(ck, count, scores))
    if len(validCookiesArr) > 0:
        # 去重
        validCookiesArr = list(set(validCookiesArr))
        # 重新写入到文件
        with open(os.path.join(os.path.dirname(__file__), txtName), 'w') as f:
            f.write('\n'.join(validCookiesArr))
            f.close()
        printf(f"\n已将合格账号写入至{txtName}，共{len(validCookiesArr)}个\n")

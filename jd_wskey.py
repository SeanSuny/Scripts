# -*- coding: utf-8 -*
'''
new Env('wskey转换');
'''
import socket  # 用于端口检测
import base64  # 用于编解码
import json  # 用于Json解析
import os  # 用于导入系统变量
import sys  # 实现 sys.exit
import logging  # 用于日志输出
import time  # 时间
import re  # 正则过滤

WSKEY_MODE = 0
# 0 = Default / 1 = Debug!

if "WSKEY_DEBUG" in os.environ or WSKEY_MODE:  # 判断调试模式变量
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')  # 设置日志为 Debug等级输出
    logger = logging.getLogger(__name__)  # 主模块
    logger.debug("\nDEBUG模式开启!\n")  # 消息输出
else:  # 判断分支
    logging.basicConfig(level=logging.INFO, format='%(message)s')  # Info级日志
    logger = logging.getLogger(__name__)  # 主模块

try:  # 异常捕捉
    import requests  # 导入HTTP模块
except Exception as e:  # 异常捕捉
    logger.info(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")  # 日志输出
    sys.exit(1)  # 退出脚本
os.environ['no_proxy'] = '*'  # 禁用代理
requests.packages.urllib3.disable_warnings()  # 抑制错误
try:  # 异常捕捉
    from notify import send  # 导入青龙消息通知模块
except Exception as err:  # 异常捕捉
    logger.debug(str(err))  # 调试日志输出
    logger.info("无推送文件")  # 标准日志输出

ver = 21212  # 版本号


def hw_send(text):
    if "WSKEY_SEND" in os.environ and os.environ["WSKEY_SEND"] == 'disable':
        return True
    else:
        try:  # 异常捕捉
            send('WSKEY转换', text)  # 消息发送
        except Exception as err:  # 异常捕捉
            logger.debug(str(err))  # Debug日志输出
            logger.info("通知发送失败")  # 标准日志输出


# 返回值 Token
def hw_login():  # 方法 HW登录(获取Token 功能同上)
    path = '/jd/config/auth.json'  # 设置HW auth文件地址
    if os.path.isfile(path):  # 进行文件真值判断
        with open(path, "r", encoding="utf-8") as file:  # 上下文管理
            auth = file.read()  # 读取文件
            file.close()  # 关闭文件
        auth = json.loads(auth)  # 使用 json模块读取
        token = auth.get('openApiToken', '')  # 提取 openApiToken
        return token
    else:  # 判断分支
        logger.info("没有发现auth文件, 你这是HW吗???")  # 输出标准日志
        sys.exit(0)  # 脚本退出


# 返回值 list[wskey]
def get_wskey():  # 方法 获取 wskey值 [系统变量传递]
    wskey_file = '/jd/config/account.json'
    with open(wskey_file, 'r') as f:
        data = json.load(f)

    json_data = []
    for item in data:
        pt_pin = item['pt_pin']
        ws_key = item['ws_key']
        remarks = item['remarks'] if item['remarks'] else ''
        json_item = f"pin={pt_pin};wskey={ws_key};"
        json_data.append((json_item, remarks))
    return json_data


# 返回值 bool
def check_ck(ck):  # 方法 检查 Cookie有效性 使用变量传递 单次调用
    searchObj = re.search(r'pt_pin=([^;\s]+)', ck, re.M | re.I)  # 正则检索 pt_pin
    if searchObj:  # 真值判断
        pin = searchObj.group(1)  # 取值
    else:  # 判断分支
        pin = ck.split(";")[1]  # 取值 使用 ; 分割
    if "WSKEY_UPDATE_HOUR" in os.environ:  # 判断 WSKEY_UPDATE_HOUR是否存在于环境变量
        updateHour = 23  # 更新间隔23小时
        if os.environ["WSKEY_UPDATE_HOUR"].isdigit():  # 检查是否为 DEC值
            updateHour = int(os.environ["WSKEY_UPDATE_HOUR"])  # 使用 int化数字
        nowTime = time.time()  # 获取时间戳 赋值
        updatedAt = 0.0  # 赋值
        searchObj = re.search(r'__time=([^;\s]+)', ck, re.M | re.I)  # 正则检索 [__time=]
        if searchObj:  # 真值判断
            updatedAt = float(searchObj.group(1))  # 取值 [float]类型
        if nowTime - updatedAt >= (updateHour * 60 * 60) - (10 * 60):  # 判断时间操作
            logger.info(str(pin) + ";即将到期或已过期\n")  # 标准日志输出
            return False  # 返回 Bool类型 False
        else:  # 判断分支
            remainingTime = (updateHour * 60 * 60) - (nowTime - updatedAt)  # 时间运算操作
            hour = int(remainingTime / 60 / 60)  # 时间运算操作 [int]
            minute = int((remainingTime % 3600) / 60)  # 时间运算操作 [int]
            logger.info(str(pin) + ";未到期，{0}时{1}分后更新\n".format(hour, minute))  # 标准日志输出
            return True  # 返回 Bool类型 True
    elif "WSKEY_DISCHECK" in os.environ:  # 判断分支 WSKEY_DISCHECK 是否存在于系统变量
        logger.info("不检查账号有效性\n--------------------\n")  # 标准日志输出
        return False  # 返回 Bool类型 False
    else:  # 判断分支
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion'  # 设置JD_API接口地址
        headers = {'Cookie': ck, 'Referer': 'https://home.m.jd.com/myJd/home.action', 'user-agent': ua}  # 设置 HTTP头
        try:  # 异常捕捉
            res = requests.get(url=url, headers=headers, verify=False, timeout=10, allow_redirects=False)  # 进行 HTTP请求[GET] 超时 10秒
        except Exception as err:  # 异常捕捉
            logger.debug(str(err))  # 调试日志输出
            logger.info("JD接口错误 请重试或者更换IP")  # 标准日志输出
            return False  # 返回 Bool类型 False
        else:  # 判断分支
            if res.status_code == 200:  # 判断 JD_API 接口是否为 200 [HTTP_OK]
                code = int(json.loads(res.text)['retcode'])  # 使用 Json模块对返回数据取值 int([retcode])
                if code == 0:  # 判断 code值
                    logger.info(str(pin) + ";状态正常\n")  # 标准日志输出
                    return True  # 返回 Bool类型 True
                else:  # 判断分支
                    logger.info(str(pin) + ";状态失效\n")
                    return False  # 返回 Bool类型 False
            else:  # 判断分支
                logger.info("JD接口错误码: " + str(res.status_code))  # 标注日志输出
                return False  # 返回 Bool类型 False


# 返回值 bool jd_ck
def getToken(wskey):  # 方法 获取 Wskey转换使用的 Token 由 JD_API 返回 这里传递 wskey
    try:  # 异常捕捉
        url = str(base64.b64decode(url_t).decode()) + 'api/genToken'  # 设置云端服务器地址 路由为 genToken
        header = {"User-Agent": ua}  # 设置 HTTP头
        params = requests.get(url=url, headers=header, verify=False, timeout=20).json()  # 设置 HTTP请求参数 超时 20秒 Json解析
    except Exception as err:  # 异常捕捉
        logger.info("Params参数获取失败")  # 标准日志输出
        logger.debug(str(err))  # 调试日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    headers = {'cookie': wskey, 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'charset': 'UTF-8', 'accept-encoding': 'br,gzip,deflate', 'user-agent': ua}  # 设置 HTTP头
    url = 'https://api.m.jd.com/client.action'  # 设置 URL地址
    data = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml%252fappjmp_blank.html%22%7D&'  # 设置 POST 载荷
    try:  # 异常捕捉
        res = requests.post(url=url, params=params, headers=headers, data=data, verify=False, timeout=10)  # HTTP请求 [POST] 超时 10秒
        res_json = json.loads(res.text)  # Json模块 取值
        tokenKey = res_json['tokenKey']  # 取出TokenKey
    except Exception as err:  # 异常捕捉
        logger.info("JD_WSKEY接口抛出错误 尝试重试 更换IP")  # 标准日志输出
        logger.info(str(err))  # 标注日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    else:  # 判断分支
        return appjmp(wskey, tokenKey)  # 传递 wskey, Tokenkey 执行方法 [appjmp]


# 返回值 bool jd_ck
def appjmp(wskey, tokenKey):  # 方法 传递 wskey & tokenKey
    wskey = "pt_" + str(wskey.split(";")[0])  # 变量组合 使用 ; 分割变量 拼接 pt_
    if tokenKey == 'xxx':  # 判断 tokenKey返回值
        logger.info(str(wskey) + ";疑似IP风控等问题 默认为失效\n--------------------\n")  # 标准日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    headers = {'User-Agent': ua, 'accept': 'accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'x-requested-with': 'com.jingdong.app.mall'}  # 设置 HTTP头
    params = {'tokenKey': tokenKey, 'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'}  # 设置 HTTP_URL 参数
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'  # 设置 URL地址
    try:  # 异常捕捉
        res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False, timeout=20)  # HTTP请求 [GET] 阻止跳转 超时 20秒
    except Exception as err:  # 异常捕捉
        logger.info("JD_appjmp 接口错误 请重试或者更换IP\n")  # 标准日志输出
        logger.info(str(err))  # 标准日志输出
        return False, wskey  # 返回 -> False[Bool], Wskey
    else:  # 判断分支
        try:  # 异常捕捉
            res_set = res.cookies.get_dict()  # 从res cookie取出
            pt_key = 'pt_key=' + res_set['pt_key']  # 取值 [pt_key]
            pt_pin = 'pt_pin=' + res_set['pt_pin']  # 取值 [pt_pin]
            if "WSKEY_UPDATE_HOUR" in os.environ:  # 判断是否在系统变量中启用 WSKEY_UPDATE_HOUR
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';__time=' + str(time.time()) + ';'  # 拼接变量
            else:  # 判断分支
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';'  # 拼接变量
        except Exception as err:  # 异常捕捉
            logger.info("JD_appjmp提取Cookie错误 请重试或者更换IP\n")  # 标准日志输出
            logger.info(str(err))  # 标准日志输出
            return False, wskey  # 返回 -> False[Bool], Wskey
        else:  # 判断分支
            if 'fake' in pt_key:  # 判断 pt_key中 是否存在fake
                logger.info(str(wskey) + ";WsKey状态失效\n")  # 标准日志输出
                return False, wskey  # 返回 -> False[Bool], Wskey
            else:  # 判断分支
                logger.info(str(wskey) + ";WsKey状态正常\n")  # 标准日志输出
                return True, jd_ck  # 返回 -> True[Bool], jd_ck


def update():  # 方法 脚本更新模块
    up_ver = int(cloud_arg['update'])  # 云端参数取值 [int]
    if ver >= up_ver:  # 判断版本号大小
        logger.info("当前脚本版本: " + str(ver))  # 标准日志输出
        logger.info("--------------------\n")  # 标准日志输出
    else:  # 判断分支
        logger.info("当前脚本版本: " + str(ver) + "新版本: " + str(up_ver))  # 标准日志输出
        logger.info("存在新版本, 请更新脚本后执行")  # 标准日志输出
        logger.info("--------------------\n")  # 标准日志输出
        text = '当前脚本版本: {0}新版本: {1}, 请更新脚本~!'.format(ver, up_ver)  # 设置发送内容
        hw_send(text)
        # sys.exit(0)  # 退出脚本 [未启用]


def hw_check(port):  # 方法 检查HW端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket模块初始化
    sock.settimeout(2)  # 设置端口超时
    try:  # 异常捕捉
        sock.connect(('127.0.0.1', port))  # 请求端口
    except Exception as err:  # 捕捉异常
        logger.debug(str(err))  # 调试日志输出
        sock.close()  # 端口关闭
        return False  # 返回 -> False[Bool]
    else:  # 分支判断
        sock.close()  # 关闭端口
        return True  # 返回 -> True[Bool]


def serch_ck(pin):  # 方法 搜索 Pin
    if not os.path.exists("cookie_export.sh"):
        os.system('task https://supermanito.github.io/Helloworld/scripts/cookie_export.sh now | grep -Ev "JD_COOKIE|^$" > /jd/config/cookie.txt')
    else:
        os.system('task cookie_export.sh now | grep -Ev "JD_COOKIE|^$" > /jd/config/cookie.txt')
    ck = open('/jd/config/cookie.txt', 'r')
    for line in ck.readlines():
        line_ck = re.sub(r'\n|,|"', '', line)
        if pin in line_ck:  # 判断line_ck
            logger.info(str(pin) + "检索成功\n")  # 标准日志输出
            return True, line_ck  # 返回 -> True[Bool], line_ck
        else:  # 判断分支
            continue  # 继续循环
    logger.info(str(pin) + "检索失败\n")  # 标准日志输出
    return False, 1  # 返回 -> False[Bool], 1


def hw_update(n_ck):  # 方法 HW更新变量 传递 cookie
    url = hw_url + 'openApi/updateCookie'
    data = {"cookie": n_ck}  # 设置 HTTP POST 载荷
    data = json.dumps(data)  # json模块格式化
    res = s.post(url=url, data=data).json()  # HTTP [PUT] 请求 使用 session
    return res


def cloud_info():  # 方法 云端信息
    url = str(base64.b64decode(url_t).decode()) + 'api/check_api'  # 设置 URL地址 路由 [check_api]
    for i in range(3):  # For循环 3次
        try:  # 异常捕捉
            headers = {"authorization": "Bearer Shizuku"}  # 设置 HTTP头
            res = requests.get(url=url, verify=False, headers=headers, timeout=20).text  # HTTP[GET] 请求 超时 20秒
        except requests.exceptions.ConnectTimeout:  # 异常捕捉
            logger.info("\n获取云端参数超时, 正在重试!" + str(i))  # 标准日志输出
            time.sleep(1)  # 休眠 1秒
            continue  # 循环继续
        except requests.exceptions.ReadTimeout:  # 异常捕捉
            logger.info("\n获取云端参数超时, 正在重试!" + str(i))  # 标准日志输出
            time.sleep(1)  # 休眠 1秒
            continue  # 循环继续
        except Exception as err:  # 异常捕捉
            logger.info("\n未知错误云端, 退出脚本!")  # 标准日志输出
            logger.debug(str(err))  # 调试日志输出
            sys.exit(1)  # 脚本退出
        else:  # 分支判断
            try:  # 异常捕捉
                c_info = json.loads(res)  # json读取参数
            except Exception as err:  # 异常捕捉
                logger.info("云端参数解析失败")  # 标准日志输出
                logger.debug(str(err))  # 调试日志输出
                sys.exit(1)  # 脚本退出
            else:  # 分支判断
                return c_info  # 返回 -> c_info


def check_cloud():  # 方法 云端地址检查
    url_list = ['aHR0cHM6Ly9hcGkubW9tb2UubWwv', 'aHR0cHM6Ly9hcGkubGltb2UuZXUub3JnLw==', 'aHR0cHM6Ly9hcGkuaWxpeWEuY2Yv']  # URL list Encode
    for i in url_list:  # for循环 url_list
        url = str(base64.b64decode(i).decode())  # 设置 url地址 [str]
        try:  # 异常捕捉
            requests.get(url=url, verify=False, timeout=10)  # HTTP[GET]请求 超时 10秒
        except Exception as err:  # 异常捕捉
            logger.debug(str(err))  # 调试日志输出
            continue  # 循环继续
        else:  # 分支判断
            info = ['HTTPS', 'Eu_HTTPS', 'CloudFlare']  # 输出信息[List]
            logger.info(str(info[url_list.index(i)]) + " Server Check OK\n--------------------\n")  # 标准日志输出
            return i  # 返回 ->i
    logger.info("\n云端地址全部失效, 请检查网络!")  # 标准日志输出
    hw_send('云端地址失效. 请联系作者或者检查网络.')  # 推送消息
    sys.exit(1)  # 脚本退出


def check_port():  # 方法 检查变量传递端口
    logger.info("\n--------------------\n")  # 标准日志输出
    port = 5678  # 默认5678端口
    if not hw_check(port):  # 调用方法 [hw_check] 传递 [port]
        logger.info(str(port) + "端口检查失败, 请查看端口是否填写错误，默认5678端口。")  # 标准日志输出
        logger.info("\n如果你很确定端口没错, 还是无法执行, 在GitHub给我发issus\n--------------------\n")  # 标准日志输出
        sys.exit(1)  # 脚本退出
    else:  # 判断分支
        logger.info(str(port) + "端口检查通过")  # 标准日志输出
        return port  # 返回->port


if __name__ == '__main__':  # Python主函数执行入口
    port = check_port()  # 调用方法 [check_port]  并赋值 [port]
    hw_url = 'http://127.0.0.1:{0}/'.format(port)
    token = hw_login()  # 调用方法 [hw_login]  并赋值 [token]
    s = requests.session()  # 设置 request session方法
    s.headers.update({"Content-Type": "application/json", "Authorization": "Bearer", "api-token": str(token)})  # 增加 HTTP头 json 类型
    url_t = check_cloud()  # 调用方法 [check_cloud] 并赋值 [url_t]
    cloud_arg = cloud_info()  # 调用方法 [cloud_info] 并赋值 [cloud_arg]
    update()  # 调用方法 [update]
    ua = cloud_arg['User-Agent']  # 设置全局变量 UA
    wslist = get_wskey()  # 调用方法 [get_wskey] 并赋值 [wslist]
    if "WSKEY_SLEEP" in os.environ and str(os.environ["WSKEY_SLEEP"]).isdigit():  # 判断变量[WSKEY_SLEEP]是否为数字类型
        sleepTime = int(os.environ["WSKEY_SLEEP"])  # 获取变量 [int]
    else:  # 判断分支
        sleepTime = 10  # 默认休眠时间 10秒
    for ws, remark in wslist:  # wslist变量 for循环  [wslist -> ws]
        #logger.info(f"remark:{remark},wskey:{ws}")
        wspin = ws.split(";")[0]  # 变量分割 ;
        if "pin" in wspin:  # 判断 pin 是否存在于 [wspin]
            wspin = "pt_" + wspin + ";"  # 封闭变量
            return_serch = serch_ck(wspin)  # 变量 pt_pin 搜索获取 key eid
            if return_serch[0]:  # bool: True 搜索到账号
                jck = str(return_serch[1])  # 拿到 JD_COOKIE
                if not check_ck(jck):  # bool: False 判定 JD_COOKIE 有效性
                    tryCount = 1  # 重试次数 1次
                    if "WSKEY_TRY_COUNT" in os.environ:  # 判断 [WSKEY_TRY_COUNT] 是否存在于系统变量
                        if os.environ["WSKEY_TRY_COUNT"].isdigit():  # 判断 [WSKEY_TRY_COUNT] 是否为数字
                            tryCount = int(os.environ["WSKEY_TRY_COUNT"])  # 设置 [tryCount] int
                    for count in range(tryCount):  # for循环 [tryCount]
                        count += 1  # 自增
                        return_ws = getToken(ws)  # 使用 WSKEY 请求获取 JD_COOKIE bool jd_ck
                        if return_ws[0]:  # 判断 [return_ws]返回值 Bool类型
                            break  # 中断循环
                        if count < tryCount:  # 判断循环次
                            logger.info("{0} 秒后重试，剩余次数：{1}\n".format(sleepTime, tryCount - count))  # 标准日志输出
                            time.sleep(sleepTime)  # 脚本休眠 使用变量 [sleepTime]
                    if return_ws[0]:  # 判断 [return_ws]返回值 Bool类型
                        nt_key = str(return_ws[1])  # 从 return_ws[1] 取出 -> nt_key
                        # logger.info("wskey转pt_key成功", nt_key)  # 标准日志输出 [未启用]
                        logger.info(f"{wspin}WsKey转换成功\n")  # 标准日志输出
                        text = "账号:{0}备注:{1};转换成功".format(wspin, remark)
                        res = hw_update(nt_key)  # 函数 hw_update 参数  JD_COOKIE
                        if res["code"] == 1:
                            logger.info("账号:{0}备注:{1};HW面板更新成功\n".format(wspin, remark))
                    else:  # 判断分支
                        logger.info(str(wspin) + "账号失效")  # 标准日志输出
                        text = "账号:{0}备注:{1};WsKey疑似失效".format(wspin, remark)  # 设置推送内容
                        hw_send(text)
                    logger.info("--------------------\n")  # 标准日志输出
                    logger.info("暂停{0}秒\n".format(sleepTime))  # 标准日志输出
                    time.sleep(sleepTime)  # 脚本休眠
                else:  # 判断分支
                    logger.info(str(wspin) + "账号有效")  # 标准日志输出
                    logger.info("--------------------\n")  # 标准日志输出
        else:  # 判断分支
            logger.info("WSKEY格式错误\n--------------------\n")  # 标准日志输出
    logger.info("执行完成\n--------------------")  # 标准日志输出
    sys.exit(0)  # 脚本退出
    # Enjoy

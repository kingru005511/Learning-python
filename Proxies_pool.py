# -*- encoding=utf-8 -*-
# python3.6


import requests
from lxml import etree
import re
import time
import random
import telnetlib
import pymysql
import typing
result: typing.Optional[requests.Response] = None


# 检查代理是否可用

# def check(ip, port):
#     try:
#         telnetlib.Telnet(ip, port, timeout=2)
#
#
#     except:
#         False
#
#     else:
#         True

def check(http_https, ip, port):
    try:
        # IP = random.choice(IPAgents)
        proxy = f"{http_https}://{ip}:{port}"
        # thisIP = "".join(IP.split(":")[0:1])
        # print(thisIP)
        res = requests.get(url="http://icanhazip.com/", timeout=2, proxies={http_https: proxy})
        proxyIP = res.text
        if (proxyIP == proxy):
            print("代理IP:'" + proxyIP + "'有效！")
            return True
        else:
            print("代理" + proxyIP + "无效！")
            return False
    except:
        print("代理IP无效！")
        return False



headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
        }
# 伪装成浏览器


def get_agent():   # 绕过反爬虫
    agents = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
    ]
    User_Agents = {}
    User_Agents['User-agent'] = agents[random.randint(0, len(agents)-1)]
    return User_Agents



def get_proxies(max_page):   # 爬取多少页   快代理
    proxy_list = []
    for i in range(1, max_page+1):
        url = 'https://www.kuaidaili.com/free/inha/{}/'.format(i)
        response = requests.get(url, headers=get_agent())
        time.sleep(2)
        # print(response.content.decode('utf-8'))
        # for i in response:
        #     print(i)
        html = response.content.decode('utf-8')
        info = etree.HTML(html)
        global proxies
        proxies = info.xpath('//td[@data-title="IP"]/text()')   # IP地址
        # for proxy in proxies:
        #     print(proxy)
        global ports
        ports = info.xpath('//td[@data-title="PORT"]/text()')    # port端口
        # for port in ports:
        #     print(port)
        global anonymous
        anonymous = info.xpath('//td[@data-title="匿名度"]/text()')    # 匿名形式
        # for a in anonymous:
        #     print(a)
        global http_https
        http_https = info.xpath('//td[@data-title="类型"]/text()')   # https or http
        # for http in http_https:
        #     print(http)
        global location
        location = info.xpath('//td[@data-title="位置"]/text()')    # 位置

        global speed
        speed = info .xpath('//td[@data-title="响应速度"]/text()')     # 响应速度

        # last_time = info.xpath('//td[@data-title="最后验证时间"]/text()')      # 最后验证时间

    # cnt = int(0)

    for i in range(0, len(proxies)-1):
        if check(http_https[i], proxies[i], ports[i]):
            pass

        else:
            # http_https.remove(http_https[i])
            # proxies.remove(proxies[i])
            # ports.remove(ports[i])
            anonymous[i] = '无效IP'
            # location.remove(location[i])
            # speed.remove(speed[i])
            # print("删除")
        #     proxy_list[i] = {
        #         'IP地址': proxies[i]+ports[i],
        #         '匿名形式': anonymous[i],
        #         '服务': http_https[i],
        #         '位置': location[i],
        #         '响应速度': speed[i]
        #         # '最后验证时间': last_time[i]
        #     }
        #     print("加入字典ing")
        #     # print(proxy_list)
        # else:
        #     print("丢弃不可使用的代理ing")


    # return proxy_list

    connect_mysql(proxies, ports, anonymous, http_https, location, speed)


def connect_mysql(proxies, ports, anonymous, http_https, location, speed):

        conn = pymysql.connect(
            host='127.0.0.1', user='root', password='root', database='proxy_pool'
        )   # 打开数据库连接
        cursor = conn.cursor()
        cursor.execute("use proxy_pool;")
        cursor.execute('''
            CREATE TABLE if not exists proxy(
            id int primary key auto_increment,
            iP varchar(20),
            port varchar(10),
            anonymous varchar(20),
            type1 varchar(10),
            location varchar(20),
            speed varchar(20));
        ''')
        for a, b, c, d, e, f in zip(proxies, ports, anonymous, http_https, location, speed):
            if a and b and c and d and e and f:
                cursor.execute('''insert into proxy(
                               iP,
                               port,
                               anonymous,
                               type1,
                               location,
                               speed) values("%s","%s","%s","%s","%s","%s");''' % (a, b, c, d, e, f))
                cursor.execute('''
                    DELETE FROM proxy where anonymous='无效IP';  
                ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("已生成！")



if __name__ == '__main__':
    get_proxies(max_page=2)

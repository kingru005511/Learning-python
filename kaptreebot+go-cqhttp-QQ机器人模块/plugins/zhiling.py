import os
from ctypes import Union

from nonebot.permission import SUPERUSER
from requests_html import HTMLSession
import requests
from nonebot import on_command
from nonebot import on_keyword,on_message
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event, Message, unescape
import random
from aiocqhttp import MessageSegment
import json

kiss=['么么哒','不要这样嘛!','你好讨厌哦!','你好坏哦，欺负呆毛，哼！','不要酱紫嘛','一天没和你聊天，就觉得哪里不对劲！','快亲亲人家啦!!','不理你了，真讨厌。','呆毛不要了啦!','你今天有没有想念呆毛呀!',
      '别这样啦，呆毛是个女孩子嘛!','(✿◡‿◡)','(*/ω＼*)','つ﹏⊂','ヾ(≧O≦)〃嗷~','(>▽<)，好呀','恶心心','mu--a','可以教呆毛写代码吗','记得AK比赛哦','能AK比赛吗？']

music_=['http://music.163.com/song/media/outer/url?id=1817935489.mp3','http://music.163.com/song/media/outer/url?id=1816835031.mp3','http://music.163.com/song/media/outer/url?id=1813913037.mp3',
        'http://music.163.com/song/media/outer/url?id=1813389565.mp3','http://music.163.com/song/media/outer/url?id=452986458.mp3',]

# 获取图片
def get_meitu():
    url='https://api.iyk0.com/ecy/api.php'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url,headers=headers)
    c = res.url
    return c
# COS图片
def get_cos():
    url="https://api.iyk0.com/cos"
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url,headers=headers)
    c = res.url
    return c

# MC酱的表情包
def get_mc():
    url='https://api.ixiaowai.cn/mcapi/mcapi.php'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url,headers=headers)
    c = res.url
    return c


# 有一定概率刷出R18的图
def get_R18():
    url='https://api.lolicon.app/setu/v2?tag=白丝|黑丝&r18=1'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url,headers=headers)
    res = res.json()
    c = res['data'][0]['urls']['original']
    return c

# https://api.yimian.xyz/img?type=moe&size=1920x1080
def get_setu():
    # 萝莉|少女
    url='https://api.lolicon.app/setu/v2?tag=白丝|黑丝&少女|萝莉'
    proxies = {"http": None, "https": None}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url,headers=headers,proxies=proxies,timeout=5)
    res = res.json()
    c = res['data'][0]['urls']['original']
    return c


# 毒鸡汤语录
def get_dujit():
    url='https://du.liuzhijin.cn/'
    session = HTMLSession()
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
    r = session.get(url,headers=headers)
    sel ='#text'
    s = r.html.find(sel)
    str1 = s[0].text
    print('毒鸡汤+',str1)
    return str1


# 朋友圈文案
def get_wenan():
    url='https://pyq.shadiao.app/api.php'
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
    t = requests.get(url,headers=headers)
    c = t.text
    print('朋友圈文案',c)
    return c


# 彩虹屁
def get_caihongpi():
    url='https://chp.shadiao.app/api.php'
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
    t = requests.get(url,headers=headers)
    c = t.text
    print('彩红屁',c)
    return c


# 网易语录
def get_wangyi():
    url ='https://v1.hitokoto.cn/?c=j&c=k'
    res = requests.get(url)
    c = json.loads(res.text)
    ans = c['hitokoto']+'---->'+c['from']
    print(ans)
    return ans


explain = on_command("我要亲亲",aliases={'我要抱抱','抱抱呆毛','亲亲呆毛','抱呆毛','亲呆毛'} ,priority=2)
@explain.handle()
async def explainsend(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        k = (random.randint(0,10000)+random.randint(0,10000))%len(kiss)
        s = kiss[k]
        print('kiss总数目',len(kiss),'我要抱抱指令输出:',s)
        await bot.send(
            event=event,
            message=s,
            at_sender=True
        )

cos = on_keyword({'cos图'},priority=2)
@cos.handle()
async def cos_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message=MessageSegment.image(get_cos())
        )


st = on_keyword({'setu','涩图','色图'}, priority=2)
@st.handle()
async def st_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message=MessageSegment.image(get_setu())
        )



R18 = on_keyword({'R18','r18'}, priority=2)
@R18.handle()
async def R18_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message=MessageSegment.image(get_R18()),
        )

meitu = on_keyword({'壁纸','美图','每日一图'},priority=2)
@meitu.handle()
async def meitu_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message=MessageSegment.image(get_meitu()),
        )

mc = on_keyword(['mc表情包','MC酱','Mc酱','mC酱',"mc酱"],priority=2)
@mc.handle()
async def mcpo(bot: Bot,event: Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message=MessageSegment.image(get_mc()),
            at_sender=True
        )


dudu = on_keyword(['毒鸡汤'],priority=2)
@dudu.handle()
async def getdu_(bot:Bot,event:Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        str1 = str(get_dujit())
        await bot.send(
            event=event,
            message= str1,
            at_sedner=True
        )


wangyi = on_command('开始网抑',priority=2)
@wangyi.handle()
async def wangyi_(bot:Bot,event:Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        str1 = str(get_wangyi())
        await bot.send(
            event=event,
            message= str1,
            at_sedner=True
        )


caihong = on_command('彩虹屁',priority=2)
@caihong.handle()
async def caihong_(bot:Bot,event:Event,state: dict):
        str1 = str(get_caihongpi())
        await bot.send(
            event=event,
            message= str1,
            at_sedner=True
        )


pyqwenan= on_command('朋友圈文案',priority=2)
@pyqwenan.handle()
async def pyqwenan_(bot:Bot,event:Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        str1 = str(get_wenan())
        await bot.send(
            event=event,
            message= str1,
            at_sedner=True
        )


master = on_keyword(['主人','你是谁的?'],priority=2)
@master.handle()
async def master_(bot:Bot,event: Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        await bot.send(
            event=event,
            message='我是大家的哦，请大家爱护我，不要对我说一些奇怪的话'
        )

help = on_command("查看说明",aliases={'help','帮助','使用说明'},priority=2)
@help.handle()
async def help_(bot:Bot,event: Event,state: dict):
    if int(event.get_user_id()) != event.self_id:
        path_ = os.getcwd()
        path_ = path_ + '\help.png'
        mypath = 'file:///' + path_
        print(mypath)
        await bot.send(
            event=event,
            message=MessageSegment.image(mypath)
        )
zhibo= on_command('$直播',priority=2)
@zhibo.handle()
async def zhibo_(bot:Bot,event:Event,state: dict):
    print(event.get_user_id())
    print(event.self_id)
    if int(event.get_user_id()) != event.self_id:
        str1 = '主人，您订阅的直播间开播辣，快来看看叭\n地址:https://live.bilibili.com/2996078'
        await bot.send(event=event,group_id = 913088980,message=str1)

# test = on_command('test',priority=2)
# @test.handle()
# async def test_(bot:Bot,event:Event,state: dict):
#     url = 'https://api.iyk0.com/60s'
#     r = requests.get(url)
#     result = json.loads(r.content)
#     message = result['imageUrl']
#     print(message)
#     await bot.send(
#         event=event,
#         message=MessageSegment.image(message)
#     )
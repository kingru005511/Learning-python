import requests
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event, Message
import random
from aiocqhttp import MessageSegment
import json
# md5反查
async def get_md5(text:str):
    url= ('https://api.iyk0.com/md5/dec/?md5='+text)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    r =requests.get(url,headers=headers)
    result = json.loads(r.content)
    result = "md5解码:"+ result['text']
    print(result)
    return result

MD5_Decode = on_command("md5解码",aliases={"md5解密"},priority=2)
@MD5_Decode.handle()
async def MD5_Decode_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
        if args:
            state["md5"] = args  # 如果用户发送了参数则直接赋值

@MD5_Decode.got("md5", prompt="你要解码的md5加密值是啥(@_@)...")
async def handle_MD5_Decode(bot: Bot, event: Event, state: dict):
    md5 = state["md5"]
    md5_decode = await get_md5(md5)
    await bot.send(
        event =event,
        message=MessageSegment.text(md5_decode)
    )
# url= ('https://api.iyk0.com/md5/dec/?md5='+'f379eaf3c831b04de153469d1bec345e')
# r =requests.get(url)
# result = json.loads(r.content)
# result = "md5解码: "+result['text']
# print(result)

# md5加密
async def get_md5_encoding(text:str):
    url= ('https://api.iyk0.com/md5/?msg='+text)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    r =requests.get(url,headers=headers)
    result = json.loads(r.content)
    result = "md5加密:"+ result['data']
    print(result)
    return result

MD5_encoding = on_command("md5加密",priority=2)
@MD5_encoding.handle()
async def MD5_Encoding_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
        if args:
            state["txt"] = args  # 如果用户发送了参数则直接赋值

@MD5_encoding.got("txt", prompt="你要进行md5加密的字符串是啥(@_@)...")
async def handle_MD5_Encoding(bot: Bot, event: Event, state: dict):
    txt = state["txt"]
    md5_encoding = await get_md5_encoding(txt)
    await bot.send(
        event =event,
        message=MessageSegment.text(md5_encoding)
    )
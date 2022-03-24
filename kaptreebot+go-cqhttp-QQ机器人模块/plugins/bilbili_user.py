import urllib.request
import gzip
import json
import requests
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event
from aiocqhttp import MessageSegment

async def get_uid(id:str):
    url = ('https://api.iyk0.com/bilibili/user/?mid='+id)
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    r = requests.get(url,headers=headers)
    result = json.loads(r.content)
    if result['code'] != 200:
        return f"未搜索到该b站用户哟♥~"
    elif result['code'] == 200:
        user_detial = "B站用户id: " + str(result['mid']) + '\n'\
                    + "B站姓名: " + result['name'] + '\n'\
                    + "B站留言: " + result['sign'] + '\n'\
                    + "B站性别: " + result['sex'] + '\n'\
                    + "B站等级: " + str(result['level']) + '\n'\
                    + "B站封禁状态: " + result['silence'] + '\n'\
                    + "B站生日: " + result['birthday'] + '\n'\
                    + "B站认证类型: " + result['role'] + '\n'\
                    + "B站认证信息: " + result['title'] + '\n'\
                    + "B站会员类型文案: " + result['vip_text'] + '\n'\
                    + "B站会员状态: " + result['vip_status'] + '\n'\
                    + "B站会员类型: " + result['vip_type'] + '\n'\
                    + "B站会员过期时间: " + result['vip_due_date'] + '\n'\
                    + "B站会员名称颜色: " + result['vip_nickname_color'] + '\n'\
                    + "B站直播间状态: " + result['live_status'] + '\n'\
                    + "B站直播状态: " + result['live_bf'] + '\n'\
                    + "B站直播间网址: " + result['live_url'] + '\n'\
                    + "B站直播间标题: " + result['live_title'] + '\n'\
                    + "B站直播间人气: " + str(result['live_online']) + '\n'
        # + "B站头像: " + result['face'] + '\n'\
        return user_detial


User = on_command("b站用户ID",aliases={"b站uid","bilibilimid","b站id"},priority=2)
@User.handle()
async def User_(bot: Bot, event: Event, state: dict):
    if int(event.get_user_id()) != event.self_id:
        args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
        if args:
            state["id"] = args  # 如果用户发送了参数则直接赋值

@User.got("id", prompt="你要搜索的B站用户ID是啥(@_@)...")
async def handler_User(bot: Bot, event: Event, state: dict):
    id = state["id"]
    User = await get_uid(id)
    await bot.send(
        event=event,
        message=MessageSegment.text(User)
    )

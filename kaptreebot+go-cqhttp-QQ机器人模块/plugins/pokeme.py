from nonebot import on_notice
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, PokeNotifyEvent,LuckyKingNotifyEvent,GroupRecallNoticeEvent
from nonebot.adapters.cqhttp.message import Message
import random
from aiocqhttp import MessageSegment

a = ['那...那里...那里不能戳...绝对...','嘤嘤嘤,好疼','你再戳，我就把你的作案工具没收了，哼哼~','别戳了别戳了，戳怀孕了',
   '嘤嘤嘤，人家痛痛','我错了我错了，别戳了','桥豆麻袋,别戳老子','手感怎么样','戳够了吗？该学习了','戳什么戳，没戳过吗',
   '你用左手戳的还是右手戳的？','不要啦，别戳啦','给你一拳','再摸就是狗','你这么闲吗？','代码写完了吗？','你能AK WF吗？','爬去学习']

pre = 0
poke=on_notice()
@poke.handle()
async def _(bot:Bot,event:Event):
    if isinstance(event,PokeNotifyEvent):
        if event.is_tome() and event.user_id !=event.self_id:
            l = len(a)
            k = random.randint(0,l-1)
            while pre == k:
                k = random.randint(0,l-1)
            last = k
            await bot.send(
                event=event,
                message=a[k],
                at_sender=True
            )

chehui = on_notice()
@chehui.handle()
async def cheh(bot:Bot,event:GroupRecallNoticeEvent):
    print(event.self_id)
    # print(event.user_id)
    if event.operator_id == event.user_id:
        await bot.send(
                event=event,
                message='喜欢呆毛就直说啊,我还没说不同意呢~',
                at_sender=True
              )

regbag = on_notice()
@regbag.handle()
async def redb(bot:Bot,event:LuckyKingNotifyEvent):
    atmsg = MessageSegment.at(event.target_id)
    await bot.send(
        event=event,
        message = atmsg+'恭喜你是运气王，请立即红包接力，不要不识好歹',
    )

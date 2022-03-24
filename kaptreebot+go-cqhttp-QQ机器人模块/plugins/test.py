import json
import requests
# 查询备案
url = "https://api.iyk0.com/bilibili/user/?mid="
text = "123456"
header = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
    'referer':'www.baidu.com'
}
url = url + text
res = requests.get(url,headers=header)
result = json.loads(res.content)
# print(result)
print(type(result['code']))
# mid = "B站用户id: " + str(result['mid']) + '\n'
# name = "B站姓名: " + result['name'] + '\n'
# face = "B站头像: " + result['face'] + '\n'
# sign = "B站留言: " + result['sign'] + '\n'
# sex = "B站性别: " + result['sex'] + '\n'
# level = "B站等级: " + str(result['level']) + '\n'
# silence = "B站封禁状态: " + result['silence'] + '\n'
# birthday = "B站生日: " + result['birthday'] + '\n'
# role = "B站认证类型: " + result['role'] + '\n'
# title = "B站认证信息: " + result['title'] + '\n'
# vip_text = "B站会员类型文案: " + result['vip_text'] + '\n'
# vip_status = "B站会员状态: " + result['vip_status'] + '\n'
# vip_type= "B站会员类型: " + result['vip_type'] + '\n'
# vip_due_date = "B站会员过期时间: " + result['vip_due_date'] + '\n'
# vip_nickname_color = "B站会员名称颜色: " + result['vip_nickname_color'] + '\n'
# live_status = "B站直播间状态: " + result['live_status'] + '\n'
# live_bf = "B站直播状态: " + result['live_bf'] + '\n'
# live_url = "B站直播间网址: " + result['live_url'] + '\n'
# live_title = "B站直播间标题: " + result['live_title'] + '\n'
# live_online = "B站直播间人气: " + str(result['live_online']) + '\n'
# print(mid+name+face+sign+sex+level+silence+birthday+role+title+vip_text+vip_status+vip_type+vip_due_date+vip_nickname_color+live_status+live_bf+live_title+live_url+live_online)

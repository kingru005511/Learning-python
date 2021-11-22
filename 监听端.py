# coding:utf-8
# python3
# by 此意系

import socket
import time


# 写入文件
def write_file(word):
    f = open(r"C:\Users\ASUS\Desktop\password.txt", "a+", encoding="utf-8")
    f.write(word)


MaxBytes = 1024 * 1024  # 最大字节
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.settimeout(60)
# host = '192.168.1.18'
host = socket.gethostname()  # 获取本机ip
port = 2828
server.bind((host, port))  # 绑定端口

server.listen(1)  # 监听
try:
    client, addr = server.accept()  # 等待客户端连接
    print(addr, " 连接成功！\n")
    while True:
        data = client.recv(MaxBytes)
        localTime = time.asctime(time.localtime(time.time()))
        print(localTime, ' 接收到数据字节数:', len(data))
        write_file(data.decode())  # 调用写入函数
        print(data.decode())

except BaseException as e:
    print("出现异常：%s" % e)

finally:
    server.close()  # 关闭连接
    print("连接已断开！！")

# coding=utf-8
# python3
# by 此意系

import socket
ip = str(input("请输入对方服务器IP:"))
port = input("请输入对方服务器port:")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 连接对方使用tcp协议 对象建立
s.connect((ip, port))  # 连接

while True:
    data = input("请输入命令:")
    data = bytes(data, encoding="utf-8")
    s.send(data)   # 发送数据给对方
    data2 = s.recv(1024) # 接收返回的数据
    print(str(data2, encoding="utf-8"))
    if data == b"q":
        break

s.close()
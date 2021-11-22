# coding=utf-8
# python3
# by 此意系

import pexpect

# SSH连接成功时的命令行交互窗口中前面的提示字符的集合
PROMPT = ['# ', '>>> ', '> ', '\$ ']


def send_command(child, cmd):
    # 发送一条命令
    child.sendline(cmd)

    # 期望有命令行提示字符出现
    child.expect(PROMPT)

    # 将之前的内容都输出
    print(child.before)


def connect(user, host, password):
    # 表示主机已使用一个新的公钥的消息
    ssh_newkey = 'Are you sure you want to continue connecting'
    connStr = 'ssh ' + user + '@' + host

    # 为ssh命令生成一个spawn类的对象
    child = pexpect.spawn(connStr)

    # 期望有ssh_newkey字符、提示输入密码的字符出现，否则超时
    ret = child.expect([pexpect.TIMEOUT, ssh_newkey, '[P|p]assword: '])

    # 匹配到超时TIMEOUT
    if ret == 0:
        print('[-] Error Connecting')
        return

    # 匹配到ssh_newkey
    if ret == 1:
        # 发送yes回应ssh_newkey并期望提示输入密码的字符出现
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT, '[P|p]assword: '])

    # 匹配到超时TIMEOUT
    if ret == 0:
        print('[-] Error Connecting')
        return

    # 发送密码
    child.sendline(password)
    child.expect(PROMPT)
    return child


def main():
    host = str(input("请输入目标IP:"))
    user = str(input("请输入目标用户名:"))
    password = str(input("请输入目标密码:"))
    child = connect(user, host, password)
    send_command(child, 'uname -a')  # 命令


if __name__ == '__main__':
    main()

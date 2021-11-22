# coding=utf-8
# by 此意系
# python3

import crypt

def main():
    with open('/etc/shadow','r') as f1 :         #获取/etc/shadow中的内容
        with open('C:/Users/Administrator/Desktop/passwd.txt','a') as f2:
            f2.write(str(f1))

    passFile = open('passwd.txt','r')
    for line in passFile.readlines():
        if ":" in line:
            username = line.split(':')[0] #分离出用户名和密码字段
            password = line.split(':')[1].strip(' ')
            print ("[*] Cracking Password For "+username)
            GetPass(password)
    passFile.close()

def GetPass(password):
    salt = password[:password.rindex('$')+1]
    print(salt)
    dictFile = open('dictionary.txt','r')
    for passwd in dictFile.readlines():
        passwd = passwd.strip('\n')
        cryptpass = crypt.crypt(passwd,salt)
        if cryptpass == password:
            print ("[+] Found Password:"+passwd+"\n")
            return
    print ("[+] Not Found Password")

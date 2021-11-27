# coding=utf-8
# python3
# by 此意系

import paramiko

ssh = paramiko.SSHClient()   # 创建一个客户端
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)     # 消除报错    陌生测机器也可以连接
ssh.connect(hostname='192.168.1.101',username='root',password='toor')
stdin,stdout,stderr = ssh.exec_command('df')
print(stdout.read())
ssh.close()
# 上述测试试简单的登录
# 下面开始文件的上传和下载
transport = paramiko.Transport('192.168.1.101',22)     # 连接IP和Port  创建一个隧道
transport.connect(username='root',password='toor')
sftp = paramiko.SFTPClient.from_transport(transport)     # 创建一个SFTP对象
sftp.get('f1','f1')     # 从服务器 把名字为f1文件 传输到本机 取名叫f1
sftp.put('test','data')    # 将本机的test文件 传输到服务器 取名叫data
sftp.close()



# 当本机存在ssh的RSA钥匙
privatekey = 'c:/key/id_rsa'
key = paramiko.RSAKey.from_private_key_file(privatekey)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
ssh.connect(hostname='192.168.1.101',username='root',pkey=key)
# 就可以进行无密码登录
ssh.exec_command('ls -lh')
ssh.close()

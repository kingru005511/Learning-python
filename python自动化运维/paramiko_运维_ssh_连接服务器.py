# coding=utf-8
# python3
# by 此意系

import paramiko

# 创建一个实例
ssh_client = paramiko.SSHClient()
# 下面进行设置
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)       # 屏蔽错误
# 以下是连接部分
ssh_client.connect(hostname='192.168.1.101',username='root',password='toor')
stdin,stdout,stderr = ssh_client.exec_command('ls -lh')       # 执行的命令
print(stdout.read)
print('\n')
stdin,stdout,stderr = ssh_client.exec_command('free -m')    # 查看内存使用率
print(stdout.read())
ssh_client.close()        # 关闭


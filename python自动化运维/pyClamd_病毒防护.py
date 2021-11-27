# coding=utf-8
# python3
# by 此意系

# https://dandelioncloud.cn/article/details/1420385626700189697 学习的链接
import sys

import pyclamd
import os
import time
import platform
from threading import Thread
if(platform.system()=='Windows'):
    pass
elif(platform.system()=='Linux'):
    print("将为您打开'/etc/clamd',请输入该配置文件的TCPsocket端口...")
    time.sleep(1)
    print(os.system('cat /etc/clamd.conf'))
    time.sleep(1)
    port = int(input('TCPsoketPort:'))
    while port not in range(0,66535):
        print("输入端口出错!")
        port = int(input('TCPsoketPort:'))
    else:
        print("输入端口成功!端口Port为:" + str(port))
    try:
        TargetIP=str(input("请输入连接主机的IP:"))
        class Scan(Thread):  # 继承多线程Thread类
            def __init__(self,IP,scan_type,file):
                Thread.__init__(self)
                self.IP = IP
                self.scan_type = scan_type
                self.file = file
                self.constr = ""
                self.scanresult = ""
            def run(self):    # 多进程run方法
                try:
                    cd = pyclamd.ClamdNetworkSocket(self.IP,3310)
                    # 探测连通性
                    if(cd.ping()):
                        self.constr = self.IP+" connection [OK]"
                    # 重载clamd病毒特征库
                        cd.reload()
                    # 判断扫描模式
                        if(self.scan_type=="contscan_file"):
                            self.scanresult="{0}\n".format(cd.contscan_file(self.file))
                        elif(self.scan_type=='multiscan_file'):
                            self.scanresult="{0}\n".format(cd.multiscan_file(self.file))
                        elif(self.scan_type=='scan_file'):
                            self.scanresult="{0}\n".format(cd.scan_file(self.file))
                        time.sleep(1)
                    else:
                        self.constr = self.IP+" ping error,exit"
                        return
                except Exception as e:
                    self.constr=self.IP+" "+str(e)
        IPs=['192.168.1.101','192.168.1.100']     # 扫描主机的列表
        scantype = "multiscan_file"      # 指定扫描模式，支持multiscan_file、contscan_file、scan_file
        scanfile = "/usr/local/bin"      # 指定扫描目录
        i=1
        threadnum=2       # 指定线程数
        scanlist = []     # 存储Scan类线程对象列表
        for ip in IPs:
                # 将数据值代入类中，实例化对象
            currp = Scan(ip,scantype,scanfile)
            scanlist.append(currp)       # 追加对象到列表
            # 当达到指定的线程数或IP列表数后启动线程
            if(i%threadnum==0 or i==len(IPs)):
                for task in scanlist:
                    task.start()   # 启动线程
                for task in scanlist:
                    task.join()    # 等待所有子线程退出，并输出扫描结果
                    print(task.constr)   # 打印服务器连接信息
                    print(task.scanresult)   # 打印结果信息
    except Exception as e:
        print(e)

else:
    print('其他系统')


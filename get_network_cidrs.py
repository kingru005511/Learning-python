#!/usr/bin/env python3
import ipaddress
import psutil

def get_network_cidrs():
    """
    返回一个列表，包含当前所有非回环 IPv4 接口的网络段（CIDR 格式）
    """
    cidrs = []
    for iface, addrs in psutil.net_if_addrs().items():
        for snic in addrs:
            # 只处理 IPv4，且排除回环地址
            if snic.family.name == 'AF_INET' and not snic.address.startswith('127.'):
                # 构造网络对象（strict=False：主机地址也能创建网络）
                net = ipaddress.IPv4Network(f"{snic.address}/{snic.netmask}", strict=False)
                cidrs.append(f"{net.network_address}/{net.prefixlen}")
    return cidrs

if __name__ == "__main__":
    for cidr in get_network_cidrs():
        print(cidr)

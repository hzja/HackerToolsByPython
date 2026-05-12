"""
author:Byt3h
refer: 《python黑帽子》
usage: "python Sniffer.py"
"""

import socket
import os

# 主机的内网IP
Host = "192.168.223.1"

def main():
    # 判断是否是Windows系统，选择不同的协议
    if os.name == "nt":
        SocketProtocol = socket.IPPROTO_IP
    else:
        SocketProtocol = socket.IPPROTO_ICMP
    
    # 创建嗅探器
    Sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, SocketProtocol)
    Sniffer.bind((Host, 0))
    
    # 在抓包中包含IP头
    Sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    
    if os.name == "nt":
        # 发送IOCTL消息启用网卡的混杂模式
        Sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    print(Sniffer.recvfrom(65565))
    
    if os.name == "nt":
        # 发送IOCTL消息停用网卡的混杂模式
        Sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        
if __name__ == "__main__":
    main()
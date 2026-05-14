"""
author:Byt3h
referer:>《python黑帽子》
bug:无法成功抓取到数据包，不清楚是什么问题，需要查找一下bug
"""
import ipaddress
import os
import socket
import struct
import sys
import time

class IP:
# 定义IP头数据结构
    def __init__(self, buff=None):
        header = struct.unpack("BBHHHBBH4s4s", buff)
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF
        
        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.checksum = header[7]
        self.src = header[8]
        self.dst = header[9]
        
        # 人类可读IP地址
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)
        
        # 映射协议约束到它们的名称
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print("%s No protocol for %s" %(e, self.protocol_num))
            self.protocol = str(self.protocol_num)
        
class ICMP:
# 定义ICMP协议数据结构
    def __init__(self, buff):
        header = struct.unpack("<BBHHH", buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]
        
def sniff(Host):
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

    try:
        while True:
            #读取包的内容
            raw_buffer = Sniffer.recvfrom(65535)[0]

            #从初始的20字节创建一个IP头
            ip_header = IP(raw_buffer[0:20])
            
            #获取当前时间
            CurTime = time.strftime("%H:%M:%S", time.localtime())

            # 打印被检测到的协议和链路
            print("当前时间：%s 协议：%s 链路：%s -> %s" % (CurTime, ip_header.protocol, ip_header.src_address, ip_header.dst_address))
            
            # 解析ICMP包
            if(ip_header.protocol == "ICMP"):
                print("协议： %s 链路：%s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
                print(f"版本:{ip_header.ver}")
                print(f"头长度：{ip_header.ihl} TTL:{ip_header.ttl}")
                
                # 计算ICMP包从哪里开始，IP头的长度是基于IP头中的ihl字段计算的，该字段
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset : offset + 8]
                # 创造ICMP结构
                icmp_header = ICMP(buf)
                print("ICMP -> 类型：%s, 代码：%s\n" % (icmp_header.type, icmp_header.code))

    except KeyboardInterrupt:
        if os.name == "nt":
            # 发送IOCTL消息停用网卡的混杂模式
            Sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = "192.168.1.8"
    sniff(host)
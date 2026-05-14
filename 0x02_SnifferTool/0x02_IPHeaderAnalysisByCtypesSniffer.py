"""
author:Byt3h
refer: 《python黑帽子》
"""

from ctypes import * 
import socket
import struct

class IP(Structure):
    # _fields_是IP协议头数据结构，可在抓取IP数据报的时候将协议的数据头映射到该变量中
    # 想要了解更多可参考ctypes的官方文档
    _fields_ = [
        ("version",     c_utype,   4),
        ("IpHeaderLen", c_utype,   4),
        ("TypeOfSer",   c_utype,   8),
        ("length",      c_short,   16),
        ("id",          c_short,   16),
        ("offset",      c_short,   16),
        ("ttl",         c_utype,   8),
        ("protocal",    c_utype,   8),
        ("CheckSum",    c_ushort,  16),
        ("src",         c_uint32,  32),
        ("dst",         c_uint32,  32)
    ]
    
    def __new__(cls, socket_buffer = None):
        return cls.from_buffer_copy(socket_buffer)
            
    def __init__(self, socket_buffer = None):
        # 初始化为人类可读的IP地址
        self.src_address = socket.inet_ntoa(struct.pack("<L"， self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L"， self.dst))
        
        
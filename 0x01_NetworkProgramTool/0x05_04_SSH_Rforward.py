"""
author: Byt3h
refer: python黑帽子
备注: 这个程序暂时无法成功执行操作
"""

import paramiko
import parse
import select
import socket
import sys
import threading

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose("映射请求到%s:%d失败:%r" % (host, port, e))
        return
    
    verbose("已连接! 打开隧道: %r -> %r -> %r" % (chan.origin_addr, chan.getpeername(), (host, port)))
    
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data=sock.recv(1024)
            if len(data)==0:
                break
            chan.send(data)
        if chan in r:
            data=sock.recv(1024)
            if len(data)==0:
                break
            sock.send(data)
            
    chan.close()
    sock.close()
    verbose("从%r关闭隧道" % (chan.origin_addr, ))

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward('', server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()

def main:
    options, server, remote = parse.options()
    password = None
    if options.readpass:
        password = getpass.getpass("输入SSH密码：")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    verbose("正在连接ssh主机%s:%d..." % (server[0], server[1]))
    
    try:
        client.connect(
            server[0],
            server[1],
            username=options.user,
            key_filename=options.look_for_keys,
            password=password
        )
    except Exception as e:
        print("连接%s:%d时发生错误%r" % (sever[0], server[1], e))
        sys.exit(1)
    
    try:
        reverse_forward_tunnel(
            options.port, remote[0], remote[1], client.get_transport()
        )
    except KeyboardInterrupt:
        print("C-c:端口映射终止")
        sys.exit(0)

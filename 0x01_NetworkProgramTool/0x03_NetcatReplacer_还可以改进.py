'''
Designed by: Byt3h
Description: 用于模仿著名工具NetCat
Refer: 参考《Python黑帽子》一书
'''

import argparse
import shlex
import socket
import subprocess
import sys
import textwrap
import threading

class NetcatReplacer:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break

                if response:
                    print("接收到: " + response)
                    buffer = input('>')
                    buffer += '\n'
                    self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print("用户终止")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target = self.handle, args = (client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f"保存文件{self.args.upload}"
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'Byt3h: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f"服务器终止:{e}")
                    self.socket.close()
                    sys.exit()

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr = subprocess.STDOUT)
    return output.decode()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = "Netcat工具",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''
        Example:
            NetcatReplacer.py -t 192.168.1.108 -p 5555 -l -c #获取shell
            NetcatReplacer.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt #上传文件
            NetcatReplacer.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/password\" #命令执行
            echo 'ABC' | ./NetcatReplacer.py -t 192.168.1.108 -p 135 #输出文本给服务器端口135
            NetcatReplacer.py -t 192.168.1.108 -p 5555 #连接服务器
        ''')
    )
    parser.add_argument('-c', '--command', action = 'store_true', help = '获取shell')
    parser.add_argument('-e', '--execute', help = '执行特殊命令')
    parser.add_argument('-l', '--listen', action = 'store_true', help = '监听')
    parser.add_argument('-p', '--port', type = int, default = 5555, help = '固定端口')
    parser.add_argument('-t', '--target', default = '192.168.1.203', help='固定IP')
    parser.add_argument('-u', '--upload', help='上传文件')
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetcatReplacer(args, buffer.encode())
    nc.run()
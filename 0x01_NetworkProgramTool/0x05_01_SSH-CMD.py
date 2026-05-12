'''
designed by: Byt3h
refer: 参考《Python黑帽子》
'''

import paramiko
def ssh_command(ip, port, user, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=password)
    
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("-------------------输出------------------------")
        for line in output:
            print(line.strip())
            
if __name__ == '__main__':
     import getpass
     user = input("用户:")
     password = getpass.getpass()
    
     ip = input("服务器IP:") or "192.168.223.128"
     port = input("服务器IP端口:") or 22
     cmd = input("执行的命令:") or "id"
     ssh_command(ip, port, user, password, cmd)
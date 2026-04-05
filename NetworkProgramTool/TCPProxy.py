import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) ==3) and chr(i) or '.' for i in range(256)])
# 生成一个长度为256的字符串，用于将字节值映射为可打印字符或占位符'.'
# 遍历0-255的所有字节值i：
#   - chr(i) 将字节转换为对应的ASCII/Unicode字符
#   - repr(chr(i)) 返回该字符的Python字符串表示（带引号和转义）
#   - len(repr(chr(i))) == 3 判断表示长度是否为3
#     长度为3表示该字符是单个可打印字符且无需转义（如字母、数字、空格、常见标点）
#     例如：chr(65) -> 'A' -> repr -> "'A'"（长度3）
#            chr(10) -> '\n' -> repr -> "'\\n'"（长度4，条件为False）
#   - 若条件为真，则取 chr(i) 本身，否则取 '.' 作为占位符
#   - 列表推导式生成256个单字符，最后用空字符串连接成完整字符串
# 结果：HEX_FILTER[字节值] 可得到该字节对应的显示字符（可打印字符原样显示，不可打印显示为'.'）

def hexdump(src, length=16, show=True):
    """
    将字符串或字节数据以十六进制和可打印字符形式转储（类似 hexdump 命令）。
    参数:
        src: 输入数据，可以是 bytes 或 str
        length: 每行显示的字符数（字节数），默认16
        show: 是否直接打印结果，若为 False 则返回结果列表
    """

    # 如果输入是 bytes 类型，则使用 UTF-8 解码为字符串（注意：非 UTF-8 编码可能出错）
    if isinstance(src, bytes):
        src = src.decode()

    # 用于存储每行输出字符串的列表
    results = list()

    # 以步长 length 遍历字符串的起始索引
    for i in range(0, len(src), length):
        # 取出当前行的原始字符串片段
        word = str(src[i:i + length])

        # 将当前片段中的每个字符通过 HEX_FILTER 映射为可打印字符或 '.'，得到可打印表示
        # HEX_FILTER 是一个长度为256的字符串，索引为字节值，值为字符或 '.'
        # 由于 word 是字符串，translate 会将每个字符的 Unicode 码点（0~65535）作为索引，
        # 但 HEX_FILTER 只定义了 0~255，超出范围会报错。实际上 hexdump 通常处理字节，
        # 这里假设 src 解码后只包含 ASCII/拉丁-1 范围（0~255），否则会有问题。
        printable = word.translate(HEX_FILTER)

        # 生成十六进制表示：对每个字符取其 Unicode 码点（ord），格式化为两位大写的十六进制数
        hexa = ''.join([f'{ord(c):02X}' for c in word])

        # 计算十六进制部分占用的最小宽度：每个字节占3个字符（两个十六进制数加一个空格）
        hexwidth = length * 3

        # 格式化当前行：偏移量（4位十六进制）、十六进制内容（左对齐且宽度为 hexwidth）、可打印字符
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')

    # 如果 show 为 True，则打印所有行；否则返回 results 列表
    if show:
        for line in results:
            print(line)
    else:
        # 注意：这里的 else 与 if 对齐，表示 show 为 False 时返回 results
        return results

def receive_from(connection):
    #从链接中接受的数据
    buffer = b''
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    #请求处理句柄，后期可以添加一些处理逻辑，比如加密通信数据、隐藏IP地址等
    return buffer

def response_handler(buffer):
    #回应处理句柄，后期可以添加一些处理逻辑，比如加密通信数据、隐藏IP地址等
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    #代理句柄
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==]发送%s字节到localhost" % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]从localhost获取%s字节" % len(local_buffer)
            print(line)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>]发送到remote")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==]从remote获取%s字节" % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==]发送到localhost")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*]没有更多的数据，正在关闭连接。")
            break

def server_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    #代理服务器多开
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("连接出现差错: %r" % e)
        print("[!!]监听%s:%d失败" % (local_host, local_port))
        print("[!!]检查其他监听链接或者正确全权限")
        sys.exit(0)

    print("[*]正在监听%s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = ">从%s:%d接收到进入链接" % (addr[0], addr[1])
        print(line)
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, recieve_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("用法: ./TCPProxy.py [localhost][localport]", end="")
        print("[remotehost][remoteport][receive_first]")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
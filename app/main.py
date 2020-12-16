import socket  # 导入 socket 模块
from app.utils import *

file_name = "../data/distribution_add_data_1.csv"
from_index = 0
to_index = 50

if __name__ == '__main__':
    s = socket.socket()  # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    port = 12345  # 设置端口号
    s.connect((host, port))

    data_list = read_csv_int(file_name, from_index, to_index)
    sum = add(data_list)

    print("向服务端发送计算结果：{}".format(sum))

    s.send(string2bytes(str(sum)))

    print(s.recv(1024))
    s.close()

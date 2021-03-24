import socket
from app.utils import *
import time

file_name = "data/distribution_add_data_1.csv"
from_index = 0
to_index = 50

if __name__ == '__main__':
    # create socket instance
    s = socket.socket()
    # local host name
    host = socket.gethostname()
    # set server/proxy port
    port = 23456
    print(f"waiting for connecting to proxy {host}:{port}")
    s.connect((host, port))

    count = 1
    while True:
        s.send(string2bytes(str(count)))
        print(f"sending data: {count}")
        count += 3
        time.sleep(1)

    # data_list = read_csv_int(file_name, from_index, to_index)
    # sum = add(data_list)
    #
    # print("sending calculate result to server: {}".format(sum))
    #
    # s.send(string2bytes(str(sum)))
    #
    # print(s.recv(1024))
    # s.close()

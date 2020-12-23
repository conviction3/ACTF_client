import socket
from app.utils import *

file_name = "data/distribution_add_data_1.csv"
from_index = 50
to_index = -1

if __name__ == '__main__':
    # create socket instance
    s = socket.socket()
    # local host name
    host = socket.gethostname()
    # set server/proxy port
    port = 12345
    s.connect((host, port))

    data_list = read_csv_int(file_name, from_index, to_index)
    sum = add(data_list)

    print("sending calculate result to server: {}".format(sum))

    s.send(string2bytes(str(sum)))

    print(s.recv(1024))
    s.close()

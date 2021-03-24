import socket
from app.utils import *
import time
from client import Client

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

    client = Client(socket=s)


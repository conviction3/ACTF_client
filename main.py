import socket
from app.utils import *
import time
from client import Client

log = Logger()

if __name__ == '__main__':
    # create socket instance
    s = socket.socket()
    # local host name
    host = socket.gethostname()
    # set server/proxy port
    port = 23456
    log.info("""
        ___    ______ ______ ______   ______ __     ____ ______ _   __ ______
       /   |  / ____//_  __// ____/  / ____// /    /  _// ____// | / //_  __/
      / /| | / /      / /  / /_     / /    / /     / / / __/  /  |/ /  / /
     / ___ |/ /___   / /  / __/    / /___ / /___ _/ / / /___ / /|  /  / /
    /_/  |_|\____/  /_/  /_/       \____//_____//___//_____//_/ |_/  /_/

     """)
    s.connect((host, port))

    client = Client(socket=s)

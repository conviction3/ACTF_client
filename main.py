import socket
from app.utils import *
from client import Client
import sqlite3
from queue import Queue
from client import SeqData
from threading import Thread
import sys

log = Logger()


def produce(record_start: int, record_end: int, group_size: int, buffer: Queue):
    conn = sqlite3.connect('./data/test_data.db')
    c = conn.cursor()
    offset = record_start - 1
    while offset < record_end:
        cursor = c.execute(
            f'''
               SELECT id,number FROM random_numbers LIMIT {offset},{group_size} 
            '''
        )
        # fetch group_size data
        temp_list = []
        for row in cursor:
            temp_list.append(row[1])
        result = min(temp_list)
        if not buffer.full():
            buffer.put(SeqData(seq=int(offset / group_size), data=result))
        log.debug(f"[.] {offset + group_size}/{record_start}~{record_end}")
        offset += group_size
    log.debug(f"[+] {record_start}~{record_end}")


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

    # client1 = Client(socket=s)
    # t1 = Thread(target=produce, args=(1, 200, 10, client1.data_buffer))
    # client1.produce_thread = t1
    # client1.start()
    # produce(1,200,10,client1.data_buffer)

    client1 = Client(socket=s)
    t1 = Thread(target=produce, args=(int(sys.argv[1]),
                                      int(sys.argv[2]),
                                      int(sys.argv[3]),
                                      client1.data_buffer))
    client1.produce_thread = t1
    client1.start()

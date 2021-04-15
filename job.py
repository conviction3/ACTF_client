from client import Client
from threading import Thread
from package import Package, Header, PackageDataType
import subprocess
import socket

import time
from typing import List
import random


class Job:
    def __init__(self, client: Client):
        # create socket instance
        s = socket.socket()
        # local host name
        host = socket.gethostname()
        # set server/proxy port
        port = 23456

        self.__client = client

    def start_produce_thread(self):
        t = Thread(target=self.produce)
        t.start()
        t.join()

    def produce(self):
        data_set = []
        # result_buffer = []

        for i in range(1000000):
            data_set.append(random.random())
        for i in range(0, 1000000, step=10):
            result = self.__simulate_training_process(data_slice=data_set[i:i + 10])
            package = self.box_result_to_package(result)
            self.__client.add_data(package)

    def box_result_to_package(self, result: int) -> Package:
        package = Package(payload=result.to_bytes(length=4, byteorder='big', signed=False),
                          data_type=PackageDataType.INT)
        return package

    def __simulate_training_process(self, data_slice) -> int:
        time.sleep(1)
        return random.randint(0, 9999999)


def start_subprocess(*argv):
    def temp():
        subprocess.run(["./venv/Scripts/python", "main.py",
                        str(argv[0]), str(argv[1]), str(argv[2])
                        ]
                       )

    t = Thread(target=temp)
    t.start()


if __name__ == '__main__':
    start_subprocess(1, 200, 10)
    start_subprocess(201, 300, 10)

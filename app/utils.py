import csv
from typing import List
from functools import reduce

import logging.handlers


class Logger(logging.Logger):
    def __init__(self, name: str = None, filename=None):
        super().__init__(name)
        if filename is None:
            filename = './logs/client.log'
        self.filename = filename

        """
            File log handler
        """
        fh = logging.FileHandler(self.filename)
        fh.setLevel(logging.DEBUG)
        """
            Console log handler.
        """
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)5s]-[thread:%(thread)s]-[process:%(process)s] : %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(ch)


def read_csv_int(file_name: str, from_index: int, to_index: int) -> list:
    """
    read data from csv file
    :param file_name:   file name will be read
    :param from_index: start index, start from 0, include from_index
    :param to_index: end index,start from 0, exclude to_index
    :return: list of int
    """
    result_list = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        next(f)
        for item in reader:
            result_list.append(item[0])
    return [int(t) for t in result_list[from_index:to_index]]


def add(data_list: list) -> int:
    """
    sum of the list of int
    :param data_list: list of int
    :return: sum
    """
    return sum(data_list)


def string2bytes(string: str) -> bytes:
    return bytes(string, encoding="utf-8")


def int2bytes(val: int) -> bytes:
    """
        Used to transmit integer type in package payload,
    the size of int must be 8 bytes, signed.
    """
    return val.to_bytes(length=8, byteorder='big', signed=True)


def int_list_to_bytes(int_list: List[int]) -> bytes:
    bytes_list = [int2bytes(i) for i in int_list]
    return reduce(lambda x, y: x + y, bytes_list)


def bytes2int(val: bytes) -> int:
    """
        The size of int must be 8 bytes, signed.
    """
    return int.from_bytes(val, byteorder='big', signed=True)


def bytes_to_int_list(_bytes: bytes) -> List[int]:
    if len(_bytes) % 8 != 0:
        raise ValueError("length of bytes must be 8 times")

    temp_bytes_list = [_bytes[i:i + 8] for i in range(0, len(_bytes), 8)]
    int_list = []
    for item in temp_bytes_list:
        int_list.append(bytes2int(item))
    return int_list

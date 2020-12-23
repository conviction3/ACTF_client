import csv


def read_csv_int(file_name: str, from_index: int, to_index: int) -> list:
    """
    read data from csv file
    :param file_name:   file name will be read
    :param from_index: start index, start from 0, include from_index
    :param to_index: end index,start from 0, exclude to_index
    :return: list of int
    todo: use parquet
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
    todo: extend type
    """
    return sum(data_list)


def string2bytes(string: str) -> bytes:
    return bytes(string, encoding="utf-8")

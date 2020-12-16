import csv


def read_csv_int(file_name: str, from_index: int, to_index: int) -> list:
    """
    read data from csv file
    :param file_name:   要读取的文件名
    :param from_index: 开始下标，从0开始，包括from_index
    :param to_index: 结束下标，从0开始，不包括to_index
    :return: list of int
    todo: 分块读取大文件
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
    对list of int 求和
    :param data_list: list of int
    :return: sum
    todo: 拓展类型
    """
    return sum(data_list)

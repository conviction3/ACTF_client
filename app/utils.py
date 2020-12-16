import csv


def read_csv_int(file_name: str, from_index: int, to_index: int) -> list:
    """
    todo: 分块读取大文件
    read data from csv file
    :param file_name:
    :return: list of int
    """
    result_list = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        next(f)
        for item in reader:
            result_list.append(item[0])
    return [int(t) for t in result_list[from_index:to_index]]

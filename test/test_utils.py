from app.utils import *
import unittest

import os
import sys

pwd = os.getcwd()
parent_path = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
sys.path.append(parent_path)

test_file_name = "data/distribution_add_data_1.csv"


# using relative path in pycharm
# test_file_name = "../data/distribution_add_data_1.csv"


class UtilsTestSuite(unittest.TestCase):
    def test_read_csv_int(self):
        # data = read_csv_int(file_name=test_file_name, from_index=0, to_index=5)
        data = read_csv_int(file_name=test_file_name, from_index=0, to_index=4)
        self.assertEqual([1, 2, 3, 4], data)

    def test_add(self):
        data = read_csv_int(file_name=test_file_name, from_index=0, to_index=4)
        sum = add(data)
        self.assertEqual(10, sum)

    def test_string2bytes(self):
        string = "2345"
        self.assertEqual(b'2345', string2bytes(string))

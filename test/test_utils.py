from app.utils import *
import unittest

test_file_name = "../data/distribution_add_data_1.csv"


class UtilsTestSuite(unittest.TestCase):
    def test_read_csv_int(self):
        # data = read_csv_int(file_name=test_file_name, from_index=0, to_index=5)
        data = read_csv_int(file_name=test_file_name, from_index=0, to_index=4)
        self.assertEqual([1, 2, 3, 4], data)

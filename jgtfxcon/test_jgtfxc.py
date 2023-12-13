import datetime
import unittest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtfxc import parse_date

class TestParseDate(unittest.TestCase):
    def test_parse_date(self):
        # Test case 1: Valid date format '%d.%m.%Y %H:%M:%S'
        #date_format = '%m.%d.%Y %H:%M:%S'
        date_str = "12.31.2022 23:59:59"
        expected_result = datetime.datetime(2022, 12, 31, 23, 59, 59)
        print(str(expected_result))
        parsed = parse_date(date_str)
        print(str(parsed))
        self.assertEqual (parsed, expected_result)

        # Test case 2: Valid date format '%d.%m.%Y %H:%M'
        date_str = "01.01.2023 00:00"
        expected_result = datetime.datetime(2023, 1, 1, 0, 0)
        self.assertEqual ( parse_date(date_str) , expected_result)

        # Test case 3: Valid date format '%d.%m.%Y'
        date_str = "01.02.2023"
        expected_result = datetime.datetime(2023, 1, 2)
        self.assertEqual ( parse_date(date_str) , expected_result)

        # Test case 4: Valid date format '%Y%m%d%H%M'
        date_str = "202301020000"
        expected_result = datetime.datetime(2023, 1, 2, 0, 0)
        self.assertEqual ( parse_date(date_str) , expected_result)

        # Test case 5: Valid date format '%y%m%d%H%M'
        date_str = "2301020000"
        expected_result = datetime.datetime(2023, 1, 2, 0, 0)
        self.assertEqual ( parse_date(date_str) , expected_result)

        # Test case 6: Valid date format '%Y-%m-%d %H:%M'
        date_str = "2023-01-02 00:00"
        expected_result = datetime.datetime(2023, 1, 2, 0, 0)
        self.assertEqual ( parse_date(date_str), expected_result)

        # Test case 7: Invalid date format
        date_str = "2023/01/02"
        
        try:
            parse_date(date_str)
            self.assertFalse(False, 'no valid date format found')
        except ValueError:
            pass

        print("All test cases passed!")




if __name__ == "__main__":
    unittest.main()
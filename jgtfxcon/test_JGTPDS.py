import unittest
from datetime import datetime
from pandas.testing import assert_frame_equal
import pandas as pd
from JGTPDS import getPH,connect as on,stayConnectedSetter as sc,disconnect as off

class TestGetPH(unittest.TestCase):
    def test_getPH(self):
        # Test case 1: Retrieve price history from broker
        instrument = "EUR/USD"
        timeframe = "H1"
        quote_count = 335
        start = None
        end = None
        with_index = True
        quiet = True

        expected_result = pd.DataFrame({
            'Date': [datetime(2022, 12, 31), datetime(2023, 1, 1), datetime(2023, 1, 2)],
            'BidOpen': [1.2345, 1.2356, 1.2367],
            'BidHigh': [1.2356, 1.2367, 1.2378],
            'BidLow': [1.2334, 1.2345, 1.2356],
            'BidClose': [1.2356, 1.2367, 1.2378],
            'AskOpen': [1.2346, 1.2357, 1.2368],
            'AskHigh': [1.2357, 1.2368, 1.2379],
            'AskLow': [1.2335, 1.2346, 1.2357],
            'AskClose': [1.2357, 1.2368, 1.2379],
            'Volume': [1000, 2000, 3000]
        })
        sc(True)
        result = getPH(instrument, timeframe, quote_count, start, end, with_index, quiet)
        result.to_csv("jgtfxcon/test_JGTPDS.out.csv")
        off()
        result.tail()
        assert_frame_equal(result, expected_result)

    # def test_getPH_from_filestore(self):
    #     # Test case 2: Read price history from local filestore
    #     instrument = "EURUSD"
    #     timeframe = "H1"
    #     quote_count = 335
    #     start = None
    #     end = None
    #     with_index = True
    #     quiet = True

    #     expected_result = pd.DataFrame({
    #         'Date': [datetime(2022, 12, 31), datetime(2023, 1, 1), datetime(2023, 1, 2)],
    #         'BidOpen': [1.2345, 1.2356, 1.2367],
    #         'BidHigh': [1.2356, 1.2367, 1.2378],
    #         'BidLow': [1.2334, 1.2345, 1.2356],
    #         'BidClose': [1.2356, 1.2367, 1.2378],
    #         'AskOpen': [1.2346, 1.2357, 1.2368],
    #         'AskHigh': [1.2357, 1.2368, 1.2379],
    #         'AskLow': [1.2335, 1.2346, 1.2357],
    #         'AskClose': [1.2357, 1.2368, 1.2379],
    #         'Volume': [1000, 2000, 3000]
    #     })

    #     result = getPH(instrument, timeframe, quote_count, start, end, with_index, quiet)

    #     assert_frame_equal(result, expected_result)

if __name__ == "__main__":
    unittest.main()
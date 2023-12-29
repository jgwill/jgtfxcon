#%% Imports

# Copyright 2019 Gehtsoft USA LLC

# Licensed under the license derived from the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

# http://fxcodebase.com/licenses/open-source/license.html

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from forexconnect import ForexConnect, fxcorepy
#from jgtpy import JGTConfig as conf

from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()  # take environment variables from .env.
#env=load_dotenv(os.getenv(os.getcwd()))
env = dotenv_values(".env")

if os.getenv('user_id') == "":
  load_dotenv(os.getenv('HOME'))
if os.getenv('user_id') == "":
  load_dotenv(os.getenv(os.getcwd()))

user_id = os.getenv('user_id')
password = os.getenv('password')
url = os.getenv('url')
connection = os.getenv('connection')
quotes_count = os.getenv('quotes_count')

#from jgtpy import jgtcommon as jgtcomm,iprops
from jgtutils import jgtcommon as jgtcomm,iprops

##import jgtcommon as jgtcomm,iprops

import common_samples
"""

url='https://www.fxcorporate.com/Hosts.jsp'
connection='Demo'
quotes_count='800'
"""

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    #jgtcomm.add_main_arguments(parser)
    jgtcomm.add_instrument_timeframe_arguments(parser)
    #common_samples.add_date_arguments(parser)
    jgtcomm.add_tlid_range_argument(parser)
    #jgtcomm.add_date_arguments(parser)
    jgtcomm.add_max_bars_arguments(parser)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    str_user_id = user_id#args.l
    str_password = password#args.p
    str_url = url#args.u
    using_tlid = False
    if args.tlidrange is not None:
      using_tlid= True
      tlid_range = args.tlidrange
      #print(tlid_range)
      dtf,dtt = jgtcomm.tlid_range_to_start_end_datetime(tlid_range)
      #print(str(dtf) + " " + str(dtt))
      date_from =dtf
      date_to = dtt
      print(str(date_from),str(date_to))
    else:
      quotes_count = args.quotescount
      
    str_connection = connection#args.c
    #str_session_id = args.session
    #str_pin = args.pin
    
    str_instrument = args.instrument
    str_timeframe = args.timeframe
    

    ip = iprops.get_iprop(instrument=str_instrument)
    pips= ip["pips"]
    lpip=len(str(pips))
    
    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url,
                     str_connection,
                     common_samples.session_status_changed)

            #print("")
            #print("Requesting a price history...")
            if using_tlid:
              history = fx.get_history(str_instrument, str_timeframe, date_from, date_to)
            else:
              history = fx.get_history(str_instrument, str_timeframe,None,None, quotes_count)
            current_unit, _ = ForexConnect.parse_timeframe(str_timeframe)
           
            #date_format = '%m.%d.%Y %H:%M:%S'
            date_format = '%Y-%m-%d %H:%M:%S'
            if current_unit == fxcorepy.O2GTimeFrameUnit.TICK:
                print("Date, Bid, Ask")
                #print(history.dtype.names)
                for row in history:
                    print("{0:s}, {1:,.5f}, {2:,.5f}".format(
                        pd.to_datetime(str(row['Date'])).strftime(date_format), row['Bid'], row['Ask']))
            else:
                print("Date, Open, High, Low, Close, Median, Volume")
                rounder = lpip+1
                for row in history:
                    print(format_output(rounder,row,rounder,date_format))
                    
                    # print("{0:s},{1:.5f},{2:.5f},{3:.5f},{4:.5f},{5:.5f},{6:d}".format(                    
                    #     pd.to_datetime(str(row['Date'])).strftime(date_format), open_price, high_price,
                    #     low_price, close_price, median, row['Volume']))
        except Exception as e:
            jgtcomm.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            jgtcomm.print_exception(e)

def format_output(nb_decimal, row, rounder, date_format = '%Y-%m-%d %H:%M:%S'):
    open_price = round(((row['BidOpen'] + row['AskOpen']) / 2), rounder)
    high_price = round(((row['BidHigh'] + row['AskHigh']) / 2), rounder)
    low_price = round(((row['BidLow'] + row['AskLow']) / 2), rounder)
    close_price = round(((row['BidClose'] + row['AskClose']) / 2), rounder)
    median = round(((high_price + low_price) / 2), rounder)
    dt_formatted=pd.to_datetime(str(row['Date'])).strftime(date_format)
    #print("dt formatted: " + dt_formatted)
    formatted_string = f"{dt_formatted},{open_price:.{nb_decimal}f},{high_price:.{nb_decimal}f},{low_price:.{nb_decimal}f},{close_price:.{nb_decimal}f},{median:.{nb_decimal}f},{row['Volume']:d}"
    return formatted_string
  
def format_output1(nb_decimal, row, rounder,date_format = '%Y-%m-%d %H:%M:%S'):
    open_price = round(((row['BidOpen'] + row['AskOpen']) / 2),rounder)
    high_price = round(((row['BidHigh'] + row['AskHigh']) / 2),rounder)
    low_price = round(((row['BidLow'] + row['AskLow']) / 2),rounder)
    close_price = round(((row['BidClose'] + row['AskClose']) / 2),rounder)
    median = round(((high_price + low_price) / 2),rounder)
    format_specifier = f"{{:.{nb_decimal}f}}"
    formatted_string = f"{pd.to_datetime(str(row['Date'])).strftime(date_format)},{open_price:{format_specifier}},{high_price:{format_specifier}},{low_price:{format_specifier}},{close_price:{format_specifier}},{median:{format_specifier}},{row['Volume']:d}"
    return formatted_string

# Usage

if __name__ == "__main__":
    main()
    print("")
    #input("Done! Press enter key to exit\n")
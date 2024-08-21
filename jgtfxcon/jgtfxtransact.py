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

from jgtutils.jgtclihelper import print_jsonl_message

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

from jgtutils import jgtos, jgtcommon, jgtpov

SAVE_FXTR_FILE_AUTOMATICALLY=True

from forexconnect import ForexConnect, EachRowListener

from jgtutils.FXTransact import FXTransactWrapper
from jgtutils.FXTransact import FXTransactDataHelper as fxtdh

import common_samples 

import json

def parse_args():
    parser = jgtcommon.new_parser("JGT FX Transact CLI", "List and hopefully manage trade and order on FXConnect", "fxtransact")
    
    parser=jgtcommon.add_demo_flag_argument(parser)
    parser=jgtcommon.add_verbose_argument(parser)
    parser=jgtcommon.add_instrument_standalone_argument(parser,required=False)
    parser=jgtcommon.add_orderid_arguments(parser,required=False)
    parser=jgtcommon.add_tradeid_arguments(parser,required=False)
    parser=jgtcommon.add_account_arguments(parser,required=False)
    
    parser.add_argument('-table',
                        metavar="TABLE",
                        default="all",
                        help='The print table. Possible values are: orders - orders table,\
                        trades - trades table. Default value is trades. Optional parameter.')
    # parser.add_argument('-account', metavar="AccountID", required=False,
    #                     help='Account ID')
    
    # parser.add_argument('-id','--orderid', metavar="OrderID", required=False,
    #                     help='The identifier (optional for filtering).')
    #optional instrument
    # parser.add_argument('-i','--instrument', metavar="Instrument", required=False,
    #                     help='The instrument (optional for filtering).')
    #-save
    parser.add_argument('-save','--save', required=False,
                        help='Save the output to a file.', action='store_true')
    
    
    args=jgtcommon.parse_args(parser)

    return args

str_order_id = None
str_trade_id = None
str_instrument = None

def get_account(table_manager, quiet=True):
    accounts_table = table_manager.get_table(ForexConnect.ACCOUNTS)
    for account_row in accounts_table:
        msg = "{" + " \"AccountID\": {0:s}, \"Balance\": {1:.5f} ".format(account_row.account_id, account_row.balance) + "}"
        if not quiet:print(msg)
    return accounts_table.get_row(0)

from jgtutils.FXTransact import FXOrder

def parse_order_row(order_row, account_id,quiet=True):
    global str_order_id, str_instrument
    if order_row.table_type == ForexConnect.ORDERS:
        if not account_id or account_id == order_row.account_id:
            string = _order_row_to_string(order_row)
            #if not quiet:print(string)
            order=FXOrder.from_string(string)
            
            if not str_order_id and not str_instrument:
                json_str = order.tojson()
                if not quiet:print(json_str)
                return order
            
            current_instrument=order.instrument
            
            #try:current_instrument = order.instrument if order.instrument else None 
            #except:pass
            #@STCIssue Contingent OrderID are related to a TradeID, how to manage that ?
            
            if str_instrument and str_instrument == current_instrument:
                json_str = order.tojson()
                if not quiet:print(json_str)
                return order
            
            if str_instrument:
                return None
            
            if not str_order_id : #NO FILTERING
                json_str = order.tojson()
                if not quiet:print(json_str)
                return order
            else:
                if str_order_id == str(order.order_id):
                    json_str = order.tojson()
                    if not quiet:print(json_str)
                    return order
        return None
    return None

def _order_row_to_string(order_row):
    string = ""
    for column in order_row.columns:
        string += column.id + "=" + str(order_row[column.id]) + "; "
    return string

from jgtutils.FXTransact import FXOrders
def parse_orders(table_manager, account_id,quiet=True):
    orders_table = table_manager.get_table(ForexConnect.ORDERS)
    if len(orders_table) == 0:
        if not quiet:print_jsonl_message("Table is empty!")
        return None
    else:
        fxorders:FXOrders=FXOrders()
        for order_row in orders_table:
            order_data=parse_order_row(order_row, account_id)
            if order_data:
                fxorders.add_order(order_data)
        return fxorders


from jgtutils.FXTransact import FXTrade
def parse_trade_row(trade_row, account_id,quiet=True):
    global str_order_id, str_instrument,str_trade_id
    if trade_row.table_type == ForexConnect.TRADES:
        if not account_id or account_id == trade_row.account_id:
            trade_data = {}
            string =_trade_row_to_string(trade_row, trade_data)
            trade = FXTrade.from_string(string)
            
            if str_instrument and str_instrument == trade.instrument:
                json_str = trade.tojson()
                if not quiet:print(json_str)
                return trade
            
            if str_instrument:
                return None
                
            if not str_order_id and not str_trade_id: #NO FILTERING
                json_str = trade.tojson()
                if not quiet:print(json_str)
                return trade
            else:
                cur_id:str = str(trade.trade_id)
                #by tradeid
                if str_trade_id and str_trade_id == str(cur_id):
                    json_str = trade.tojson()
                    if not quiet:print(json_str)
                    return trade
                #by orderid #@STCIssue Might Want to support filtering by orderid of the original order id that generated the trade
                if str_order_id and str_order_id == str(cur_id):
                    json_str = trade.tojson()
                    if not quiet:print(json_str)
                    return trade

def _trade_row_to_string(trade_row, trade_data):
    string=""
    for column in trade_row.columns:
        string += column.id + "=" + str(trade_row[column.id]) + "; "
        trade_data[column.id] = trade_row[column.id]
    return string

from jgtutils.FXTransact import FXTrades

def parse_trades(table_manager, account_id,quiet=True)->FXTrades:
    trades_table = table_manager.get_table(ForexConnect.TRADES)
    if len(trades_table) == 0:
        if not quiet:print_jsonl_message("Table is empty!")
        return None
    else:
        trades=FXTrades()
        for trade_row in trades_table:
            trade_data=parse_trade_row(trade_row, account_id)
            if trade_data:
                trades.add_trade(trade_data)
        return trades


def main():
    global str_order_id, str_instrument,str_trade_id
    args = parse_args()
    quiet=args.quiet
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    str_session_id = ""
    str_pin = ""
    str_order_id=args.orderid if args.orderid else None
    str_trade_id=args.tradeid if args.tradeid else None
    if str_trade_id and not str_order_id:
        str_order_id=str_trade_id #@STCIssue Fix not working for trades
    str_instrument=args.instrument if args.instrument else None
    save_flag=True if args.save else False
    
    str_table = args.table

    if str_table != 'orders' and  str_table != 'trades' :
        str_table = 'all'

    with ForexConnect() as fx:

        fx.login(str_user_id, str_password, str_url,
                 str_connection, str_session_id, str_pin,
                 common_samples.session_status_changed)

        table_manager = fx.table_manager
        account = get_account(table_manager)

        if not account:
            raise Exception("No valid accounts")

        fxtransactwrapper = FXTransactWrapper()
        
        fxorders:FXOrders =None
        if str_table == "orders" or str_table == "all":
            fxorders:FXOrders = parse_orders(table_manager, account.account_id)
            if fxorders:
                if not quiet:print(fxorders.tojson())
                fxtransactwrapper.add_orders(fxorders)
        
        fxtrades:FXTrades =None
        if str_table == "trades" or str_table == "all":
            fxtrades:FXTrades =parse_trades(table_manager, account.account_id)
            if fxtrades:
                if not quiet:print(fxtrades.tojson())
                fxtransactwrapper.add_trades(fxtrades)

        if save_flag or SAVE_FXTR_FILE_AUTOMATICALLY:
            saved_filepath=fxtdh.save_fxtransact_to_file(fxtransactwrapper,str_table,str_connection,save_prefix="fxtransact_",prefix_to_connection=False,str_order_id=str_order_id,str_instrument=str_instrument,str_trade_id=str_trade_id)
            print_jsonl_message("Trade Data Saved.",extra_dict={"file":saved_filepath},scope="fxtr")

        else:# we print the data
            print(fxtransactwrapper.tojson())
            
            
        
        
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()

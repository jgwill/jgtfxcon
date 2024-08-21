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
import threading
from time import sleep

import os
import sys

import pandas as pd

from jgtutils.jgtclihelper import print_jsonl_message
from FXTransact import FXTrade,FXTransactDataHelper as ftdh
import FXHelperTransact as fht

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

from jgtutils import jgtcommon
from jgtutils.jgtfxhelper import offer_id_to_instrument,offers_to_dict

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples


str_trade_id = None
lots_to_close=-1
quiet=True
verbose=0

def parse_args():
    parser = jgtcommon.new_parser("JGT FX CloseByInstrument CLI", "Close trade on FXConnect", "fxclosetradebyinstrument")

    #common_samples.add_main_arguments(parser)
    #parser=jgtcommon.add_instrument_timeframe_arguments(parser, timeframe=False)
    parser=jgtcommon.add_instrument_standalone_argument(parser)
    parser=jgtcommon.add_demo_flag_argument(parser)
    parser=jgtcommon.add_tradeid_arguments(parser)
    parser=jgtcommon.add_orderid_arguments(parser, required=False)
    parser=jgtcommon.add_lots_arguments(parser,default_value=-1)
    
    parser=jgtcommon.add_account_arguments(parser)
    parser=jgtcommon.add_verbose_argument(parser)
    
    args = jgtcommon.parse_args(parser)

    return args


class ClosedTradesMonitor:
    def __init__(self):
        self.__close_order_id = None
        self.__closed_trades = {}
        self.__event = threading.Event()

    def on_added_closed_trade(self, _, __, closed_trade_row):
        close_order_id = closed_trade_row.close_order_id
        self.__closed_trades[close_order_id] = closed_trade_row
        if self.__close_order_id == close_order_id:
            self.__event.set()

    def wait(self, time, close_order_id):
        self.__close_order_id = close_order_id

        closed_trade_row = self.find_closed_trade(close_order_id)
        if closed_trade_row is not None:
            return closed_trade_row

        self.__event.wait(time)

        return self.find_closed_trade(close_order_id)

    def find_closed_trade(self, close_order_id):
        if close_order_id in self.__closed_trades:
            return self.__closed_trades[close_order_id]
        return None

    def reset(self):
        self.__close_order_id = None
        self.__closed_trades.clear()
        self.__event.clear()


class OrdersMonitor:
    def __init__(self):
        self.__order_id = None
        self.__added_orders = {}
        self.__deleted_orders = {}
        self.__added_order_event = threading.Event()
        self.__deleted_order_event = threading.Event()

    def on_added_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__added_orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__added_order_event.set()

    def on_deleted_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__deleted_orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__deleted_order_event.set()

    def wait(self, time, order_id):
        self.__order_id = order_id

        is_order_added = True
        is_order_deleted = True

        # looking for an added order
        if order_id not in self.__added_orders:
            is_order_added = self.__added_order_event.wait(time)

        if is_order_added:
            order_row = self.__added_orders[order_id]
            print("The order has been added. Order ID: {0:s}, Rate: {1:.5f}, Time In Force: {2:s}".format(
                order_row.order_id, order_row.rate, order_row.time_in_force))

        # looking for a deleted order
        if order_id not in self.__deleted_orders:
            is_order_deleted = self.__deleted_order_event.wait(time)

        if is_order_deleted:
            order_row = self.__deleted_orders[order_id]
            print("The order has been deleted. Order ID: {0}".format(order_row.order_id))

        return is_order_added and is_order_deleted

    def reset(self):
        self.__order_id = None
        self.__added_orders.clear()
        self.__deleted_orders.clear()
        self.__added_order_event.clear()
        self.__deleted_order_event.clear()


def main():
    global str_trade_id, quiet,verbose,lots_to_close
    
    args = parse_args()

    verbose=args.verbose
    
    str_trade_id = args.tradeid if args.tradeid else None
    if str_trade_id is None and args.orderid:
        str_trade_id = args.orderid #support using -id
    quiet=args.quiet
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    str_session_id = ""
    str_pin = ""
    
    str_instrument = args.instrument if args.instrument else None
    str_account = args.account
    lots_to_close=args.lots

    with ForexConnect() as fx:
        fx.login(str_user_id, str_password, str_url, str_connection, str_session_id,
                 str_pin, common_samples.session_status_changed)
        str_account_fix = str_account if str_connection != "Demo" else None
        account = Common.get_account(fx, str_account_fix)

        if not account:
            raise Exception(
                "The account '{0}' is not valid".format(account))
        else:
            str_account = account.account_id
            msg = f"Account information."
            print_jsonl_message(msg, extra_dict={"account_id": str_account})#extra_dict={"account_id": str_account, "balance": account.balance, "equity": account.equity, "used_margin": account.used_margin, "usable_margin": account.usable_margin})

        
        if str_instrument:
            offer = Common.get_offer(fx, str_instrument)
        else:
            offer = None

        if not offer and not str_trade_id:
            #from jgtutils.jgterrorcodes import 
            raise Exception(
                 "Requires instrument(-i) or TradeId(-tid) to be specified")
            
        if not offer:
            if verbose>0:
                print_jsonl_message("We will lookup for this trade in all instruments")
        

        if not str_trade_id:
            trade = Common.get_trade(fx, str_account, offer.offer_id)
        else:
            if offer:
                trade=Common.get_trade_by_id(fx, str_account, str_trade_id, offer.offer_id)
            else:
                trade=Common.get_trade_by_id(fx, str_account, str_trade_id)

        if not trade:
            msg = "There are no opened positions for instrument '{0}' '{1}' ".format(str_instrument, str_trade_id)
            print_jsonl_message(msg, extra_dict={"instrument": str_instrument, "trade_id": str_trade_id})
            exit(0)

        trade_offer_id = trade.offer_id
        if not offer:
            #print(trade_offer_id)
            __instrument=offer_id_to_instrument(trade_offer_id)
            offer = Common.get_offer(fx, __instrument)
        
        offer_df:pd.DataFrame=Common.convert_row_to_dataframe(offer)
        offer_df.to_json("offer.json")
        trade_df:pd.DataFrame=Common.convert_row_to_dataframe(trade)
        trade_df.to_json("trade.json")

        contract_multiplier=offer.contract_multiplier if offer.contract_multiplier else 1
        
        lotsize=1
        instruments_table = fx.get_table(ForexConnect.OFFERS)
        for row in instruments_table:
            offer_df2:pd.DataFrame=pd.DataFrame()
            current_instrument = row.instrument
            fn = f"{current_instrument}.json"
            savepath=os.path.join("offers",fn.replace("/","-"))
            offer_df2=Common.convert_row_to_dataframe_v2(row)
            def __remove_number_prefix(column_name):
                return ''.join([i for i in column_name if not i.isdigit()])
            offer_df2.columns = [__remove_number_prefix(col) for col in offer_df2.columns]
            columns_to_clean = [
                "ask", "ask_change_direction", "ask_expire_date", "ask_id", "ask_tradable",
                "bid", "bid_change_direction", "bid_expire_date", "bid_id", "bid_tradable",
                "buy_interest", "default_sort_order", "dividend_buy", "dividend_sell",
                "hi_change_direction", "high", "instrument", "instrument_type", "low",
                "low_change_direction", "pip_cost", "point_size", "quote_id", "subscription_status","trading_status","sell_interest","time","value_date","volume"
            ]
            for col in columns_to_clean:
                if col in offer_df2.columns:
                    offer_df2.drop(col, axis=1, inplace=True)
            offer_df2.to_json(savepath)
            offer_df2.to_csv(savepath.replace(".json",".csv"),index=False)
            offer_df2.to_markdown(savepath.replace(".json",".md"))
            if current_instrument == str_instrument:
                lotsize=row.default_lot_size
                break
        print(f"Lot size for {str_instrument} is {lotsize}")
        amount = trade.amount
        """
        -In case of FX instruments, the returned value is expressed in the instrument base currency.
        -In case of CFD instruments, the returned value is expressed in contracts.
        
        """
        fxtrade=fht.trade_row_to_trade_object(trade)
        if lots_to_close>0:
            #offer = Common.get_offer(fx, trade.instrument)
            amount=lots_to_close
            print_jsonl_message(f"Closing {lots_to_close} lots", extra_dict={"lots": lots_to_close,"total_amount_of_trade":trade.amount})
        
            

        buy = fxcorepy.Constants.BUY
        sell = fxcorepy.Constants.SELL

        buy_sell = sell if trade.buy_sell == buy else buy

        request = fx.create_order_request(
            order_type=fxcorepy.Constants.Orders.TRUE_MARKET_CLOSE,
            OFFER_ID=trade_offer_id,
            ACCOUNT_ID=str_account,
            BUY_SELL=buy_sell,
            AMOUNT=amount,
            TRADE_ID=trade.trade_id
        )

        if request is None:
            raise Exception("Cannot create request")

        orders_monitor = OrdersMonitor()
        closed_trades_monitor = ClosedTradesMonitor()

        closed_trades_table = fx.get_table(ForexConnect.CLOSED_TRADES)
        orders_table = fx.get_table(ForexConnect.ORDERS)

        trades_listener = Common.subscribe_table_updates(closed_trades_table,
                                                         on_add_callback=closed_trades_monitor.on_added_closed_trade)
        orders_listener = Common.subscribe_table_updates(orders_table, on_add_callback=orders_monitor.on_added_order,
                                                         on_delete_callback=orders_monitor.on_deleted_order)

        try:
            resp = fx.send_request(request)
            order_id = resp.order_id

        except Exception as e:
            common_samples.print_exception(e)
            trades_listener.unsubscribe()
            orders_listener.unsubscribe()

        else:
            # Waiting for an order to appear/delete or timeout (default 30)
            is_success = orders_monitor.wait(30, order_id)

            closed_trade_row = None
            if is_success:
                # Waiting for a closed trade to appear or timeout (default 30)
                closed_trade_row = closed_trades_monitor.wait(30, order_id)

            if closed_trade_row is None:
                response_timeout_expired = "Response waiting timeout expired.\n"
                print_jsonl_message(response_timeout_expired, extra_dict={"status": "timeout"})
            else:
                #print("For the order: OrderID = {0} the following positions have been closed: ".format(order_id))
                msg =f"Closed positions for the OrderID = {order_id}"
                # msg = "Closed Trade ID: {0:s}; Amount: {1:d}; Closed Rate: {2:.5f}".format(closed_trade_row.trade_id,
                #                                                                            closed_trade_row.amount,
                #                                                                            closed_trade_row.close_rate)
                                                                         
                print_jsonl_message(msg, extra_dict={"trade_id": closed_trade_row.trade_id, "amount": closed_trade_row.amount, "close_rate": closed_trade_row.close_rate, "original_order_id": order_id})
                sleep(1)
            trades_listener.unsubscribe()
            orders_listener.unsubscribe()

        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()

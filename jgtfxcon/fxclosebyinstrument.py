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

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

from jgtutils import jgtcommon
from jgtutils.jgtfxhelper import offer_id_to_instrument

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples


str_trade_id = None

def parse_args():
    parser = jgtcommon.new_parser("JGT FX CloseByInstrument CLI", "Close trade on FXConnect", "fxclosetradebyinstrument")

    #common_samples.add_main_arguments(parser)
    #parser=jgtcommon.add_instrument_timeframe_arguments(parser, timeframe=False)
    parser=jgtcommon.add_instrument_standalone_argument(parser)
    parser=jgtcommon.add_demo_flag_argument(parser)
    parser=jgtcommon.add_tradeid_arguments(parser)
    parser=jgtcommon.add_orderid_arguments(parser, required=False)
    
    parser=jgtcommon.add_account_arguments(parser)
    
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
    global str_trade_id
    args = parse_args()
    str_trade_id = args.tradeid if args.tradeid else None
    if str_trade_id is None and args.orderid:
        str_trade_id = args.orderid #support using -id
    quiet=args.quiet
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    str_session_id = ""
    str_pin = ""
    
    str_instrument = args.instrument if args.instrument else None
    str_account = args.account

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
            print("AccountID='{0}'".format(str_account))

        
        if str_instrument:
            offer = Common.get_offer(fx, str_instrument)
        else:
            offer = None

        if not offer and not str_trade_id:
            raise Exception(
                 "Requires instrument(-i) or TradeId(-tid) to be specified")
            
        if not offer:
            print("We will lookup for this trade in all instruments")
        

        if not str_trade_id:
            trade = Common.get_trade(fx, str_account, offer.offer_id)
        else:
            if offer:
                trade=Common.get_trade_by_id(fx, str_account, str_trade_id, offer.offer_id)
            else:
                trade=Common.get_trade_by_id(fx, str_account, str_trade_id)

        if not trade:
            print("There are no opened positions for instrument '{0}' '{1}' ".format(str_instrument, str_trade_id))
            exit(0)

        amount = trade.amount
        
        trade_offer_id = trade.offer_id
        #if not offer:
            #print(trade_offer_id)
            #str_instrument=offer_id_to_instrument(trade_offer_id)
            #offer = Common.get_offer(fx, str_instrument)
            

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
                print("Response waiting timeout expired.\n")
            else:
                print("For the order: OrderID = {0} the following positions have been closed: ".format(order_id))
                print("Closed Trade ID: {0:s}; Amount: {1:d}; Closed Rate: {2:.5f}".format(closed_trade_row.trade_id,
                                                                                           closed_trade_row.amount,
                                                                                           closed_trade_row.close_rate))
                sleep(1)
            trades_listener.unsubscribe()
            orders_listener.unsubscribe()

        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()

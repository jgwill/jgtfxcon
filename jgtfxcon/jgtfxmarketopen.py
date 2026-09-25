# jgtfxmarketopen.py — Open a position at market price via ForexConnect
#
# CLI: fxopen -i EUR/JPY -d B -n 1 --demo
# Uses TRUE_MARKET_OPEN order type (immediate execution at current market price)

import argparse
import json
from time import sleep
from threading import Event

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
from jgtutils import jgtos, jgtcommon, jgtpov

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples


def parse_args():
    parser = jgtcommon.new_parser(
        "JGT FX Market Open CLI",
        "Open a position at market price on FXConnect",
        "fxopen",
    )
    parser = jgtcommon.add_demo_flag_argument(parser)
    parser = jgtcommon.add_direction_rate_lots_arguments(
        parser, direction=True, rate=False, lots=True, stop=False
    )
    parser = jgtcommon.add_instrument_timeframe_arguments(parser, timeframe=False)
    args = jgtcommon.parse_args(parser)
    return args


class OrdersMonitor:
    def __init__(self):
        self.__order_id = None
        self.__orders = {}
        self.__event = Event()

    def on_added_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__event.set()

    def on_deleted_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__event.set()

    def wait(self, time, order_id):
        self.__order_id = order_id
        order_row = self.find_order(order_id)
        if order_row is not None:
            return order_row
        self.__event.wait(time)
        return self.find_order(order_id)

    def find_order(self, order_id):
        return self.__orders.get(order_id, None)

    def reset(self):
        self.__order_id = None
        self.__orders.clear()
        self.__event.clear()


class TradesMonitor:
    def __init__(self):
        self.__trade_id = None
        self.__trades = {}
        self.__event = Event()

    def on_added_trade(self, _, __, trade_row):
        trade_id = trade_row.trade_id
        self.__trades[trade_id] = trade_row
        self.__event.set()

    def wait(self, time):
        self.__event.wait(time)
        if self.__trades:
            return list(self.__trades.values())[0]
        return None

    def reset(self):
        self.__trades.clear()
        self.__event.clear()


def main():
    args = parse_args()
    str_user_id, str_password, str_url, str_connection, str_account = (
        jgtcommon.read_fx_str_from_config(demo=args.demo)
    )
    str_session_id = ""
    str_pin = ""
    str_instrument = args.instrument
    str_buy_sell = args.bs
    str_lots = args.lots

    with ForexConnect() as fx:
        fx.login(
            str_user_id,
            str_password,
            str_url,
            str_connection,
            str_session_id,
            str_pin,
            common_samples.session_status_changed,
        )

        try:
            str_account_fix = str_account if not args.demo else None
            account = Common.get_account(fx, str_account_fix)
            if not account:
                raise Exception("The account '{0}' is not valid".format(str_account))
            str_account = account.account_id

            offer = Common.get_offer(fx, str_instrument)
            if offer is None:
                raise Exception(
                    "The instrument '{0}' is not valid".format(str_instrument)
                )

            login_rules = fx.login_rules
            trading_settings_provider = login_rules.trading_settings_provider
            base_unit_size = trading_settings_provider.get_base_unit_size(
                str_instrument, account
            )
            amount = base_unit_size * str_lots

            request = fx.create_order_request(
                order_type=fxcorepy.Constants.Orders.TRUE_MARKET_OPEN,
                OFFER_ID=offer.offer_id,
                ACCOUNT_ID=str_account,
                BUY_SELL=str_buy_sell,
                AMOUNT=amount,
            )

            orders_monitor = OrdersMonitor()
            trades_monitor = TradesMonitor()

            orders_table = fx.get_table(ForexConnect.ORDERS)
            trades_table = fx.get_table(ForexConnect.TRADES)

            orders_listener = Common.subscribe_table_updates(
                orders_table,
                on_add_callback=orders_monitor.on_added_order,
                on_delete_callback=orders_monitor.on_deleted_order,
            )
            trades_listener = Common.subscribe_table_updates(
                trades_table, on_add_callback=trades_monitor.on_added_trade
            )

            try:
                resp = fx.send_request(request)
                order_id = resp.order_id

            except Exception as e:
                _type = type(e).__name__
                error_msg = str(e)
                print(json.dumps({"error": error_msg, "type": _type}))
                orders_listener.unsubscribe()
                trades_listener.unsubscribe()
                exit(1)

            else:
                # Wait for the trade to appear (market orders fill immediately)
                trade_row = trades_monitor.wait(30)
                if trade_row is None:
                    print(
                        json.dumps(
                            {
                                "order_id": order_id,
                                "status": "submitted",
                                "warning": "Trade confirmation timeout — check trades table",
                            }
                        )
                    )
                else:
                    result = {
                        "order_id": order_id,
                        "trade_id": trade_row.trade_id,
                        "instrument": str_instrument,
                        "buy_sell": trade_row.buy_sell,
                        "amount": trade_row.amount,
                        "open_rate": trade_row.open_rate,
                        "status": "executed",
                    }
                    print(json.dumps(result))
                    sleep(1)

                orders_listener.unsubscribe()
                trades_listener.unsubscribe()

        except Exception as e:
            common_samples.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()

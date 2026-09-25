# jgtfxclose.py — Close an open position at market price via ForexConnect
#
# CLI: fxclose -i EUR/JPY --demo           (close by instrument)
#      fxclose --trade-id 12345 --demo      (close by trade ID)
# Uses TRUE_MARKET_CLOSE order type (immediate close at current market price)

import argparse
import json
import threading
from time import sleep

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
from jgtutils import jgtos, jgtcommon, jgtpov

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples


def parse_args():
    parser = jgtcommon.new_parser(
        "JGT FX Close Position CLI",
        "Close an open position at market price on FXConnect",
        "fxclose",
    )
    parser = jgtcommon.add_demo_flag_argument(parser)
    parser.add_argument(
        "-i",
        "--instrument",
        metavar="INSTRUMENT",
        required=False,
        help="Instrument to close (e.g. EUR/JPY). Closes first matching trade.",
    )
    parser.add_argument(
        "--trade-id",
        metavar="TRADE_ID",
        required=False,
        help="Trade ID to close (from fxtr -table trades).",
    )
    parser.add_argument(
        "-n",
        "--lots",
        metavar="LOTS",
        type=int,
        required=False,
        default=0,
        help="Lots to close (0 = close full position). Default: 0",
    )
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
        return self.__closed_trades.get(close_order_id, None)

    def reset(self):
        self.__close_order_id = None
        self.__closed_trades.clear()
        self.__event.clear()


class OrdersMonitor:
    def __init__(self):
        self.__order_id = None
        self.__added_orders = {}
        self.__deleted_orders = {}
        self.__added_event = threading.Event()
        self.__deleted_event = threading.Event()

    def on_added_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__added_orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__added_event.set()

    def on_deleted_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__deleted_orders[order_id] = order_row
        if self.__order_id == order_id:
            self.__deleted_event.set()

    def wait(self, time, order_id):
        self.__order_id = order_id
        is_added = True
        is_deleted = True
        if order_id not in self.__added_orders:
            is_added = self.__added_event.wait(time)
        if order_id not in self.__deleted_orders:
            is_deleted = self.__deleted_event.wait(time)
        return is_added and is_deleted

    def reset(self):
        self.__order_id = None
        self.__added_orders.clear()
        self.__deleted_orders.clear()
        self.__added_event.clear()
        self.__deleted_event.clear()


def _find_trade_by_instrument(fx, account_id, instrument):
    """Find an open trade by instrument name."""
    offer = Common.get_offer(fx, instrument)
    if offer is None:
        return None, None
    trade = Common.get_trade(fx, account_id, offer.offer_id)
    return trade, offer


def _find_trade_by_id(fx, account_id, trade_id):
    """Find an open trade by trade_id."""
    trades_table = fx.get_table(ForexConnect.TRADES)
    for trade_row in trades_table:
        if trade_row.trade_id == trade_id and trade_row.account_id == account_id:
            offer = fx.get_table(ForexConnect.OFFERS)
            for offer_row in offer:
                if offer_row.offer_id == trade_row.offer_id:
                    return trade_row, offer_row
            return trade_row, None
    return None, None


def main():
    args = parse_args()

    if not args.instrument and not args.trade_id:
        print(json.dumps({"error": "Must specify -i INSTRUMENT or --trade-id TRADE_ID"}))
        exit(1)

    str_user_id, str_password, str_url, str_connection, str_account = (
        jgtcommon.read_fx_str_from_config(demo=args.demo)
    )
    str_session_id = ""
    str_pin = ""

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

            # Find the trade to close
            if args.trade_id:
                trade, offer = _find_trade_by_id(fx, str_account, args.trade_id)
                if not trade:
                    print(json.dumps({"error": "Trade {0} not found".format(args.trade_id)}))
                    fx.logout()
                    exit(1)
            else:
                trade, offer = _find_trade_by_instrument(fx, str_account, args.instrument)
                if not trade:
                    print(
                        json.dumps(
                            {
                                "error": "No open position for instrument '{0}'".format(
                                    args.instrument
                                )
                            }
                        )
                    )
                    fx.logout()
                    exit(1)

            # Determine amount to close
            if args.lots > 0 and offer:
                login_rules = fx.login_rules
                tsp = login_rules.trading_settings_provider
                base_unit_size = tsp.get_base_unit_size(
                    offer.instrument if hasattr(offer, "instrument") else args.instrument,
                    account,
                )
                amount = base_unit_size * args.lots
            else:
                amount = trade.amount  # close full position

            # Reverse direction for close
            buy = fxcorepy.Constants.BUY
            sell = fxcorepy.Constants.SELL
            buy_sell = sell if trade.buy_sell == buy else buy

            request = fx.create_order_request(
                order_type=fxcorepy.Constants.Orders.TRUE_MARKET_CLOSE,
                OFFER_ID=trade.offer_id,
                ACCOUNT_ID=str_account,
                BUY_SELL=buy_sell,
                AMOUNT=amount,
                TRADE_ID=trade.trade_id,
            )

            if request is None:
                print(json.dumps({"error": "Cannot create close request"}))
                fx.logout()
                exit(1)

            orders_monitor = OrdersMonitor()
            closed_trades_monitor = ClosedTradesMonitor()

            closed_trades_table = fx.get_table(ForexConnect.CLOSED_TRADES)
            orders_table = fx.get_table(ForexConnect.ORDERS)

            trades_listener = Common.subscribe_table_updates(
                closed_trades_table,
                on_add_callback=closed_trades_monitor.on_added_closed_trade,
            )
            orders_listener = Common.subscribe_table_updates(
                orders_table,
                on_add_callback=orders_monitor.on_added_order,
                on_delete_callback=orders_monitor.on_deleted_order,
            )

            try:
                resp = fx.send_request(request)
                order_id = resp.order_id

            except Exception as e:
                error_msg = str(e)
                print(json.dumps({"error": error_msg, "type": type(e).__name__}))
                trades_listener.unsubscribe()
                orders_listener.unsubscribe()
                exit(1)

            else:
                is_success = orders_monitor.wait(30, order_id)
                closed_trade_row = None
                if is_success:
                    closed_trade_row = closed_trades_monitor.wait(30, order_id)

                if closed_trade_row is None:
                    print(
                        json.dumps(
                            {
                                "order_id": order_id,
                                "trade_id": trade.trade_id,
                                "status": "submitted",
                                "warning": "Close confirmation timeout — check closed trades",
                            }
                        )
                    )
                else:
                    result = {
                        "order_id": order_id,
                        "trade_id": closed_trade_row.trade_id,
                        "close_rate": closed_trade_row.close_rate,
                        "amount": closed_trade_row.amount,
                        "gross_pl": closed_trade_row.gross_pl,
                        "status": "closed",
                    }
                    print(json.dumps(result))
                    sleep(1)

                trades_listener.unsubscribe()
                orders_listener.unsubscribe()

        except Exception as e:
            common_samples.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()

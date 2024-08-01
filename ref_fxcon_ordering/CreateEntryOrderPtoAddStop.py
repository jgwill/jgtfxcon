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
from time import sleep
from threading import Event

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples

g_rate = None
g_stop = None
g_order_id = None

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    common_samples.add_main_arguments(parser)
    common_samples.add_instrument_timeframe_arguments(parser, timeframe=False)
    common_samples.add_direction_rate_lots_arguments(parser)
    common_samples.add_account_arguments(parser)
    parser.add_argument('-stop', metavar="STOP", type=float,
                        help='Stop level')
    args = parser.parse_args()

    return args


class OrdersMonitor:
    def __init__(self):
        self.__order_id = None
        self.__orders = {}
        self.__event = Event()

    def on_added_order(self, _, __, order_row):
        global g_order_id
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
        if order_id in self.__orders:
            return self.__orders[order_id]
        else:
            return None

    def reset(self):
        self.__order_id = None
        self.__orders.clear()
        self.__event.clear()


# def change_order_pto(fx, order): #@STCissue Probably not here it would be
#     global g_stop,g_order_id,g_rate
#     if g_stop is not None:
#         print("Adding a stop to the order BUT IT MIGHT BE POSSIBLE TO DO IT RIGHT FROM THE INITIAL REQUEST")

#         pass

def main():
    global g_stop, g_order_id,g_rate
    args = parse_args()
    str_user_id = args.l
    str_password = args.p
    str_url = args.u
    str_connection = args.c
    str_session_id = args.session
    str_pin = args.pin
    str_instrument = args.i
    str_buy_sell = args.d
    str_rate = args.r
    g_rate = str_rate
    if not args.stop:
        print("Stop level must be specified")
        return
    str_stop = args.stop
    g_stop=str_stop
    str_lots = args.lots
    str_account = args.account
    print("Starting example for adding a stop to an entry order with \nentry rate: {0:.5f}, stop: {1:.5f}".format(
        str_rate, str_stop))

    with ForexConnect() as fx:
        fx.login(str_user_id, str_password, str_url, str_connection, str_session_id,
                 str_pin, common_samples.session_status_changed)

        try:
            account = Common.get_account(fx, str_account)
            if not account:
                raise Exception(
                    "The account '{0}' is not valid".format(str_account))

            else:
                str_account = account.account_id
                print("AccountID='{0}'".format(str_account))

            offer = Common.get_offer(fx, str_instrument)

            if offer is None:
                raise Exception(
                    "The instrument '{0}' is not valid".format(str_instrument))

            login_rules = fx.login_rules

            trading_settings_provider = login_rules.trading_settings_provider

            base_unit_size = trading_settings_provider.get_base_unit_size(
                str_instrument, account)

            amount = base_unit_size * str_lots

            entry = fxcorepy.Constants.Orders.ENTRY

            request = fx.create_order_request(
                order_type=entry,
                OFFER_ID=offer.offer_id,
                ACCOUNT_ID=str_account,
                BUY_SELL=str_buy_sell,
                RATE_STOP=str_stop,
                AMOUNT=amount,
                RATE=str_rate,
            )

            orders_monitor = OrdersMonitor()

            orders_table = fx.get_table(ForexConnect.ORDERS)
            orders_listener = Common.subscribe_table_updates(orders_table,
                                                             on_add_callback=orders_monitor.on_added_order)

            try:
                resp = fx.send_request(request)
                order_id = resp.order_id
                sleep(1)


            except Exception as e:
                #Print the type of exception
                _type_of_exception = type(e).__name__
                print("Exception type: ", _type_of_exception)
                if _type_of_exception=="RequestFailedError":
                    print("Request failed Error Handling coming up....")
                    print("INput Stop value:",str_stop)
                    orders_listener.unsubscribe()
                    exit(1)

                common_samples.print_exception(e)
                orders_listener.unsubscribe()
                exit(1)

            else:
                # Waiting for an order to appear or timeout (default 30)
                order_row = orders_monitor.wait(30, order_id)
                if order_row is None:
                    print("Response waiting timeout expired.\n")
                else:
                    print("The order has been added. OrderID={0:s}, "
                          "Type={1:s}, BuySell={2:s}, Rate={3:.5f}, TimeInForce={4:s}".format(
                        order_row.order_id, order_row.type, order_row.buy_sell, order_row.rate,
                        order_row.time_in_force))
                    # sleep(1)
                    # print("...or it is here ?? (It might be done already)")
                    # sleep(1)
                    # #@STCGoal Our Order id is here, we can now add a stop to it
                    # g_order_id = order_row.order_id
                    # change_order_pto(fx, order_row)
                orders_listener.unsubscribe()

        except Exception as e:
            common_samples.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()
    print("")
    #input("Done! Press enter key to exit\n")

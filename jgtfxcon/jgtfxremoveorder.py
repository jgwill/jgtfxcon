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
import json
import threading
from time import sleep

import os
import sys

from jgtutils.jgtclihelper import print_jsonl_message

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
from jgtutils.jgterrorcodes import ORDER_NOT_FOUND_EXIT_ERROR_CODE

from jgtutils import jgtos, jgtcommon, jgtpov

from forexconnect import fxcorepy, ForexConnect, Common

import common_samples


RAISE_EXCEPTION_ON_ORDER_NOT_FOUND = False



def parse_args(from_jgt_env=False):
    parser = jgtcommon.new_parser("JGT FX RemoveEntry Order CLI", "Remove an Entry order on FXConnect", "fxrmorder",add_exiting_quietly_flag=True)
    
    parser=jgtcommon.add_demo_flag_argument(parser,from_jgt_env=from_jgt_env)

    # specific arguments
    parser=jgtcommon.add_orderid_arguments(parser,from_jgt_env=from_jgt_env)
    
    parser=jgtcommon.add_verbose_argument(parser)

    args=jgtcommon.parse_args(parser)

    return args


class OrdersMonitor:
    def __init__(self):
        self.__order_id = None
        self.__deleted_orders = {}
        self.__event = threading.Event()

    def on_delete_order(self, _, __, order_row):
        order_id = order_row.order_id
        self.__deleted_orders[order_id] = order_row
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
        if order_id in self.__deleted_orders:
            return self.__deleted_orders[order_id]
        else:
            return None

    def reset(self):
        self.__order_id = None
        self.__deleted_orders.clear()
        self.__event.clear()


def main():
    doit(False)

def emain():
    doit(True)
    
def doit(from_jgt_env=False):
    args = parse_args(from_jgt_env)
    quiet=args.quiet
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    str_session_id = ""
    str_pin = ""
    str_old = args.orderid

    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url, str_connection, str_session_id,
                     str_pin, common_samples.session_status_changed)

            order_id = str_old
            orders_table = fx.get_table(ForexConnect.ORDERS)
            orders = orders_table.get_rows_by_column_value("order_id", order_id)
            order = None
            
            for order_row in orders:
                order = order_row
                break

            if order is None:
                msg = "Order {0} not found".format(order_id)
                order_not_found={
                    "order_id":order_id,
                    "status":"not found"
                }
                print_jsonl_message(msg,order_not_found)
                
                if RAISE_EXCEPTION_ON_ORDER_NOT_FOUND:
                    raise Exception(msg)
                else: #Exit the program with an error code 
                    sys.exit(ORDER_NOT_FOUND_EXIT_ERROR_CODE)

            order_account_id = order.account_id
            request = fx.create_request({

                fxcorepy.O2GRequestParamsEnum.COMMAND: fxcorepy.Constants.Commands.DELETE_ORDER,
                fxcorepy.O2GRequestParamsEnum.ACCOUNT_ID: order_account_id,
                fxcorepy.O2GRequestParamsEnum.ORDER_ID: str_old
            })

            orders_monitor = OrdersMonitor()

            orders_table = fx.get_table(ForexConnect.ORDERS)
            orders_listener = Common.subscribe_table_updates(orders_table, on_delete_callback=orders_monitor.on_delete_order)

            try:
                fx.send_request(request)

            except Exception as e:
                common_samples.print_exception(e)
                orders_listener.unsubscribe()
            else:
                # Waiting for an order to delete or timeout (default 30)
                is_deleted = orders_monitor.wait(30, order_id)
                if not is_deleted:
                    msg = "Response waiting timeout expired.\n"
                    timed_out={
                        "order_id":order_id,
                        "status":"waiting timeout expired"
                    }
                    print_jsonl_message(msg,timed_out)
                else:
                    msg="The order has been deleted. Order ID: {0:s}".format(order_row.order_id)
                    order_deleted={
                        "order_id":order_row.order_id,
                        "buy_sell":order_row.buy_sell,
                        "rate":order_row.rate,
                        "status":"deleted"
                                   }
                    print_jsonl_message(msg,order_deleted)
                    sleep(1)
                orders_listener.unsubscribe()

        except Exception as e:
            common_samples.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)



if __name__ == "__main__":
    main()
    
    #input("Done! Press enter key to exit\n")

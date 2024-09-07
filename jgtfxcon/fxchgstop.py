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

#INITIAL NAME : SetStop.py

import argparse
import threading
from time import sleep

import os
import sys
import json,yaml

from jgtutils.jgtclihelper import print_jsonl_message

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

from jgtutils import  jgtcommon
from jgtutils.FXTransact import FXTrade,FXTrades
from jgtutils.FXTransact import TRADE_FXMVSTOP_PREFIX
from jgtutils.FXTransact import FXTransactDataHelper as fxtdh

from forexconnect import fxcorepy, ForexConnect, Common, EachRowListener

import common_samples

str_account = None
str_instrument = None
str_stop = None
str_trade_id = None
pips_flag=False
quiet=True
fxtrade:FXTrade=None
fxtrades:FXTrades=FXTrades()
FXTRADE_DEBUG_FLAG=True
APP_SCOPE = "fxchgstop"
 
def parse_args():
    parser = jgtcommon.new_parser("JGT FX MV Trade Stop CLI", "Change stop order of trade by id on FXConnect", "fxmvstop")
    
    parser=jgtcommon.add_demo_flag_argument(parser)
    parser=jgtcommon.add_instrument_standalone_argument(parser,required=False)
    parser=jgtcommon.add_orderid_arguments(parser,required=False)
    parser=jgtcommon.add_tradeid_arguments(parser,required=False)
    parser=jgtcommon.add_stop_arguments(parser,pips_flag=True)
    parser=jgtcommon.add_account_arguments(parser,required=False)
    parser=jgtcommon.add_verbose_argument(parser)
    
    args = jgtcommon.parse_args(parser)

    return args


def change_trade(fx, trade):
    global str_trade_id
    global str_account
    global str_instrument
    global str_stop
    global pips_flag
    global fxtrade,fxtrades
    
    amount = trade.amount
    event = threading.Event()

    offer = Common.get_offer(fx, trade.instrument)

    if not offer:
        raise Exception(
            "The offer is not valid")

    buy = fxcorepy.Constants.BUY
    sell = fxcorepy.Constants.SELL

    buy_sell = sell if trade.buy_sell == buy else buy

    if str_trade_id and trade.trade_id == str_trade_id:
        msg = "Starting the Stop changes for TradeID: {0:s}".format(trade.trade_id)        
        print_jsonl_message(msg,extra_dict={"trade_id":str_trade_id},scope=APP_SCOPE)
    order_id = trade.stop_order_id
    #print("Stop OrderID: {0:s}".format(order_id))
    open_price = trade.open_rate
    last_close_price = trade.close
    amount = trade.amount
    pip_size = offer.PointSize
    #print("Open Price: {0:.5f}".format(open_price))
    #exit(0)
    #@STCIssue WTF is this for ?
    if not pips_flag:
        stopv=str_stop
    else:
        pip_size_str = "{0:.5f}".format(pip_size)
        msg=f"Stop is in PipSized: {pip_size_str} * {str_stop}"
        print(msg)
        if trade.buy_sell == buy:
            stopv = last_close_price-str_stop*pip_size
        else:
            stopv = last_close_price+str_stop*pip_size
    
    future_validation_stop = True
    if future_validation_stop:
        #from FXTradeStopValidator import FXTradeMVStopValidator
        from jgtutils.jgtfxhelper import is_entry_stop_valid
        stop_entry_validated=is_entry_stop_valid(last_close_price,stopv,trade.buy_sell)
        msg=f"Stop is invalid - Passed Current Market price" if not stop_entry_validated else f"Stop is valid"
        if not quiet or not stop_entry_validated:
            print_jsonl_message(msg,extra_dict={"last_close":last_close_price,"stop_rate":stopv,"bs":trade.buy_sell},scope=APP_SCOPE)
        if not stop_entry_validated:
            from jgtutils.jgterrorcodes import TRADE_STOP_INVALID_EXIT_ERROR_CODE
            exit(TRADE_STOP_INVALID_EXIT_ERROR_CODE)
    
    #Create an object for our outputs
    import FXCONHelperTransact as fxh
    fxtrade =fxh.trade_row_to_trade_object(trade)
    fxtrade.message=f"Requesting Trade Stop Changes: {stopv}"
    
    fxtrades.add_trade(fxtrade)
    if FXTRADE_DEBUG_FLAG:
        fxtrade.tojsonfile(use_local=True)
        
        fxtransact_save_prefix_all = TRADE_FXMVSTOP_PREFIX
        fxtransact_save_prefix = fxtransact_save_prefix_all+"01_"
    
        saved_filepath=fxtdh.save_fxtrade_to_file(fxtrade,save_prefix=fxtransact_save_prefix,prefix_to_connection=False,str_order_id=str_trade_id)
        print_jsonl_message(fxtrade.message,extra_dict={"filepath":saved_filepath},scope=APP_SCOPE)
        fxtrades.tojsonfile(use_local=True)
    #print(trade)
    #trade = FXTrade.from_string(string)
        
    
    if order_id:
        stop_order_id = trade.stop_order_id
        request = fx.create_order_request(
            order_type=fxcorepy.Constants.Orders.STOP,
            command=fxcorepy.Constants.Commands.EDIT_ORDER,
            OFFER_ID=offer.offer_id,
            ACCOUNT_ID=str_account,
            RATE=stopv,
            TRADE_ID=trade.trade_id,
            ORDER_ID=stop_order_id
        )
    else:
        stop_order_id = trade.stop_order_id
        request = fx.create_order_request(
            order_type=fxcorepy.Constants.Orders.STOP,
            command=fxcorepy.Constants.Commands.CREATE_ORDER,
            OFFER_ID=offer.offer_id,
            ACCOUNT_ID=str_account,
            BUY_SELL=buy_sell,
            RATE=stopv,
            AMOUNT=amount,
            TRADE_ID=trade.trade_id,
            ORDER_ID=stop_order_id
        )

    if request is None:
        raise Exception("Cannot create request")

    done_saving_updates=False
    
    def on_changed_order(_, __, order_row):
        nonlocal order_id,done_saving_updates
        global fxtrade,fxtrades
        if order_row.stop_order_id == order_id:
            if done_saving_updates:
                sleep(1)
                return
            msg = "Trade Stop Order changed. StopOrderID: {0:s}".format(
                order_row.trade_id)

            order_changed_data={
                "order_id":order_row.trade_id,
                "new_stop":stopv,
                "trade_id":str_trade_id
            }
            print_jsonl_message(msg,order_changed_data,scope=APP_SCOPE)
            fxtradeupdated=fxh.trade_row_to_trade_object(order_row)
            #print(fxtradeupdated.tojson())
            #fxtrade.message=msg
            fxtradeupdated.message=msg
            fxtrades.add_trade(fxtradeupdated)
            if FXTRADE_DEBUG_FLAG:
                fxtradeupdated.tojsonfile()
                #fxtradeupdated.toyamlfile()
            
                fxtransact_save_prefix = fxtransact_save_prefix_all+"02_"
                written_filepath=fxtdh.save_fxtrade_to_file(fxtrade,save_prefix=fxtransact_save_prefix,prefix_to_connection=False,str_order_id=str_trade_id)
                #@STCGoal Expect that we will have a trades.json with before the change and after the change
                fxtrades.tojsonfile()
                #fxtrades.toyamlfile()
                msg = "Changing trade stop completed and saved to file"
                
               
                if not quiet:
                    print_jsonl_message(msg,extra_dict={"filepath":written_filepath},scope=APP_SCOPE)
                #print_jsonl_message(" --DEV NOTES - WE WANT RESULTS TO OBSERVE WHEN THE TRADE WAS CHANGED - Where does get saved is the question",scope="DEV")
            done_saving_updates=True

    trades_table = fx.get_table(ForexConnect.TRADES)

    trades_listener = Common.subscribe_table_updates(trades_table,
                              on_change_callback=on_changed_order)

    try:
        resp = fx.send_request(request)
        sleep(2)

    except Exception as e:
        common_samples.print_exception(e)
        trades_listener.unsubscribe()
    else:
        # Waiting for an order to appear or timeout (default 30)
        sleep(1)
        trades_listener.unsubscribe()


def on_each_row(fx, row_data):
    global str_instrument,str_trade_id
    trade = None
    if str_instrument and row_data.instrument == str_instrument and (str_trade_id is None or str_trade_id == ""):
        #print("Changing trad, row_data:")
        #print(row_data)
        change_trade(fx, row_data)
    elif not str_instrument or str_trade_id is not None:
        if str_trade_id and row_data.trade_id == str_trade_id:
            #print("Changing trade, row_data:")
            #print(row_data)
            change_trade(fx, row_data)


def check_trades(fx, table_manager, account_id):
    orders_table = table_manager.get_table(ForexConnect.TRADES)
    if len(orders_table) == 0:
        print("There are no trades!")
    else:
        for row in orders_table:
            on_each_row(fx, row)


def main():
    global str_account
    global str_instrument
    global str_stop
    global str_trade_id
    global pips_flag

    args = parse_args()
    quiet=args.quiet
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    str_session_id = ""
    str_pin = ""
    
    str_instrument = args.instrument if args.instrument else None
    str_account = args.account
    str_stop = args.stop
    pips_flag=args.pips if args.pips else False
    
    str_trade_id = args.tradeid if args.tradeid else None
    if str_trade_id is None and args.orderid:
        str_trade_id = args.orderid #support using -id
    if str_trade_id is None:
        print("Trade ID must be specified")
        return
    
    event = threading.Event()

    if not str_stop:
        print("Stop level must be specified")
        return


    with ForexConnect() as fx:
        fx.login(str_user_id, str_password, str_url, str_connection, str_session_id,
                 str_pin, common_samples.session_status_changed)
        str_account_fix= str_account if str_connection != "Demo" else None
        account = Common.get_account(fx, str_account_fix)
        #print("Account:")
        #print(account)

        table_manager = fx.table_manager

        if not account:
            raise Exception(
                "The account '{0}' is not valid".format(account))
        else:
            str_account = account.account_id
            msg = "AccountID='{0}'".format(str_account)
            
            if not quiet:
                print_jsonl_message(msg,extra_dict={"account_id":str_account},scope=APP_SCOPE)

        #offer = Common.get_offer(fx, str_instrument)

        # if not offer:
        #     raise Exception(
        #         "The instrument '{0}' is not valid".format(str_instrument))

        check_trades(fx, table_manager, account.account_id)

        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()
    #input("Done! Press enter key to exit\n")

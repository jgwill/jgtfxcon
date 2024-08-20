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


from threading import Event

import os
import sys

from jgtutils.jgtclihelper import print_jsonl_message

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtos, jgtcommon
from jgtutils.jgterrorcodes import SUBSCRIPTION_MANAGEMENT_EXIT_ERROR_CODE

from forexconnect import ForexConnect, EachRowListener, ResponseListener

from forexconnect import fxcorepy
from forexconnect import SessionStatusListener
from forexconnect.common import Common
from time import sleep

import common_samples

SCOPE = "fxsubs"

str_instrument = None
old_status = None
current_status = None


def parse_args():
    parser = jgtcommon.new_parser("JGT FX SetSubscription for Instrument", "Deals with Instrument subscription", "fxsetsubscription")
    parser=jgtcommon.add_demo_flag_argument(parser)
    parser=jgtcommon.add_instrument_standalone_argument(parser,required=True)
    
    #flag to get the status
    xclusive_group = parser.add_mutually_exclusive_group(required=True)
    xclusive_group.add_argument('-I','--info',action='store_true',
                        help='Info only on the tatus')
    xclusive_group.add_argument('-S','-A','-T','--active',action='store_true',help='Activate a subscription')
    xclusive_group.add_argument('-D','-U','--deactivate',action='store_true',help='Deactivate a subscription')
    
    #parser.add_argument('-S','--status', metavar="STATUS", required=True,
    #                    help='Status')
    args=jgtcommon.parse_args(parser)
    

    return args


def get_offer(fx, s_instrument):
    table_manager = fx.table_manager
    offers_table = table_manager.get_table(ForexConnect.OFFERS)
    for offer_row in offers_table:
        if offer_row.instrument == s_instrument:
            return offer_row

class SubscriptionMonitor:
    def __init__(self):
        self.__subscription_status = None
        self.__event = Event()
    
    def wait(self, time):
        self.__event.wait(time)
        return self.get_status()
    
    def get_status(self):
        return self.__subscription_status
    
    def reset(self):
        self.__subscription_status = None
        self.__event.clear()
    
    #on_status_change_callback : typing.Callable[[AO2GTableListener, O2GTableStatus], None]
    ##The function that is called when the table status is changed.
    def on_status_change(self, table_listener, status):
        global old_status
        global current_status
        self.__subscription_status = status
        print("Subscription status changed to ", status)
        self.__event.set()
        #print("Event set")
        
    def on_changed(self,table_listener, row_id, row):
        global str_instrument
        global old_status
        global current_status
        #print("Row changed:",row_id)
        if row.instrument == str_instrument:
            current_status = row.subscription_status
            if current_status != old_status:
                self.__subscription_status = current_status
                _print_subscription_info(current_status,extra_info="status changed")
                
                old_status = current_status
                self.__event.set()
        return

        #return _on_changed


def main():
    global str_instrument
    global old_status
    args = parse_args()
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)
    
    str_session_id = ""
    str_pin = ""
    str_instrument = args.instrument
    
    info_only_flag = args.info
    active_flag=args.active
    deactivate_flag=args.deactivate
    target_status="T" if active_flag else "D" if deactivate_flag else None

    update_subscription(str_user_id, str_password, str_url, str_connection, str_session_id, str_pin, info_only_flag, target_status)

def update_subscription(str_user_id, str_password, str_url, str_connection, str_session_id, str_pin, info_only_flag, target_status=None,validation_pass=False):
    global old_status
    global current_status
    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url,
                     str_connection, str_session_id, str_pin,
                     common_samples.session_status_changed)

            offer = get_offer(fx, str_instrument)

            i = offer.instrument
            context_status_code = offer.subscription_status
            
            
            
            
            
            if info_only_flag==True:
                _print_subscription_info(context_status_code)
                _logout(fx)
                if context_status_code!=target_status:
                    exit(SUBSCRIPTION_MANAGEMENT_EXIT_ERROR_CODE)
                exit(0)
                
            old_status = offer.subscription_status

            if target_status == old_status :
                context_status_label=get_subscription_status_label(context_status_code)
                msg=f"{str_instrument} already {context_status_label}, nothing to change."                
                _print_subscription_info(context_status_code)
                print_jsonl_message(msg,scope=SCOPE)
                _logout(fx)
                exit(0)
                #raise Exception('New status = current status')
            offers_table = fx.get_table(ForexConnect.OFFERS)

            request = fx.create_request({
                fxcorepy.O2GRequestParamsEnum.COMMAND: fxcorepy.Constants.Commands.SET_SUBSCRIPTION_STATUS,
                fxcorepy.O2GRequestParamsEnum.OFFER_ID: offer.offer_id,
                fxcorepy.O2GRequestParamsEnum.SUBSCRIPTION_STATUS: target_status
            })

            monitor=SubscriptionMonitor()
            
            offers_listener = Common.subscribe_table_updates(offers_table, on_change_callback=monitor.on_changed)
                                                             #,on_status_change_callback=monitor.on_status_change)

            try:
                target_status_label=get_subscription_status_label(target_status)
                print_jsonl_message(f"status changing for {target_status_label} {str_instrument}",extra_dict={"old_code":old_status,"target_code":target_status},scope=SCOPE)
                
                resp=fx.send_request(request)
                sleep(1)

            except Exception as e:
                common_samples.print_exception(e)
                offers_listener.unsubscribe()
            else:
                # sleep(1)
                _monitor_results = monitor.wait(2)
                if _monitor_results is None:
                    #Loop back to git the status info
                    target_status_1=target_status
                    update_subscription(str_user_id, str_password, str_url, str_connection, str_session_id, str_pin, True,target_status_1,True)
                #print("Wait value ", _new_status)
                #print("Monitor status:", monitor.get_status())
                
                offers_listener.unsubscribe()
                if not current_status==target_status:
                    print_jsonl_message(f"Subscription change failed for {str_instrument}",extra_dict={"target_status":target_status_label,"code":target_status},scope=SCOPE)
                    exit(SUBSCRIPTION_MANAGEMENT_EXIT_ERROR_CODE)

        except Exception as e:
            common_samples.print_exception(e)

        _logout(fx)

def _print_subscription_info(context_status_code,extra_info=""):
    context_status_label = get_subscription_status_label(context_status_code)
    string = str_instrument+' is '+context_status_label 
    print_jsonl_message(string,extra_dict={"instrument":str_instrument,"subscription":context_status_label,"code":context_status_code, "info":extra_info},scope=SCOPE)

def get_subscription_status_label(context_status_code):
    return "Active" if context_status_code=="T" else "Inactive" if context_status_code=="D" else "Unknown"

def _logout(fx):
    try:
        fx.logout()
    except Exception as e:
        common_samples.print_exception(e)


if __name__ == "__main__":
    main()
    

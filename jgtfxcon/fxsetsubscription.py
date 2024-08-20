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

from jgtutils import jgtos, jgtcommon

from forexconnect import ForexConnect, EachRowListener, ResponseListener

from forexconnect import fxcorepy
from forexconnect import SessionStatusListener
from forexconnect.common import Common
from time import sleep

import common_samples

SCOPE = "fxsymbolsubscription"

str_instrument = None
old_status = None
new_status = None


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


def on_changed():
    def _on_changed(table_listener, row_id, row):
        global str_instrument
        global old_status
        global new_status
        if row.instrument == str_instrument:
            new_status = row.subscription_status
            if new_status != old_status:
                context_status_label = get_subscription_status_label(new_status)
                _print_subscription_info(new_status, context_status_label)
                
                old_status = new_status
        return

    return _on_changed


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

    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url,
                     str_connection, str_session_id, str_pin,
                     common_samples.session_status_changed)

            offer = get_offer(fx, str_instrument)

            i = offer.instrument
            context_status_code = offer.subscription_status
            
            context_status_label = get_subscription_status_label(context_status_code)
            
            
            
            if info_only_flag==True:
                _print_subscription_info(context_status_code, context_status_label)
                _logout(fx)
                exit(0)
                
            old_status = offer.subscription_status

            if target_status == old_status and not info_only_flag:
                msg=f"{str_instrument} already {context_status_label}, nothing to change."                
                _print_subscription_info(context_status_code, context_status_label)
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

            offers_listener = Common.subscribe_table_updates(offers_table, on_change_callback=on_changed())

            try:
                target_status_label=get_subscription_status_label(target_status)
                print_jsonl_message(f"Changing subscription status for {str_instrument}",extra_dict={"target_status":target_status_label,"code":target_status},scope=SCOPE)
                resp=fx.send_request(request)
                sleep(5)

            except Exception as e:
                common_samples.print_exception(e)
                offers_listener.unsubscribe()
            else:
                sleep(1)
                offers_listener.unsubscribe()

        except Exception as e:
            common_samples.print_exception(e)

        _logout(fx)

def _print_subscription_info(context_status_code, context_status_label):
    string = str_instrument+' is '+context_status_label 
    print_jsonl_message(string,extra_dict={"instrument":str_instrument,"subscription":context_status_label,"code":context_status_code},scope=SCOPE)

def get_subscription_status_label(context_status_code):
    return "Active" if context_status_code=="T" else "Inactive" if context_status_code=="D" else "Unknown"

def _logout(fx):
    try:
        fx.logout()
    except Exception as e:
        common_samples.print_exception(e)


if __name__ == "__main__":
    main()
    

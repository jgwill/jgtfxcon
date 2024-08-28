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
import datetime
import os
import sys

from jgtutils.jgtclihelper import print_jsonl_message

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

from jgtutils import jgtos, jgtcommon, jgtpov
import tlid
from jgtutils.FXTransact import FXREPORT_FILE_PREFIX
from jgtutils.jgtfxhelper import mkfn_cfxdata_filepath

import re
from urllib.parse import urlsplit
from urllib.request import urlopen

from forexconnect import ForexConnect

import common_samples

quiet=True

def parse_args():
    parser = jgtcommon.new_parser("JGT FX Report CLI", "Obtain a report from FXConnect", "fxreport")
    parser=jgtcommon.add_demo_flag_argument(parser)
    #parser = argparse.ArgumentParser(description='Process command parameters.')
    #common_samples.add_main_arguments(parser)
    parser=jgtcommon.add_verbose_argument(parser)

    parser=jgtcommon.add_report_date_arguments(parser)
    
    #report_format = "html"
    parser.add_argument('-F', '--report_format', metavar="FORMAT", default="html",
                        help='The report format. Possible values are: html, pdf, xls. Default value is html. Optional parameter.')
    #args = parser.parse_args()
    args=jgtcommon.parse_args(parser)

    return args


def month_delta(date, delta):
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
    return date.replace(day=d, month=m, year=y)

report_format = "html"

def get_reports(fc:ForexConnect, dt_from, dt_to):
    global quiet
    global report_format
    accounts_response_reader = fc.get_table_reader(ForexConnect.ACCOUNTS)
    if dt_to is None:
        dt_to = datetime.datetime.today()
    if dt_from is None:
        dt_from = month_delta(datetime.datetime.today(), -1)
    
    for account in accounts_response_reader:

        msg = "Obtaining report URL..."
        print_jsonl_message(msg, scope="fxreport")
        url = fc.session.get_report_url(account.account_id, dt_from, dt_to, report_format, None)
        
        if not quiet:
            print("account_id={0:s}; Balance={1:.5f}".format(account.account_id, account.balance))
        #report_url = "Report URL={0:s}\n".format(url)
        print_jsonl_message("Report Generated",extra_dict={"report_url":url},scope="fxreport")
        report_basename = f"{FXREPORT_FILE_PREFIX}{account.account_id}"
        fn = f"{report_basename}__{tlid.get_minutes()}.{report_format}"
        file_name = mkfn_cfxdata_filepath(fn) #os.path.join(os.getcwd())
        
        if not quiet:print("Connecting...")
        response = urlopen(url)
        if not quiet:print("OK")
        if not quiet:print("Downloading report...")

        abs_path = '{0.scheme}://{0.netloc}/'.format(urlsplit(url))
        if report_format == "html":
            with open(file_name, 'w') as file:
                report = response.read().decode('utf-8')
                report = re.sub(r'((?:src|href)=")[/\\](.*?")', r'\1' + abs_path + r'\2', report)
                file.write(report)
        elif report_format == "pdf" or report_format == "xls":
            with open(file_name, 'wb') as file:
                file.write(response.read())
        else:
            raise ValueError("Invalid report format")
        msg = "Report is saved"
        print_jsonl_message(msg,extra_dict={"file_name":file_name},scope="fxreport")


def main():
    global quiet
    global report_format
    args = parse_args()
    quiet=args.quiet
    report_format=args.report_format
    str_user_id,str_password,str_url, str_connection,str_account = jgtcommon.read_fx_str_from_config(demo=args.demo)

    str_session_i_d=""
    str_pin=""
    date_from = args.datefrom
    date_to = args.dateto

    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url, str_connection,
                     str_session_i_d, str_pin, common_samples.session_status_changed)
            
            get_reports(fx, date_from, date_to)

        except Exception as e:
            common_samples.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            common_samples.print_exception(e)


if __name__ == "__main__":
    main()
    print("")

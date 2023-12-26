#import jgtfxcon

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import jgtconstants as constants
import jgtfxcommon as jgtfxcommon
import argparse

import JGTPDS as pds

from JGTPDS import getPH as get_price, stayConnectedSetter as set_stay_connected, disconnect,connect as on,disconnect as off, status as connection_status,  getPH2file as get_price_to_file, getPHByRange as get_price_range, stayConnectedSetter as sc,getPH as ph,getPH_to_filestore as ph2fs

import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    #jgtfxcommon.add_main_arguments(parser)
    jgtfxcommon.add_instrument_timeframe_arguments(parser)
    #jgtfxcommon.add_date_arguments(parser)
    jgtfxcommon.add_tlid_range_argument(parser)
    jgtfxcommon.add_max_bars_arguments(parser)
    #jgtfxcommon.add_output_argument(parser)
    #jgtfxcommon.add_quiet_argument(parser)
    jgtfxcommon.add_verbose_argument(parser)
    jgtfxcommon.add_debug_argument(parser)
    jgtfxcommon.add_cds_argument(parser)
    jgtfxcommon.add_iprop_init_argument(parser)
    jgtfxcommon.add_pdsserver_argument(parser)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    instrument = args.instrument
    timeframe = args.timeframe
    using_tlid = False
    date_from = None
    date_to = None
    if args.tlidrange is not None:
        using_tlid= True
        tlid_range = args.tlidrange
        #print(tlid_range)
        dtf,dtt = jgtfxcommon.tlid_range_to_start_end_datetime(tlid_range)
        #print(str(dtf) + " " + str(dtt))
        date_from =dtf
        date_to = dtt
    else:
        quotes_count = args.quotescount
    debug = args.debug
    if args.server == True:
        try:
            from . import pdsserver as svr
            svr.app.run(debug=debug)
        except:
            print("Error starting server")
            return
    if args.iprop == True:
        try:
            from . import dl_properties
            print("--------------------------------------------------")
            print("------Iprop should be downloaded in $HOME/.jgt---")
            return # we quit
        except:
            print("---BAHHHHHHHHHH Iprop trouble downloading-----")
            return
        


    
    compress=False
    verbose_level = args.verbose
    quiet=False
    output = True   # We always output
    if verbose_level == 0:
        quiet=True
    #print("Verbose level : " + str(verbose_level))

    if args.compress:
        compress = args.compress
        

    if verbose_level > 1:
        if date_from:
            print(" Date from : " + str(date_from))
        if date_to:
            print(" Date to : " + str(date_to))


    try:
        
        print_quiet(quiet,"Getting for : " + instrument + "_" + timeframe)
        instruments = instrument.split(',')
        timeframes = timeframe.split(',')

        pds.stayConnectedSetter(True)
        for instrument in instruments:
            for timeframe in timeframes:
                fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, date_from, date_to, False, quiet, compress)
                print_quiet(quiet, fpath)

        pds.disconnect()  
    except Exception as e:
        jgtfxcommon.print_exception(e)

    try:
        off()
    except Exception as e:
        jgtfxcommon.print_exception(e)

# print("")
# #input("Done! Press enter key to exit\n")




def print_quiet(quiet,content):
    if not quiet:
        print(content)


if __name__ == "__main__":
    main()

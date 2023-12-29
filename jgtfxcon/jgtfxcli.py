
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
#import jgtfxcommon as jgtcommon
from jgtutils import jgtos,jgtcommon
import argparse

import JGTPDS as pds

from JGTPDS import getPH as get_price, stayConnectedSetter as set_stay_connected, disconnect,connect as on,disconnect as off, status as connection_status,  getPH2file as get_price_to_file, getPHByRange as get_price_range, stayConnectedSetter as sc,getPH as ph,getPH_to_filestore as ph2fs

import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    #jgtfxcommon.add_main_arguments(parser)
    jgtcommon.add_instrument_timeframe_arguments(parser)
    #jgtfxcommon.add_date_arguments(parser)
    jgtcommon.add_tlid_range_argument(parser)
    jgtcommon.add_max_bars_arguments(parser)
    #jgtfxcommon.add_output_argument(parser)
    jgtcommon.add_compressed_argument(parser)
    #jgtfxcommon.add_quiet_argument(parser)
    jgtcommon.add_verbose_argument(parser)
    jgtcommon.add_debug_argument(parser)
    #jgtfxcommon.add_cds_argument(parser)
    jgtcommon.add_iprop_init_argument(parser)
    jgtcommon.add_pdsserver_argument(parser)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    instrument = args.instrument
    timeframe = args.timeframe
    quotes_count = -1
    using_tlid = False
    tlid_range= None
    date_from = None
    date_to = None
    if args.tlidrange is not None:
        using_tlid= True
        tlid_range = args.tlidrange
        #print(tlid_range)
        #dtf,dtt = jgtfxcommon.tlid_range_to_start_end_datetime(tlid_range)
        #print(str(dtf) + " " + str(dtt))
        #date_from =dtf
        #date_to = dtt
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
        

    print(instrument,timeframe,quotes_count,using_tlid,quiet,compress,tlid_range)


    try:
        
        print_quiet(quiet,"Getting for : " + instrument + "_" + timeframe)
        instruments = instrument.split(',')
        timeframes = timeframe.split(',')

        pds.stayConnectedSetter(True)
        for instrument in instruments:
            for timeframe in timeframes:
                #print("---------DEBUG jgtfxcli ------")
                fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, None, None, False, quiet, compress,tlid_range=tlid_range)
                print_quiet(quiet, fpath)

        pds.disconnect()  
    except Exception as e:
        jgtcommon.print_exception(e)

    try:
        off()
    except Exception as e:
        jgtcommon.print_exception(e)

# print("")
# #input("Done! Press enter key to exit\n")




def print_quiet(quiet,content):
    if not quiet:
        print(content)


if __name__ == "__main__":
    main()

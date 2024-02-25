TEST_MODE=False
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
#import jgtfxcommon as jgtcommon
from jgtutils import jgtos,jgtcommon,jgtpov
import argparse

import JGTPDS as pds

#from JGTPDS import getPH as get_price, stayConnectedSetter as set_stay_connected, disconnect,connect as on,disconnect as off, status as connection_status,  getPH2file as get_price_to_file, stayConnectedSetter as sc,getPH as ph,getPH_to_filestore as ph2fs

import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    #jgtfxcommon.add_main_arguments(parser)
    jgtcommon.add_instrument_timeframe_arguments(parser)
    #jgtfxcommon.add_date_arguments(parser)
    jgtcommon.add_tlid_range_argument(parser)
    jgtcommon.add_max_bars_arguments(parser)
    jgtcommon.add_viewpath_argument(parser)
    jgtcommon.add_exit_if_error(parser)
    #jgtfxcommon.add_output_argument(parser)
    jgtcommon.add_compressed_argument(parser)
    jgtcommon.add_use_full_argument(parser)
    
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
    exit_on_error = False
    if args.exitonerror:
        exit_on_error = True
    
    instrument = args.instrument
    timeframe = args.timeframe
    use_full=False
    if args.full:
        use_full = True
    quotes_count = -1
    using_tlid = False
    tlid_range= None
    viewpath = args.viewpath
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
    
    quotes_count = args.quotescount
    
        
    #print(args.quotescount)
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
        

    

    try:
        
        #print_quiet(quiet,"Getting for : " + instrument + "_" + timeframe)
        instruments = instrument.split(',')
        timeframes = timeframe.split(',')


        if not viewpath:pds.stayConnectedSetter(True)
        
        for instrument in instruments:
            for timeframe in timeframes:
                if use_full and quotes_count == -1:
                    pov_full_M1 = int(os.getenv('pov_full_M1', '1000'))
                    quotes_count = int(jgtpov.calculate_quote_counts_tf(pov_full_M1)[timeframe]) #We will download a lot of data relative to each timeframe
                    print_quiet(quiet,f"DEBUG:: {instrument}_{timeframe}  Quotes count Adjusted (--full): " + str(quotes_count))
                    
                    
                    
                if not viewpath:
                    #print("---------DEBUG jgtfxcli ------")
                    if quotes_count==-1:
                        fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, None, None, False, quiet, compress,tlid_range=tlid_range,use_full=use_full)
                    else:
                        #we will try to call with an end date from tlid and a count (so we would have only an end date)
                        start_date = None;end_date = None
                        try: start_date,end_date = jgtos.tlid_range_to_start_end_datetime(tlid_range)
                        except:pass
                        if TEST_MODE:
                            print("----------TEST_MODE--------")
                            print("start_date : " + str(start_date))
                            print("end_date : " + str(end_date))
                        try:
                            fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, None, end_date, False, quiet, compress,use_full=use_full)
                            print_quiet(quiet, fpath)
                        except Exception as e:
                            error_message = f"An error occurred with {instrument} {timeframe}: {e}"
                            if exit_on_error:
                                print_quiet(quiet,error_message)
                                sys.exit(1)
                            else:
                                print("Failed getting:" + instrument + "_" + timeframe)
                                print("fxcli2console ", sys.argv[1:])
                        if TEST_MODE:
                            print(df.head(1))
                            print(df.tail(1))
                            df.to_csv("test.csv")
                        
                else:
                    fpath = pds.create_filestore_path(instrument, timeframe, quiet, compress, tlid_range,output_path=None,nsdir="pds",use_full=use_full)
                    print(fpath)
                        #pds.mk_fullpath(instrument, timeframe, tlid_range=tlid_range)

        if not viewpath:pds.disconnect()  
    except Exception as e:
        jgtcommon.print_exception(e)

    try:
        pds.disconnect()
    except Exception as e:
        jgtcommon.print_exception(e)

# print("")
# #input("Done! Press enter key to exit\n")




def print_quiet(quiet,content):
    if not quiet:
        print(content)


if __name__ == "__main__":
    main()
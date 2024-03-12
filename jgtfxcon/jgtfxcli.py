TEST_MODE = False
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants

# import jgtfxcommon as jgtcommon
from jgtutils import jgtos, jgtcommon, jgtpov
import argparse
import subprocess

import JGTPDS as pds,JGTPDSSvc as svc

import pandas as pd
verbose_level=0

def parse_args():
    parser = argparse.ArgumentParser(description="Process command parameters.")
    # jgtfxcommon.add_main_arguments(parser)
    jgtcommon.add_instrument_timeframe_arguments(parser)
    # jgtfxcommon.add_date_arguments(parser)
    jgtcommon.add_tlid_range_argument(parser)
    jgtcommon.add_max_bars_arguments(parser)
    jgtcommon.add_viewpath_argument(parser)
    jgtcommon.add_exit_if_error(parser)
    # jgtfxcommon.add_output_argument(parser)
    jgtcommon.add_compressed_argument(parser)
    jgtcommon.add_use_full_argument(parser)

    # jgtfxcommon.add_quiet_argument(parser)
    jgtcommon.add_verbose_argument(parser)
    jgtcommon.add_debug_argument(parser)
    # jgtfxcommon.add_cds_argument(parser)
    jgtcommon.add_iprop_init_argument(parser)
    jgtcommon.add_pdsserver_argument(parser)
    args = parser.parse_args()
    return args


def main():
    global verbose_level
    args = parse_args()
    exit_on_error = False
    if args.exitonerror: #@STCIssue DEPRECATING
        exit_on_error = True

    instrument = args.instrument
    timeframe = args.timeframe
    use_full = False
    if args.full:
        use_full = True
    
    using_tlid = False
    tlid_range = None
    viewpath = args.viewpath
    if viewpath:
        print("Viewpath is on")

    if args.tlidrange is not None:
        using_tlid = True
        tlid_range = args.tlidrange


    quotes_count = args.quotescount if not use_full and tlid_range is None else -1

    # print(args.quotescount)
    debug = args.debug
    if args.server == True:
        try:
            from . import pdsserver as svr
            print("#@STCIssue DEPRECATING  Starting server - REQUIRES Upgrade and rethingking as it might be migrated to jgtpy")
            svr.app.run(debug=debug)
        except:
            print("Error starting server")
            return
    if args.iprop == True: 
        try:
            from . import dl_properties

            print("--------------- #@STCIssue DEPRECATING-----------------------------------")
            print("------Iprop should be downloaded in $HOME/.jgt---")
            return  # we quit
        except:
            print("---BAHHHHHHHHHH Iprop trouble downloading-----")
            return

    compressed = False
    verbose_level = args.verbose
    quiet = False
    with_index = False
    start_date = None
    end_date = None
    
 
    if verbose_level < 2 :  # verbose 2 is not quiet
        quiet = True
    
    # if not quiet and verbose_level == 0:
    #     verbose_level=2  # Default to verbose 2 if not quiet
    # if (verbose_level == 0 or verbose_level == 1) and not quiet:  # verbose 2 is not quiet
    #     quiet = True

    

    if args.compress:
        compressed = args.compress

    try:

        updated_povs:list=svc.getPHs(instrument=instrument,timeframe=timeframe,quote_count=quotes_count,start=start_date,end=end_date,with_index=with_index,quiet=quiet,compressed=compressed,tlid_range=tlid_range,use_full=use_full,verbose_level=verbose_level,view_output_path_only=viewpath)
        
        for i in updated_povs:
            vprint(i,1)
        
            
    except Exception as e:
        jgtcommon.print_exception(e)

    # try:
    #     pds.disconnect()
    # except Exception as e:
    #     jgtcommon.print_exception(e)



def print_quiet(quiet, content):
    if not quiet:
        print(content)

def vprint(content,level=1):
    global verbose_level
    if level <= verbose_level:
        print(content)

if __name__ == "__main__":
    main()

import jgtfxcon

from . import jgtconstants as constants
from . import jgtfxcommon
import argparse

from . import JGTPDS as pds

import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description='Process command parameters.')
    #jgtfxcommon.add_main_arguments(parser)
    jgtfxcommon.add_instrument_timeframe_arguments(parser)
    jgtfxcommon.add_date_arguments(parser)
    jgtfxcommon.add_max_bars_arguments(parser)
    jgtfxcommon.add_output_argument(parser)
    #jgtfxcommon.add_quiet_argument(parser)
    jgtfxcommon.add_verbose_argument(parser)
    jgtfxcommon.add_cds_argument(parser)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    instrument = args.instrument
    timeframe = args.timeframe
    quotes_count = args.quotescount
    date_from = None
    date_to = None

    if args.datefrom:
        date_from = args.datefrom.replace('/', '.')
    if args.dateto:
        date_to = args.dateto.replace('/', '.')

    
    output=False
    compress=False
    verbose_level = args.verbose
    quiet=False
    if verbose_level == 0:
        quiet=True
    print("Verbose level : " + str(verbose_level))

    if args.compress:
        compress = args.compress
        output = True # in case
    if args.output:
        output = True

    if verbose_level > 1:
        if date_from:
            print("Date from : " + str(date_from))
        if date_to:
            print("Date to : " + str(date_to))


    try:
        
        print_quiet(quiet,"Getting for : " + instrument + "_" + timeframe)
        instruments = instrument.split(',')
        timeframes = timeframe.split(',')

        pds.stayConnectedSetter(True)
        for instrument in instruments:
            for timeframe in timeframes:
                if output:
                    fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, date_from, date_to, False, quiet, compress)
                    print_quiet(quiet, fpath)
                else:
                    p = pds.getPH(instrument, timeframe, quotes_count, date_from, date_to, False, quiet)
                    if verbose_level > 0:
                        print(p)
        pds.disconnect()  
    except Exception as e:
        jgtfxcommon.print_exception(e)

    try:
        jgtfxcon.off()
    except Exception as e:
        jgtfxcommon.print_exception(e)

# if __name__ == "__main__":
#     main()

# print("")
# #input("Done! Press enter key to exit\n")




def print_quiet(quiet,content):
    if not quiet:
        print(content)

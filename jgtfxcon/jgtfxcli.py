TEST_MODE=False
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtconstants as constants
#import jgtfxcommon as jgtcommon
from jgtutils import jgtos,jgtcommon,jgtpov
import argparse
import subprocess

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
                        try:
                            fpath,df = pds.getPH2file(instrument, timeframe, quotes_count, None, None, False, quiet, compress,tlid_range=tlid_range,use_full=use_full)
                        except Exception as e:
                            error_message = f"An error occurred with {instrument} {timeframe}: {e}"
                            to_run_cmd = f"fxcli2console -i {instrument} -t {timeframe}" 
                            opath=get_output_fullpath(instrument, timeframe, use_full, tlid_range, compress, quiet)
                            
                            #print("------------------------------------")
                            #
                            run_alt=os.getenv('RUN_ALT',0)
                            
                            ran_ok = False
                            if run_alt == 1 or run_alt == "1":
                                print("Running ALT command...")
                                print(to_run_cmd + " > " + opath)
                                ran_ok = run_command(to_run_cmd, opath)
                            else:
                                print("Not running ALT command...(RUN_ALT==)" + str(run_alt))
                                
                            if exit_on_error:
                                if not run_alt:
                                    print_quiet(quiet,error_message)
                                    sys.exit(1)
                                else:
                                    sys.exit(0)
                                #run_command(to_run_cmd, opath)
                            # else:
                            #     print("# Failed getting:" + instrument + "_" + timeframe)
                                #to_run_cmd="fxcli2console " 
                                #for myarg in sys.argv[1:]:
                                #    to_run_cmd += myarg + " "
                                
                                #to_run_cmd = to_run_cmd.replace("--full"," ").replace("-uf"," ")
                                # Launch the command and redirect the output to the file opath
                                #print(to_run_cmd + " > " + opath)
                                #sys.exit(1)
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
                            to_run_cmd = f"fxcli2console -i {instrument} -t {timeframe}" 
                            opath=get_output_fullpath(instrument, timeframe, use_full, tlid_range, compress, quiet)
                            
                            run_alt=os.getenv('RUN_ALT',0)
                            ran_ok = False
                            if run_alt == 1:
                                print("Running ALT command...")
                                ran_ok = run_command(to_run_cmd, opath)
                            else:
                                print("Not running ALT command...(RUN_ALT==)" + str(run_alt))
                                
                            if not ran_ok:                                
                                print(to_run_cmd + " > " + opath)
                                print("------------------------------------")
                                print("# Failed getting:" + instrument + "_" + timeframe)
                                
                            if exit_on_error:
                                print_quiet(quiet,error_message)
                                #run_command(to_run_cmd, opath)
                                sys.exit(1)
                            # else:
                            #     #to_run_cmd="fxcli2console " 
                            #     #for myarg in sys.argv[1:]:
                            #     #    to_run_cmd += myarg + " "
                                
                            #     #to_run_cmd = to_run_cmd.replace("--full"," ").replace("-uf"," ")
                            #     # Launch the command and redirect the output to the file opath
           
                            #     #
                                
                            #     sys.exit(1)
                                
                        if TEST_MODE:
                            print(df.head(1))
                            print(df.tail(1))
                            df.to_csv("test.csv")
                        
                else:
                    fpath = get_output_fullpath(instrument, timeframe, use_full, tlid_range, compress, quiet)
                    print(fpath)
                        #pds.mk_fullpath(instrument, timeframe, tlid_range=tlid_range)

        if not viewpath:pds.disconnect()  
    except Exception as e:
        jgtcommon.print_exception(e)

    try:
        pds.disconnect()
    except Exception as e:
        jgtcommon.print_exception(e)

def get_output_fullpath(instrument, timeframe, use_full, tlid_range, compress, quiet):
    return pds.create_filestore_path(instrument, timeframe, quiet, compress, tlid_range,output_path=None,nsdir="pds",use_full=use_full)

def run_command(command, opath):
    with open(opath, 'w') as f:
        try:
            subprocess.run(command, stdout=f, shell=True)
            print("Ran ALT command ok.")
            return True
        except Exception as e:
            print("Exception details: " + str(e))
            print("Error running ALT command")
            return False

# print("")
# #input("Done! Press enter key to exit\n")

def print_quiet(quiet,content):
    if not quiet:
        print(content)


if __name__ == "__main__":
    main()
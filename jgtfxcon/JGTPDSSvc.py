import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

_verbose_level=0

from jgtutils import jgtconstants as constants

# import jgtfxcommon as jgtcommon
from jgtutils import jgtos, jgtcommon, jgtpov
import argparse
import subprocess

import JGTPDS as pds

import pandas as pd

def getPHs(instrument,timeframe,quote_count:int=-1,start=None,end=None,with_index=True,quiet=True,compressed=False,tlid_range=None,use_full=False,default_quote_count = 335,default_add_quote_count = 89,verbose_level=0,view_output_path_only=False):
  global _verbose_level
  instruments = instrument if isinstance(instrument, list) else instrument.split(",")
  timeframes = timeframe if isinstance(timeframe, list) else timeframe.split(",")
  
  if not view_output_path_only:  pds.stayConnectedSetter(True) #@a Connected
  updated_povs = []
  for instrument in instruments:
    pov_full_M1 = int(os.getenv("pov_full_M1", "1000"))
    for timeframe in timeframes:
      pov=instrument + "_" + timeframe         
      vprint("Getting for : " + instrument + "_" + timeframe,1)
      fpath,df = getPH(instrument,timeframe,quote_count,start,end,with_index,quiet,compressed,tlid_range,use_full,default_quote_count,default_add_quote_count,verbose_level,view_output_path_only)
      
      if view_output_path_only or verbose_level>0 or not quiet: #@a Print Path only
        print(fpath)
      vprint(df,2)
      updated_povs.append(pov)
  
  if not view_output_path_only: pds.disconnect()  #@a Disconnected
  return updated_povs

def getPH(instrument:str,timeframe:str,quote_count:int=-1,start=None,end=None,with_index=True,quiet=True,compressed=False,tlid_range=None,use_full=False,default_quote_count = 335,default_add_quote_count = 89,verbose_level=0,view_output_path_only=False):
  # Logics migrated from cli
  pov_full_M1 = int(os.getenv("pov_full_M1", "1000"))
  if view_output_path_only:
    return _make_output_fullpath(instrument, timeframe, use_full, tlid_range, compressed, quiet),None
  
  if use_full:# and quotes_count == -1:
    quote_count_fixed = int(
        jgtpov.calculate_quote_counts_tf(pov_full_M1)[timeframe] #@STCIssue FUTUR UPGRADE - READ FULL, CALC Required Quote Count and retrieve just what we need (or aren't they contained in the History Database ??)
    )  # We will download a lot of data relative to each timeframe
    vprint("   Full mode...setting quote_counts:" + str(quote_count_fixed) + f"({timeframe})/" + str(pov_full_M1) + " (M1)",1)  
  else:
    quote_count_fixed = quote_count #if quote_count > 0 else default_quote_count
  
  start_date, end_date = (
                        jgtos.tlid_range_to_start_end_datetime(tlid_range)
                    ) if tlid_range else (None, None)
  try:
    fpath, df = pds.getPH2file(
                        instrument,
                        timeframe,
                        quote_count_fixed,
                        start_date,
                        end_date,
                        with_index,
                        quiet,
                        compressed=compressed,
                        use_full=use_full,
                    )
  except Exception as e:
    print("Exception in svc::getPH " + str(e))
    vprint("INFO::Running ALT command...",1)
    ran_alt_ok,fpath = _run_get_ph_using_alt_command(instrument,timeframe,use_full,tlid_range,compressed,quiet)
    if not ran_alt_ok:
      raise Exception("Failed to run ALT command")
    else:
      df = pd.read_csv(fpath, index_col=0, parse_dates=True)
    
  
  return fpath,df
  #return pds.getPH_to_filestore(instrument,timeframe,quote_count,start,end,with_index,quiet,compressed,tlid_range,use_full=use_full,default_quote_count=default_quote_count,default_add_quote_count=default_add_quote_count)




            

def _run_get_ph_using_alt_command(instrument, 
                        timeframe, 
                        use_full, 
                        tlid_range, 
                        compressed, 
                        quiet,
                        fxcli2console="fxcli2console",
                        run_alt_env_var = "RUN_ALT"):
    ran_ok=False
    # Read RUN_ALT var so we might turn it off
    
    run_alt = os.getenv(run_alt_env_var, 1)  # DEFAULT WE RUN IT
    to_run_cmd = f"{fxcli2console} -i {instrument} -t {timeframe}"
    fpath = _make_output_fullpath(
                                instrument,
                                timeframe,
                                use_full,
                                tlid_range,
                                compressed,
                                quiet,
                            )
    ran_ok = _run_command(to_run_cmd, fpath) if run_alt == 1 or run_alt == "1" else vprint("NOT RUnning ALT")
    return ran_ok,fpath


def _make_output_fullpath(instrument, timeframe, use_full, tlid_range, compress, quiet):
    return pds.create_filestore_path(
        instrument,
        timeframe,
        quiet,
        compress,
        tlid_range,
        output_path=None,
        nsdir="pds",
        use_full=use_full,
    )


def _run_command(command_to_run, output_file):
    vprint("Running ALT command...")
    vprint(command_to_run + " > " + output_file,2)
    with open(output_file, "w") as f:
        try:
            subprocess.run(command_to_run, stdout=f, shell=True)
            print("Ran ALT command ok.")
            return True
        except Exception as e:
            print("Exception details: " + str(e))
            print("Error running ALT command")
            return False



def print_quiet(quiet, content):
    if not quiet:
        print(content)

def vprint(content,level=1):
    global _verbose_level
    if level <= _verbose_level:
        print(content)




debugging=False


import datetime 
import pandas as pd
import os


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import JGTPDHelper as jpd
import jgtfxc as jfx
from JGTConfig import local_fn_compression,get_pov_local_data_filename
from JGTPDHelper import *
from jgtfxc import *

from jgtutils import jgtos
from jgtutils.jgtos import create_filestore_path,mk_fn
import iprops

from jgtutils import jgtconstants as c






renameColumns=True
addOhlc=True
stayConnected=False

def stayConnectedSetter(_v,json_config_str=None):
  global stayConnected
  stayConnected=_v
  jfx.stayConnected=_v
  jfx.connect()
  
cleanseOriginalColumns=True
useLocal=False
con=None






def pds_add_ohlc_stc_columns(dfsrc):
  if not 'Open' in dfsrc.columns:
    dfsrc['Open'] = dfsrc[['BidOpen', 'AskOpen']].mean(axis=1)
    dfsrc['High'] = dfsrc[['BidHigh', 'AskHigh']].mean(axis=1)
    dfsrc['Low'] = dfsrc[['BidLow', 'AskLow']].mean(axis=1)
    dfsrc['Close'] = dfsrc[['BidClose', 'AskClose']].mean(axis=1)
    #Median
    dfsrc['Median']= ((dfsrc['High'] + dfsrc['Low']) / 2)
    return dfsrc


def _cleanse_original_columns(dfsrc,quiet=True):
  dfsrc=jpd.pds_cleanse_original_columns(dfsrc,quiet)
  return dfsrc


def getSubscribed():
  print("REQUIRE UPGRADE FOR THIS FUNCTION (fxcmpy DEPRECRATED)")
  print("--------------------------------------")
  return "REQUIRE UPGRADE FOR THIS FUNCTION (fxcmpy DEPRECRATED)"
  #return jfx.con.get_instruments_for_candles()

def connect(quiet=True,json_config_str=None):  
  return jfx.connect(quiet,json_config_str)

def disconnect(quiet=True):
  return jfx.disconnect(quiet)

def tryConnect():
  try:
    con=connect()
  except ConnectionError:
    print("Connection error")

def status(quiet=True):
  return jfx.status(quiet)

def getPH_from_local1(instrument,timeframe):
  srcpath=get_pov_local_data_filename(instrument,timeframe)
  df=pd.read_csv(srcpath,compression=local_fn_compression,index_col='Date')
  return df




def getPH_from_filestore(instrument,timeframe,quiet=True, compressed=False,with_index=True,tlid_range=None,output_path=None):
  """
  Retrieves OHLC data for a given instrument and timeframe from the filestore.

  Args:
    instrument (str): The instrument symbol.
    timeframe (str): The timeframe of the OHLC data.
    quiet (bool, optional): Whether to suppress print statements. Defaults to True.
    compressed (bool, optional): Whether the data is compressed. Defaults to False.
    with_index (bool, optional): Whether to include the index in the returned DataFrame. Defaults to True.
    tlid_range (str, optional): Select a range on disk or return None if unavailable
    output_path (str, optional): Select a path on disk or return None if unavailable

  Returns:
    pandas.DataFrame: The OHLC data for the given instrument and timeframe.
  """  
  srcpath = create_filestore_path(instrument, timeframe,quiet, compressed,tlid_range,output_path)  
  
  print_quiet(quiet,srcpath)
  
  df = read_ohlc_df_from_file(srcpath,quiet,compressed,with_index)
  
  return df




def read_ohlc_df_from_file(srcpath, quiet=True, compressed=False,with_index=True):
  """
  Reads an OHLC (Open-High-Low-Close) +Date as DataFrame index from a CSV file.

  Args:
    srcpath (str): The path to the CSV file.
    quiet (bool, optional): Whether to print progress messages. Defaults to True.
    compressed (bool, optional): Whether the CSV file is compressed. Defaults to False.

  Returns:
    pandas.DataFrame: The OHLC DataFrame.
  """
  try:
    if compressed:
      print_quiet(quiet, "Reading compressed: " + srcpath + " ")
      df = pd.read_csv(srcpath, compression=local_fn_compression)
    else:
      print_quiet(quiet, "Reading uncompressed csv file: " + srcpath)
      df = pd.read_csv(srcpath)
  except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    df = None
  
  if with_index:
    if 'Date' in df.columns:
      df.set_index('Date', inplace=True)
    else:
      raise ValueError("Column 'Date' is not present in the DataFrame")

  return df


def getPH_to_filestore(instrument, timeframe, quote_count=335, start=None, end=None, with_index=True, quiet=True, compressed=False,tlid_range=None):
  """
  Saves the OHLC data for a given instrument and timeframe to a CSV file.

  Args:
  - instrument (str): The instrument symbol (e.g. 'AAPL')
  - timeframe (str): The timeframe for the data (e.g. '1D' for daily, '1H' for hourly)
  - quote_count (int): The number of quotes to retrieve (default: 335)
  - start (str): The start date for the data (default: None)
  - end (str): The end date for the data (default: None)
  - with_index (bool): Whether to include the index in the CSV file (default: True)
  - quiet (bool): Whether to suppress console output (default: True)
  - compressed (bool): Whether to compress the CSV file using gzip (default: False)
  - tlid_range (str): The tlid range to retrieve (default: None)

  Returns:
  - str: The file path where the CSV file was saved.
  """
  
  df=getPH(instrument,timeframe,quote_count,start,end,False,quiet,tlid_range)
  #print("-----------------getPH------------------->>>>")
  #print(df)
  # print("-----------------getPH-------------------<<<<<<")
  # Define the file path based on the environment variable or local path
  if df is not None:
      fpath = write_df_to_filestore(df, instrument, timeframe, compressed,quiet,tlid_range)
      return fpath,df
  else:
      print("No data from getPH from getPH_to_filestore")
      raise ValueError("No data from getPH from getPH_to_filestore")
  #return "",None

def write_df_to_filestore(df, instrument, timeframe, compressed=False, quiet=True,tlid_range=None):
  try:
    fpath =  create_filestore_path(instrument, timeframe,quiet, compressed,tlid_range)

    try:
      dir_name = os.path.dirname(fpath)
      
      # Check if the directory exists
      if not os.path.exists(dir_name):
        # Try to create the directory
        os.makedirs(dir_name)
      
      # Check if the directory is writable
      if not os.access(dir_name, os.W_OK):
        raise PermissionError("Cannot write to the directory")
    except Exception as e:
      print(f"Failed to access or create directory: {e}")
      raise
    if compressed:
      df.to_csv(fpath, compression=local_fn_compression)
    else:
      df.to_csv(fpath)
    
    return fpath
  except Exception as e:
    print(f"Exception: {e}")
    print(f"Exception details: {str(e)}")




  



def getPH2file(instrument:str,timeframe:str,quote_count:int=335,start=None,end=None,with_index=True,quiet=True,compressed=False,tlid_range=None):
  return getPH_to_filestore(instrument,timeframe,quote_count,start,end,with_index,quiet,compressed,tlid_range)


#getPH(instrument,timeframe,quote_count,start,end,False,quiet,tlid_range)
def getPH(instrument:str,timeframe:str,quote_count:int=-1,start=None,end=None,with_index=True,quiet=True,tlid_range=None):
  """Get Price History from Broker

  Args:
      instrument (str): symbal
      timeframe (str): TF
      quote_count (int, optional): nb bar to retrieve. Defaults to -1.
      start (str, optional): start DateTime. Defaults to None.
      end (str, optional): end DateTime range. Defaults to None.
      with_index (bool, optional): Return DataFrame with Index. Defaults to True.
      quiet  (bool, optional): stay calm ;)
      compressed (bool, optional): Whether to compress the CSV file using gzip (default: False)
      tlid_range (str): The tlid range to retrieve (default: None)

  Returns:
      pandas.DataFrame: DF with price histories
  """
  #print("-----------------getPH------------------->>>>")
  #print(instrument,timeframe,quote_count,start,end,with_index,startquiet,tlid_range)
  if quote_count == -1:
    quote_count = 335
  df = pd.DataFrame()
  if not useLocal:
    con=connect(quiet=quiet)

    try:
      if tlid_range is not None:
        # start,end = jgtos.tlid_range_to_jgtfxcon_start_end_str(tlid_range)
        start,end = jgtos.tlid_range_to_start_end_datetime(tlid_range)
        #print("start: " + str(start) + " end: " + str(end))
        p=jfx.get_price_history(instrument, timeframe, start, end,quiet=quiet) #@STCIssue NOT WORKING
      else:
        #print(end)
        p=jfx.get_price_history(instrument, timeframe, None, end, quote_count+89,quiet=quiet) #@State WORKS
        
    except:
      try:
        disconnect()
        connect(quiet=quiet)
        
        if tlid_range is not None:
          start,end = jgtos.tlid_range_to_jgtfxcon_start_end_str(tlid_range)
          p=jfx.get_price_history(instrument, timeframe, start, end,quiet=quiet)
        else:
          p=jfx.get_price_history(instrument, timeframe, None, end, quote_count+89,quiet=quiet)
      except Exception as e:
        #print("An error occurred: ", e)
        #print("bahhhhhhhhhhhhhhhhhhhhhhh  REINITIALIZATION of the PDS todo")
        raise   e

    if p is None:
      raise ValueError("No data from get_price_history")
    
    #print("--------------DEBUG PDS------------")
    #print(p)

    df=pd.DataFrame(p,columns=['Date','BidOpen','BidHigh','BidLow','BidClose','AskOpen','AskHigh','AskLow','AskClose','Volume'])

    if not stayConnected:
      con=disconnect(quiet=quiet)
    if renameColumns:
      df=df.rename(columns={'bidopen': 'BidOpen', 'bidhigh': 'BidHigh','bidclose':'BidClose','bidlow':'BidLow','askopen': 'AskOpen', 'askhigh': 'AskHigh','askclose':'AskClose','asklow':'AskLow','tickqty':'Volume','date':'Date'})
      df= df.astype({'Volume':int})
    if with_index:
      df.index.rename('Date',inplace=True)
  else:
    #Read from local
    
    #@STCIssue When we read from filestore, the Date Columnt is ok
    df =getPH_from_filestore(instrument,timeframe,tlid_range=tlid_range) #@STCIssue add start and end and index name should be already set
    if with_index:
      df.index.rename('Date',inplace=True)
      
    if start != None:
      mask = (df['Date'] > end) & (df['Date'] <= start)
      df = df.loc[mask]

  if addOhlc and renameColumns:
    df=pds_add_ohlc_stc_columns(df)
  if cleanseOriginalColumns:
    df=_cleanse_original_columns(df,debugging)
  # Set 'Date' column as the index
  df.set_index('Date', inplace=True)
  return df



def getPresentBarAsList(dfsrc):
  _paf =dfsrc.iloc[-1:]
  _pa = _paf.to_dict(orient='list')
  _dtctx=str(_paf.index.values[0])
  _pa['Date'] = _dtctx
  return _pa

def getLastCompletedBarAsList(dfsrc):
  _paf =dfsrc.iloc[-2:-1]
  _pa = _paf.to_dict(orient='list')
  _dtctx=str(_paf.index.values[0])
  _pa['Date'] = _dtctx
  return _pa

  


def print_quiet(quiet,content):
    if not quiet:
        print(content)
        
        
class PDSRangeNotAvailableException(Exception):
    pass



def get_instrument_properties(instrument, quiet=False,from_file=False):
  if not from_file:
    return jfx.get_instrument_properties(instrument, quiet)
  else:
    
    # # Define the path to the directory
    home_dir = os.path.expanduser("~")
    dir_path = os.path.join(home_dir, '.jgt', 'iprops')
    instrument_properties = {}
    instrument_filename = instrument.replace('/', '-')
    #     # Read the instrument properties from the file
    iprop_dir_path = os.path.join(dir_path, f'{instrument_filename}.json')
    with open(iprop_dir_path, 'r') as f:
      instrument_properties = json.load(f)
    return instrument_properties


# Might move to JGTTDS later
def get_price_plus_minus_ticks(instrument, ticks_multiplier, context_price, direction_side):
  """
  Gets the price value plus or minus a defined number of ticks.

  Args:
  instrument: The instrument to trade.
  ticks_multiplier: The number of ticks to add or subtract.
  context_price: The current price of the instrument.
  direction_side: The direction side to use ('S' for minus, 'B' for plus).

  Returns:
  The price value plus or minus the defined number of ticks.
  """
  instrument_properties = get_instrument_properties(instrument)
  tick_size = instrument_properties.pipsize * ticks_multiplier
  if direction_side == 'S':
    price_minus_ticks = context_price - (ticks_multiplier * tick_size)
    return price_minus_ticks
  elif direction_side == 'B':
    price_plus_ticks = context_price + (ticks_multiplier * tick_size)
    return price_plus_ticks
  else:
    raise ValueError("Invalid direction side. Must be 'S' or 'B'.")



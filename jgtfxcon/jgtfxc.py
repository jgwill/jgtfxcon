# jgtfxc.py

import os
import platform
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json
#import datetime
from datetime import datetime,timezone
import pandas as pd
import iprops

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="importlib._bootstrap")
    # your code here

from jgtutils.jgtcommon import readconfig
from jgtfxcommon import get_connection_status,get_connection_status
import jgtfxcommon

import jgtflags
from jgtutils import jgtconstants as c

# origin_work_dir = os.getcwd()
# here = os.path.abspath(os.path.dirname(__file__))
# print("-----------------------------")
# print(here)
# print("-----------------------------")

# path_forexconnect = os.path.join(here, "forexconnect")

# if platform.system() == 'Windows':
#     path_forexconnect = os.path.join(here, 'lib', 'windows', 'mylib.dll')
# elif platform.system() == 'Linux':
#     path_forexconnect = os.path.join(here, 'lib', 'linux', 'mylib.so')
# else:
#     raise RuntimeError('Unsupported platform')


# os.chdir(path_forexconnect)

# from forexconnect import ForexConnect, fxcorepy
if platform.system() == 'Windows':
    from forexconnect import ForexConnect, fxcorepy
else: 
    if platform.system() == 'Linux':
        try:
            # Try to import ForexConnect and fxcorepy from jgtfxcon.forexconnect
            from forexconnect import ForexConnect, fxcorepy
        except ModuleNotFoundError:
            # If that fails, try to import them directly
            try:
                from .forexconnect import ForexConnect, fxcorepy
            except ModuleNotFoundError:
                # If that also fails, print an error message
                print("Could not import ForexConnect or fxcorepy. Please ensure the modules are installed and available.")



# os.chdir(origin_work_dir)   

#@STCGoal Future use
#import forexconnect as fxcon
# fxcon.ForexConnect.create_order_request
# fxcon.ForexConnect.create_request
# fxcon.ForexConnect.get_table
# fxcon.ForexConnect.get_timeframe
# fxcon.ForexConnect.get_timeframe

# from . import common_samples as jgtfxcommon


fx=None
quotes_count=None
stayConnected=False
session=None
#session_status=None
#def get_session_status():
    #return get_connection_status()

def login_forexconnect(user_id, password, url, connection, quiet=False):
    global session,fx    
    jgtfxcommon.quiet=quiet
    if fx is not None:
        try:
            fx.logout()
        except:
            pass
    fx = ForexConnect()
    try:
        fx.login(user_id=user_id,password=password,url=url,connection=connection, pin="", session_id="", session_status_callback=jgtfxcommon.session_status_changed)
        #session_status= jgtfxcommon.get_connection_status()
    except Exception as e:
        jgtfxcommon.print_exception(e)
        print("------bahhhhhhhhhhhh----------")
    return fx
_config=None
#@STCIssue Matching our original connect
def connect(quiet=True,json_config_str=None):
    global fx,quotes_count,_config
    
    if fx is not None or get_connection_status()== "CONNECTED":
        #if not quiet:
        #    print("Already connected")
        return
    
    if _config is None:
        _config=readconfig(json_config_str)

    str_user_id = _config['user_id']
    str_password = _config['password']
    str_url = _config['url']
    str_connection = _config['connection']
    quotes_count = _config['quotes_count']
    

    fx = login_forexconnect(str_user_id, str_password, str_url, str_connection,quiet=quiet)
    
    return fx


def logout_forexconnect(fx,quiet=False):
    try:
        if fx is not None:
            fx.logout()
        fx=None
        #@STCIssue on How we deal with status
        #session_status=get_connection_status()
        #session_status="DISCONNECTED"
        return True
    except Exception as e:
        jgtfxcommon.print_exception(e)
        fx=None
        return False

def disconnect(quiet=True):
    global fx
    if fx is None:
        print_quiet(quiet,"Not connected")
        return True
    return logout_forexconnect(fx,quiet)


def status(quiet=True):
    return jgtfxcommon.get_session_status()
    # if session is None:
    #     print_quiet(quiet,"UNKNOWN STATUS...")
    #     return False
    # else :
    #     print("---------AO2GSessionStatus-----------")
    #     print(fxcorepy.AO2GSessionStatus)
    #     print(session.AO2GSessionStatus)
    #     print("--------------------")
    #     if session.getStatus() == fxcorepy.AO2GSessionStatus.CONNECTED:
    #         print_quiet(quiet,"CONNECTED...")
    #         return True
    #     if session.getStatus() == fxcorepy.AO2GSessionStatus.DISCONECTED:
    #         print_quiet(quiet,"DISCONNECTED...")
    #         return False
    # print_quiet(quiet,"UNKNOWN STATUS...")
    # return False
        
def status1(quiet=True):
    global fx
    if fx is None:
        print_quiet(quiet,"STATUS : Not Connected")
        return False
    print_quiet(quiet,"STATUS : Connected")
    return True

def print_quiet(quiet,content):
    if not quiet:
        print(content)



def get_price_history(instrument: str, timeframe: str, datefrom: datetime=None, dateto:datetime=None,quotes_count_spec:int=None,quiet: bool=True):
    global quotes_count,fx
    if quotes_count_spec is None:
        quotes_count_spec=quotes_count
    
    data=None
    connect(quiet=quiet)
    # if home_dir/.jgt/iprops make it and run a save of this instrument properties
    iprop=get_instrument_properties(instrument,quiet)
    try:
        print_quiet(quiet,"Getting PH: " + instrument + " " + timeframe)
  
        #print_quiet(quiet,"   (not Parsed) from : " + str(datefrom) + ", to:" + str(dateto))
        #print_quiet(quiet,"-------------------------------------------------------")

        # if datefrom is not None:
        #     date_from_parsed = parse_date(datefrom)
        # else:
        #     date_from_parsed=None
        
        if dateto is None:
            dateto = datetime.now(timezone.utc)
        # else:
        #     date_to_parsed = parse_date(dateto)
        
        #quiet=False
        if not quiet:
            print(" Date from  : " + str(datefrom))
            print(" Date to    : " + str(dateto))
            print(" Quote count: " + str(quotes_count_spec))
            
        if fx is None:
            print("FX IS NONE")
        if datefrom is not None:
            history = fx.get_history(instrument, timeframe, datefrom, dateto)
        else:
            if dateto is not None:
                history = fx.get_history(instrument, timeframe, None, dateto, quotes_count_spec)
            else:
                history = fx.get_history(instrument, timeframe, None, None, quotes_count_spec)

        current_unit, _ = ForexConnect.parse_timeframe(timeframe)

        if current_unit == fxcorepy.O2GTimeFrameUnit.TICK:
            data = pd.DataFrame(history, columns=[c.date_column_name, 'Bid', 'Ask'])
        else:
            data = pd.DataFrame(history, columns=[c.date_column_name,c.bidopen_column_name,c.bidhigh_column_name,c.bidlow_column_name,c.bidclose_column_name,c.askopen_column_name,c.askhigh_column_name,c.asklow_column_name,c.askclose_column_name,c.volume_column_name])

        return data

    finally:
        if not stayConnected:
            disconnect()
        #else:
        #    print("---we stay connected---")
        #logout_forexconnect(fx)
    return data



def get_price_history_printed(instrument, timeframe, datefrom=None, dateto=None):
    data = get_price_history(instrument, timeframe, datefrom, dateto)

    if data is not None:
        if 'Ask' in data.columns:
            print("Date, Bid, Ask")
        else:
            print("Date, BidOpen, BidHigh, BidLow, BidClose, Volume")

        for index, row in data.iterrows():
            values = row.values.tolist()
            print(",".join(str(value) for value in values))


# Example usage
#get_price_history_printed(instrument='EUR/USD', timeframe='m1')

#fx
def getAccount():
    # account = fx.getAccount()
    # print(account)
    # return account
    print("Not implemented yet")

def getSubscribedSymbols():
    if fx is None:
        connect()
    # symbols = fx.getSubscribedSymbols()
    # print(symbols)
    #return symbols
    print("Not implemented yet")



def parse_date(date_str) -> datetime:
    if date_str is not None: 
        date_format = '%m.%d.%Y %H:%M:%S' # was bugged '%d.%m.%Y %H:%M'
        for fmt in ('%m.%d.%Y %H:%M:%S', '%m.%d.%Y %H:%M','%m.%d.%Y','%Y%m%d%H%M','%y%m%d%H%M','%Y-%m-%d %H:%M'):
            try:
                #print(date_str)
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')
    

def get_instrument_properties(instrument, quiet=False):
    instrument_properties = {}
    try:
        instrument_properties = iprops.get_iprop(instrument)
        instrument_properties["pipsize"] = instrument_properties["pips"]
    except Exception as e:
        print("An error occurred: ", e)
     
    return instrument_properties
    

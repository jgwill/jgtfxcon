import os
from io import StringIO
import pandas as pd
#from . import jgtfxcon as jfx
from jgtfxcon import JGTPDS as pds
#from jgtfxcon.jgtfxc import get_instrument_properties

all_instrument_csv = StringIO("""Filename,Name,FXCM,IBK
AUD-CAD,Australian Dollar/Canadian Dollar,AUD/CAD,AUDCAD
AUD-CHF,Australian Dollar/Swiss Franc,AUD/CHF,AUDCHF
AUD-JPY,Australian Dollar/Japanese Yen,AUD/JPY,AUDJPY
AUD-NZD,Australian Dollar/New Zealand Dollar,AUD/NZD,AUDNZD
AUD-USD,Australian Dollar/US Dollar,AUD/USD,AUDUSD
CAD-CHF,Canadian Dollar/Swiss Franc,CAD/CHF,CADCHF
CAD-JPY,Canadian Dollar/Japanese Yen,CAD/JPY,CADJPY
CHF-JPY,Swiss Franc/Japanese Yen,CHF/JPY,CHFJPY
EUR-AUD,Euro/Australian Dollar,EUR/AUD,EURAUD
EUR-CAD,Euro/Canadian Dollar,EUR/CAD,EURCAD
EUR-CHF,Euro/Swiss Franc,EUR/CHF,EURCHF
EUR-GBP,Euro/British Pound,EUR/GBP,EURGBP
EUR-JPY,Euro/Japanese Yen,EUR/JPY,EURJPY
EUR-NOK,Euro/Norwegian Krone,EUR/NOK,EURNOK
EUR-NZD,Euro/New Zealand Dollar,EUR/NZD,EURNZD
EUR-SEK,Euro/Swedish Krona,EUR/SEK,EURSEK
EUR-TRY,Euro/Turkish Lira,EUR/TRY,EURTRY
EUR-USD,Euro/US Dollar,EUR/USD,EURUSD
GBP-AUD,British Pound/Australian Dollar,GBP/AUD,GBPAUD
GBP-CAD,British Pound/Canadian Dollar,GBP/CAD,GBPCAD
GBP-CHF,British Pound/Swiss Franc,GBP/CHF,GBPCHF
GBP-JPY,British Pound/Japanese Yen,GBP/JPY,GBPJPY
GBP-NZD,British Pound/New Zealand Dollar,GBP/NZD,GBPNZD
GBP-USD,British Pound/US Dollar,GBP/USD,GBPUSD
NZD-CAD,New Zealand Dollar/Canadian Dollar,NZD/CAD,NZDCAD
NZD-CHF,New Zealand Dollar/Swiss Franc,NZD/CHF,NZDCHF
NZD-JPY,New Zealand Dollar/Japanese Yen,NZD/JPY,NZDJPY
NZD-USD,New Zealand Dollar/US Dollar,NZD/USD,NZDUSD
TRY-JPY,Turkish Lira/Japanese Yen,TRY/JPY,TRYJPY
USD-CAD,US Dollar/Canadian Dollar,USD/CAD,USDCAD
USD-CHF,US Dollar/Swiss Franc,USD/CHF,USDCHF
USD-CNH,US Dollar/Chinese Yuan,USD/CNH,USDCNH
USD-JPY,US Dollar/Japanese Yen,USD/JPY,USDJPY
USD-MXN,US Dollar/Mexican Peso,USD/MXN,USDMXN
USD-NOK,US Dollar/Norwegian Krone,USD/NOK,USDNOK
USD-SEK,US Dollar/Swedish Krona,USD/SEK,USDSEK
USD-TRY,US Dollar/Turkish Lira,USD/TRY,USDTRY
USD-ZAR,US Dollar/South African Rand,USD/ZAR,USDZAR
ZAR-JPY,South African Rand/Japanese Yen,ZAR/JPY,ZARJPY
""")

all_indices_csv = StringIO("""Name,FXCM,IBK
Australia 200 Index,AUS200,AUS200
China A50 Index,CHN50,CHN50
Spain 35 Index,ESP35,ESP35
Euro Stoxx 50 Index,EUSTX50,ESTX50
France 40 Index,FRA40,FRA40
Germany 30 Index,GER30,DAX30
Hong Kong 33 Index,HKG33,HSI
Japan 225 Index,JPN225,JP225
NASDAQ 100 Index,NAS100,NDX
S&P 500 Index,SPX500,SPX
UK 100 Index,UK100,FTSE100
US 2000 Index,US2000,RUT
Dow Jones Industrial Average,US30,DJI
""")

all_commodities_csv = StringIO("""Name,FXCM,IBK
Copper,COPPER,COPPER
Corn,CORNF,CORNF
Natural Gas,NGAS,NGAS
Soybeans,SOYF,SOYF
UK Oil,UKOIL,UKOIL
US Oil,USOIL,USOIL
Wheat,WHEATF,WHEATF
Silver,XAG/USD,XAG/USD
Gold,XAU/USD,XAU/USD
""")

import json

def write_json_file(path, data):
  with open(path, 'w') as f:
    json.dump(data, f)

commodities = pd.read_csv( all_commodities_csv)
print(commodities['FXCM'])
forexes = pd.read_csv(all_instrument_csv)

indices = pd.read_csv(all_indices_csv)

def process_fxcm(df,fn_all="iprop-forex.json"):
  #ind={}
  for fxcm_value in df['FXCM']:
    iprop=pds.get_instrument_properties(fxcm_value)
    #ind[fxcm_value]=iprop
  #write to file the fn_all
  # iprop_fpath = os.path.join(".",fn_all)
  
  # write_json_file(iprop_fpath,ind)
  # print("Wrote to file: ",iprop_fpath)


pds.stayConnectedSetter(True)


iprop_fnname = "iprop-commodities.json"
process_fxcm(commodities,iprop_fnname)
iprop_fnname = "iprop-forex.json"
process_fxcm(forexes,iprop_fnname)
iprop_fnname = "iprop-indices.json"
process_fxcm(indices,iprop_fnname)

pds.disconnect()




# def read_json_file(filename):
#   # Get the directory of the current script
#   script_dir = os.path.dirname(os.path.realpath(__file__))

#   # Construct the full file path
#   file_path = os.path.join(script_dir, filename)

#   # Read the JSON file
#   with open(file_path, 'r') as f:
#     data = json.load(f)

#   return data

# # Use the function
# data = read_json_file('iprop.json')
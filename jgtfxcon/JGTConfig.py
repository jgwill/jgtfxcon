import os
#import jgtdotenv
from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()  # take environment variables from .env.
#env=load_dotenv(os.getenv(os.getcwd()))
env = dotenv_values(".env")




# print(FXCM_TOKEN_REST_API_DEMO)

local_fn_compression='gzip'


def get_pov_local_data_filename(instrument,timeframe,local_data_dir='./data',local_fn_suffix='.full.csv.gz'):
  print("-------#@STCIssue FIXING REQUIRED-----------------")
  tf=timeframe
  if tf=="m1":
    tf="mi1"
  return local_data_dir + "/"+ instrument.replace("/","-") + "_" + tf + local_fn_suffix

pysroot=os.getenv('pysroot')
#pysroot='/w/o/pys/'
CDS_URL_BASE=os.getenv('CDS_URL_BASE')
phurlbase=CDS_URL_BASE
#phurlbase='https://ai.guillaumeisabelle.com/sds/datasets/cds/' #todo rename as pds, cds are going to be indicators/cds data

DROPBOX_ETC_PATH= '/w/etc/'


if os.getenv('usereal') == 'True' :
  #@STCIssue FIXING REQUIRED
  print('TRADING REAL ACTIVATED')

def setreal():
  #@STCIssue FIXING REQUIRED
  print('TRADING REAL ACTIVATED')
  

def setdemo():
  #@STCIssue FIXING REQUIRED
  print('TRADING DEMO/PAPER ACTIVATED')
  


# %%
contextInstruments=['AUD/CAD',
 'AUD/JPY',
 'AUD/USD',
 'CAD/CHF',
 'CAD/JPY',
 'EUR/CAD',
 'EUR/USD',
 'GBP/CAD',
 'GBP/USD',
 'NAS100',
 'SPX500',
 'NZD/CAD',
 'NZD/USD',
 'USD/CAD'
 ]

contextTimeframes=['m1','m5','m15']
# contextTimeframes=['m1','m5','m15','H1','H4','D1','W1','M1']



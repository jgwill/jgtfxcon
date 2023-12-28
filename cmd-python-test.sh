
python -i -c "import pandas as pd; import numpy as np;import jgtfxcon.JGTPDS as pds;instrument='EUR/USD';timeframe='D1';print('variable instrument,timeframe are defined.  imported  pds from jgtfxcon');import jgtfxcon;i=instrument;t=timeframe;import jgtfxcon.jgtfxc as jfx;df=pd.read_csv('../data/pds/EUR-USD_H4.csv')"

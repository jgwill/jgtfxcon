
#%%

from jgtutils import jgtcommon as jgtcommon, jgtos as jgtos





# %%
jgtcommon.is_market_open()
# %%

tr_data_path=jgtos.get_data_path("tr")
# %%
tr_data_path


# %%
# How ho we save the transactions data?
from pto_jgtfxtransact__analyze_demo_trades_orders_take_2 import analyze_trades_orders_relationship, load_transactions_json_table
data=load_transactions_json_table("demo_fxtransact.json")

#jgtos.create_filestore_path(nsdir="tr",instrument=)
# %%
data
# %%
analyzed=analyze_trades_orders_relationship("demo_fxtransact.json")
# %%
analyzed
# %%

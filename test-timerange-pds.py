# That we get a timerange and it is stored differently
#  EUR-USD_H1_2011010000_2101210000.csv
#  $instrument_$timeframe_$start_$end.csv

def mkfn_range_filename(instrument, timeframe, start, end):
    return f"{instrument}_{timeframe}_{start}_{end}.csv"

from jgtutils.FXTransact import FXTrade,FXOrder


def trade_row_to_trade_object(trade_row)->FXTrade:
    string = _trade_row_to_string(trade_row)
    return FXTrade.from_string(string)

def _trade_row_to_string(trade_row)->str:
    string=""
    for column in trade_row.columns:
        string += column.id + "=" + str(trade_row[column.id]) + "; "
    return string
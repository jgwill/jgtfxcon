

"""
SAMPLE OUTPUT:
trade_id=68773225; account_id=465876; account_name=00465876; account_kind=32; offer_id=91; amount=2000; buy_sell=B; open_rate=0.82492; open_time=2024-08-07 21:10:13; open_quote_id=Force Execute; open_order_id=169974106; open_order_req_id=U10D2_1EBF7C97ACBA92E2E063E12B3C0AB11E_08072024183956490826_J0I9-46123; open_order_request_txt=31ABA84B-8CC1-483A-A3B5-1EE7C2566A16; commission=0.14; rollover_interest=0.0; trade_id_origin=; used_margin=5.8; value_date=; parties=; dividends=0.0; pl=-8.500000000000174; gross_pl=-1.24; close=0.82407; stop=0.0; limit=0.0; stop_order_id=; limit_order_id=; instrument=NZD/CAD; trail_rate=0.0; trail_step=0.0; close_commission=0.14; 
trade_id=68773235; account_id=465876; account_name=00465876; account_kind=32; offer_id=91; amount=3000; buy_sell=B; open_rate=0.82492; open_time=2024-08-07 21:18:48; open_quote_id=Force Execute; open_order_id=169974119; open_order_req_id=U10D2_1EBF7C97ACBA92E2E063E12B3C0AB11E_08072024183956490826_J0I9-47312; open_order_request_txt=9B319ACC-7DB4-4419-BF0F-17E99FBDFD3F; commission=0.21; rollover_interest=0.0; trade_id_origin=; used_margin=8.699999999999998; value_date=; parties=; dividends=0.0; pl=-8.500000000000174; gross_pl=-1.85; close=0.82407; stop=0.82256; limit=0.0; stop_order_id=169974120; limit_order_id=; instrument=NZD/CAD; trail_rate=0.0; trail_step=0.0; close_commission=0.21
trade_id=68773234; account_id=465876; account_name=00465876; account_kind=32; offer_id=91; amount=2000; buy_sell=B; open_rate=0.82493; open_time=2024-08-07 21:18:31; open_quote_id=Force Execute; open_order_id=169974118; open_order_req_id=U10D2_1EBF7C97ACBA92E2E063E12B3C0AB11E_08072024183956490826_J0I9-47265; open_order_request_txt=C2DA4044-DF05-41A3-9CAC-8136CF8EEFD6; commission=0.14; rollover_interest=0.0; trade_id_origin=; used_margin=5.8; value_date=; parties=; dividends=0.0; pl=-8.60000000000083; gross_pl=-1.25; close=0.82407; stop=0.0; limit=0.0; stop_order_id=; limit_order_id=; instrument=NZD/CAD; trail_rate=0.0; trail_step=0.0; close_commission=0.14
"""

import datetime

class FXTrade:
    def __init__(self, trade_id, account_id, account_name, account_kind, offer_id, amount, buy_sell, open_rate, open_time, open_quote_id, open_order_id, open_order_req_id, open_order_request_txt, commission, rollover_interest, trade_id_origin, used_margin, value_date, parties, dividends, pl, gross_pl, close, stop, limit, stop_order_id, limit_order_id, instrument, trail_rate, trail_step, close_commission):
        self.trade_id = trade_id
        self.account_id = account_id
        self.account_name = account_name
        self.account_kind = account_kind
        self.offer_id = offer_id
        self.amount = amount
        self.buy_sell = buy_sell
        self.open_rate = open_rate
        self.open_time = datetime.datetime.strptime(open_time, '%Y-%m-%d %H:%M:%S')
        self.open_quote_id = open_quote_id
        self.open_order_id = open_order_id
        self.open_order_req_id = open_order_req_id
        self.open_order_request_txt = open_order_request_txt
        self.commission = commission
        self.rollover_interest = rollover_interest
        self.trade_id_origin = trade_id_origin
        self.used_margin = used_margin
        self.value_date = value_date
        self.parties = parties
        self.dividends = dividends
        self.pl = pl
        self.gross_pl = gross_pl
        self.close = close
        self.stop = stop
        self.limit = limit
        self.stop_order_id = stop_order_id
        self.limit_order_id = limit_order_id
        self.instrument = instrument
        self.trail_rate = trail_rate
        self.trail_step = trail_step
        self.close_commission = close_commission

    @classmethod
    def from_string(cls, trade_string):
        trade_data = {}
        for item in trade_string.split(';'):
            if '=' in item:
                key, value = item.split('=')
                key = key.strip()
                value = value.strip()
                trade_data[key] = value
        return cls(
            trade_id=int(trade_data.get('trade_id', 0)),
            account_id=int(trade_data.get('account_id', 0)),
            account_name=trade_data.get('account_name', ''),
            account_kind=int(trade_data.get('account_kind', 0)),
            offer_id=int(trade_data.get('offer_id', 0)),
            amount=int(trade_data.get('amount', 0)),
            buy_sell=trade_data.get('buy_sell', ''),
            open_rate=float(trade_data.get('open_rate', 0.0)),
            open_time=trade_data.get('open_time', ''),
            open_quote_id=trade_data.get('open_quote_id', ''),
            open_order_id=trade_data.get('open_order_id', ''),
            open_order_req_id=trade_data.get('open_order_req_id', ''),
            open_order_request_txt=trade_data.get('open_order_request_txt', ''),
            commission=float(trade_data.get('commission', 0.0)),
            rollover_interest=float(trade_data.get('rollover_interest', 0.0)),
            trade_id_origin=trade_data.get('trade_id_origin', ''),
            used_margin=float(trade_data.get('used_margin', 0.0)),
            value_date=trade_data.get('value_date', ''),
            parties=trade_data.get('parties', ''),
            dividends=float(trade_data.get('dividends', 0.0)),
            pl=float(trade_data.get('pl', 0.0)),
            gross_pl=float(trade_data.get('gross_pl', 0.0)),
            close=float(trade_data.get('close', 0.0)),
            stop=float(trade_data.get('stop', 0.0)),
            limit=float(trade_data.get('limit', 0.0)),
            stop_order_id=trade_data.get('stop_order_id', ''),
            limit_order_id=trade_data.get('limit_order_id', ''),
            instrument=trade_data.get('instrument', ''),
            trail_rate=float(trade_data.get('trail_rate', 0.0)),
            trail_step=float(trade_data.get('trail_step', 0.0)),
            close_commission=float(trade_data.get('close_commission', 0.0))
        )

    def __repr__(self):
        return f"Trade(trade_id={self.trade_id}, account_id={self.account_id}, account_name='{self.account_name}', account_kind={self.account_kind}, offer_id={self.offer_id}, amount={self.amount}, buy_sell='{self.buy_sell}', open_rate={self.open_rate}, open_time='{self.open_time}', open_quote_id='{self.open_quote_id}', open_order_id='{self.open_order_id}', open_order_req_id='{self.open_order_req_id}', open_order_request_txt='{self.open_order_request_txt}', commission={self.commission}, rollover_interest={self.rollover_interest}, trade_id_origin='{self.trade_id_origin}', used_margin={self.used_margin}, value_date='{self.value_date}', parties='{self.parties}', dividends={self.dividends}, pl={self.pl}, gross_pl={self.gross_pl}, close={self.close}, stop={self.stop}, limit={self.limit}, stop_order_id='{self.stop_order_id}', limit_order_id='{self.limit_order_id}', instrument='{self.instrument}', trail_rate={self.trail_rate}, trail_step={self.trail_step}, close_commission={self.close_commission})"

# # Example usage
# trade_string = "trade_id=68773235; account_id=465876; account_name=00465876; account_kind=32; offer_id=91; amount=3000; buy_sell=B; open_rate=0.82492; open_time=2024-08-07 21:18:48; open_quote_id=Force Execute; open_order_id=169974119; open_order_req_id=U10D2_1EBF7C97ACBA92E2E063E12B3C0AB11E_08072024183956490826_J0I9-47312; open_order_request_txt=9B319ACC-7DB4-4419-BF0F-17E99FBDFD3F; commission=0.21; rollover_interest=0.0; trade_id_origin=; used_margin=8.699999999999998; value_date=; parties=; dividends=0.0; pl=-8.500000000000174; gross_pl=-1.85; close=0.82407; stop=0.82256; limit=0.0; stop_order_id=169974120; limit_order_id=; instrument=NZD/CAD; trail_rate=0.0; trail_step=0.0; close_commission=0.21"
# trade = FXTrade.from_string(trade_string)
# print(trade)

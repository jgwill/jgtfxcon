
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





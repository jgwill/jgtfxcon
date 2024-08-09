
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




class FXOrder:
    def __init__(self, order_id, request_id, rate, execution_rate, rate_min, rate_max, trade_id, account_id, account_name, offer_id, net_quantity, buy_sell, stage, type, status, status_time, amount, lifetime, at_market, trail_step, trail_rate, time_in_force, account_kind, request_txt, contingent_order_id, contingency_type, primary_id, origin_amount, filled_amount, working_indicator, peg_type, peg_offset, peg_offset_min, peg_offset_max, expire_date, value_date, parties, side, stop, limit, stop_order_id, limit_order_id, type_stop, type_limit, stop_trail_step, stop_trail_rate):
        self.order_id = order_id
        self.request_id = request_id
        self.rate = rate
        self.execution_rate = execution_rate
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.trade_id = trade_id
        self.account_id = account_id
        self.account_name = account_name
        self.offer_id = offer_id
        self.net_quantity = net_quantity
        self.buy_sell = buy_sell
        self.stage = stage
        self.type = type
        self.status = status
        self.status_time = datetime.datetime.strptime(status_time, '%Y-%m-%d %H:%M:%S')
        self.amount = amount
        self.lifetime = lifetime
        self.at_market = at_market
        self.trail_step = trail_step
        self.trail_rate = trail_rate
        self.time_in_force = time_in_force
        self.account_kind = account_kind
        self.request_txt = request_txt
        self.contingent_order_id = contingent_order_id
        self.contingency_type = contingency_type
        self.primary_id = primary_id
        self.origin_amount = origin_amount
        self.filled_amount = filled_amount
        self.working_indicator = working_indicator
        self.peg_type = peg_type
        self.peg_offset = peg_offset
        self.peg_offset_min = peg_offset_min
        self.peg_offset_max = peg_offset_max
        self.expire_date = datetime.datetime.strptime(expire_date, '%Y-%m-%d %H:%M:%S')
        self.value_date = value_date
        self.parties = parties
        self.side = side
        self.stop = stop
        self.limit = limit
        self.stop_order_id = stop_order_id
        self.limit_order_id = limit_order_id
        self.type_stop = type_stop
        self.type_limit = type_limit
        self.stop_trail_step = stop_trail_step
        self.stop_trail_rate = stop_trail_rate

    
    
    @classmethod
    def from_string(cls, order_string):
        order_data = {}
        for item in order_string.split(';'):
            if '=' in item:
                key, value = item.split('=')
                key = key.strip()
                value = value.strip()
                order_data[key] = value
        return cls(
            order_id=int(order_data.get('order_id', 0)),
            request_id=order_data.get('request_id', ''),
            rate=float(order_data.get('rate', 0.0)),
            execution_rate=float(order_data.get('execution_rate', 0.0)),
            rate_min=float(order_data.get('rate_min', 0.0)),
            rate_max=float(order_data.get('rate_max', 0.0)),
            trade_id=int(order_data.get('trade_id', 0)),
            account_id=int(order_data.get('account_id', 0)),
            account_name=order_data.get('account_name', ''),
            offer_id=int(order_data.get('offer_id', 0)),
            net_quantity=order_data.get('net_quantity', 'False') == 'True',
            buy_sell=order_data.get('buy_sell', ''),
            stage=order_data.get('stage', ''),
            type=order_data.get('type', ''),
            status=order_data.get('status', ''),
            status_time=order_data.get('status_time', ''),
            amount=int(order_data.get('amount', 0)),
            lifetime=float(order_data.get('lifetime', 0.0)),
            at_market=float(order_data.get('at_market', 0.0)),
            trail_step=int(order_data.get('trail_step', 0)),
            trail_rate=float(order_data.get('trail_rate', 0.0)),
            time_in_force=order_data.get('time_in_force', ''),
            account_kind=int(order_data.get('account_kind', 0)),
            request_txt=order_data.get('request_txt', ''),
            contingent_order_id=int(order_data.get('contingent_order_id', 0)),
            contingency_type=int(order_data.get('contingency_type', 0)),
            primary_id=order_data.get('primary_id', ''),
            origin_amount=int(order_data.get('origin_amount', 0)),
            filled_amount=int(order_data.get('filled_amount', 0)),
            working_indicator=order_data.get('working_indicator', 'False') == 'True',
            peg_type=order_data.get('peg_type', ''),
            peg_offset=float(order_data.get('peg_offset', 0.0)),
            peg_offset_min=float(order_data.get('peg_offset_min', 0.0)),
            peg_offset_max=float(order_data.get('peg_offset_max', 0.0)),
            expire_date=order_data.get('expire_date', ''),
            value_date=order_data.get('value_date', ''),
            parties=order_data.get('parties', ''),
            side=int(order_data.get('side', 0)),
            stop=float(order_data.get('stop', 0.0)),
            limit=float(order_data.get('limit', 0.0)),
            stop_order_id=order_data.get('stop_order_id', ''),
            limit_order_id=order_data.get('limit_order_id', ''),
            type_stop=int(order_data.get('type_stop', 0)),
            type_limit=int(order_data.get('type_limit', 0)),
            stop_trail_step=int(order_data.get('stop_trail_step', 0)),
            stop_trail_rate=float(order_data.get('stop_trail_rate', 0.0))
        )

    def __repr__(self):
        return f"FXOrder(order_id={self.order_id}, request_id='{self.request_id}', rate={self.rate}, execution_rate={self.execution_rate}, rate_min={self.rate_min}, rate_max={self.rate_max}, trade_id={self.trade_id}, account_id={self.account_id}, account_name='{self.account_name}', offer_id={self.offer_id}, net_quantity={self.net_quantity}, buy_sell='{self.buy_sell}', stage='{self.stage}', type='{self.type}', status='{self.status}', status_time='{self.status_time}', amount={self.amount}, lifetime={self.lifetime}, at_market={self.at_market}, trail_step={self.trail_step}, trail_rate={self.trail_rate}, time_in_force='{self.time_in_force}', account_kind={self.account_kind}, request_txt='{self.request_txt}', contingent_order_id={self.contingent_order_id}, contingency_type={self.contingency_type}, primary_id='{self.primary_id}', origin_amount={self.origin_amount}, filled_amount={self.filled_amount}, working_indicator={self.working_indicator}, peg_type='{self.peg_type}', peg_offset={self.peg_offset}, peg_offset_min={self.peg_offset_min}, peg_offset_max={self.peg_offset_max}, expire_date='{self.expire_date}', value_date='{self.value_date}', parties='{self.parties}', side={self.side}, stop={self.stop}, limit={self.limit}, stop_order_id='{self.stop_order_id}', limit_order_id='{self.limit_order_id}', type_stop={self.type_stop}, type_limit={self.type_limit}, stop_trail_step={self.stop_trail_step}, stop_trail_rate={self.stop_trail_rate})"


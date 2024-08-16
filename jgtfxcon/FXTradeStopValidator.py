

from jgtutils.FXTransact import FXTrade
        
class FXTradeMVStopValidator:
    #We want to validate the stop value for a trade is within the min and max values of our risk management
    def __init__(self, trade:FXTrade, min_stop:float, max_stop:float):
        self.trade = trade
        self.min_stop = min_stop
        self.max_stop = max_stop
        self.stop = trade.stop
        self.is_valid=self.validate_stop()
    
    def validate_stop(self):
        raise NotImplementedError("#@STCGoal Setting Readings of our risk management - Tolerance for Stop Loss Preference probably by instrument and timeframe.")
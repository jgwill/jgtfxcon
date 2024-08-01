# stop_manager.py

from SetStop import change_trade,check_trades

class JGTStopManager:
    def __init__(self):
        self.stop_price = None
        self.instrument = None

    def set_stop(self, price, instrument):
        self.stop_price = price
        self.instrument = instrument
        
        return f"Stop price set to {self.stop_price}"

# Example usage:
# stop_manager = StopManager()
# stop_manager.set_stop(100)
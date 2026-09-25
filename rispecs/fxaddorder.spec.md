# fxaddorder (Entry Order) Specification

> Create Entry Stop Orders on Broker

**Specification Version**: 1.0  
**Module**: `jgtfxcon/jgtfxentryorder.py`  
**CLI Command**: `fxaddorder`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Entry stop orders on the broker with specified entry rate, stop loss, direction, and position size.

**Achievement Indicator**: Running `fxaddorder --demo -i EUR/USD -bs B -rate 1.0950 -stop 1.0900 -lots 1` produces:
- Entry order created on broker
- Order ID returned
- Confirmation with rate and time-in-force

**Value Proposition**: Execute FDB signals by creating entry orders with pre-defined stop loss - the final step in the trading workflow.

---

## Structural Tension

**Current Reality**: FDB signal validated, entry/stop rates calculated, but no broker order exists.

**Desired State**: Entry order placed on broker, waiting for price to trigger.

**Natural Progression**: Parse args → Connect → Create request → Send order → Monitor → Confirm.

---

## CLI Interface

```python
def main():
    """
    JGT FX Create Entry Stop Order CLI.
    
    Arguments:
        --demo: Use demo account (vs real)
        -i, --instrument: Instrument symbol (required)
        -bs: Buy/Sell direction - "B" or "S" (required)
        -rate: Entry rate (required)
        -stop: Stop loss rate (required)
        -lots: Position size in lots (required)
    
    Examples:
        # Create buy entry order (demo)
        fxaddorder --demo -i EUR/USD -bs B -rate 1.0950 -stop 1.0900 -lots 1
        
        # Create sell entry order (demo)
        fxaddorder --demo -i EUR/USD -bs S -rate 1.0850 -stop 1.0900 -lots 2
        
        # Real account order
        fxaddorder -i GBP/USD -bs B -rate 1.2500 -stop 1.2450 -lots 0.5
    """
```

---

## Order Creation Flow

```python
def main():
    """
    Main entry point.
    
    Flow:
        1. Parse arguments
        2. Validate stop level provided
        3. Read broker credentials from config
        4. Connect to ForexConnect
        5. Get account (demo or real)
        6. Get offer for instrument
        7. Calculate amount from lots × base_unit_size
        8. Create ENTRY order request with:
           - OFFER_ID
           - ACCOUNT_ID
           - BUY_SELL
           - RATE (entry)
           - RATE_STOP (stop loss)
           - AMOUNT
        9. Set up OrdersMonitor listener
        10. Send request
        11. Wait for order confirmation
        12. Print order details
        13. Logout
    """
```

---

## OrdersMonitor Class

```python
class OrdersMonitor:
    """Monitor for tracking order creation."""
    
    def __init__(self):
        self.__order_id = None
        self.__orders = {}
        self.__event = Event()
    
    def on_added_order(self, _, __, order_row):
        """
        Callback when order is added.
        
        Stores order in internal dict and signals
        if this is the order we're waiting for.
        """
    
    def wait(self, time: float, order_id: str) -> Optional[OrderRow]:
        """
        Wait for order to appear with timeout.
        
        Returns order_row if found, None if timeout.
        """
    
    def find_order(self, order_id: str) -> Optional[OrderRow]:
        """Find order by ID in tracked orders."""
    
    def reset(self):
        """Clear tracked orders and reset event."""
```

---

## Order Parameters

```python
# Entry order type
entry = fxcorepy.Constants.Orders.ENTRY

# Order request parameters
request = fx.create_order_request(
    order_type=entry,
    OFFER_ID=offer.offer_id,      # Instrument offer
    ACCOUNT_ID=str_account,        # Trading account
    BUY_SELL=str_buy_sell,        # "B" or "S"
    RATE=str_rate,                # Entry price
    RATE_STOP=str_stop,           # Stop loss price
    AMOUNT=amount,                # Position size (units)
)
```

---

## Lot Size Calculation

```python
# Get base unit size for instrument
base_unit_size = trading_settings_provider.get_base_unit_size(
    str_instrument, account
)

# Calculate amount in units
amount = base_unit_size * str_lots

# Example:
# EUR/USD base_unit_size = 10000
# lots = 1
# amount = 10000 (0.1 standard lot)
```

---

## Error Handling

```python
# RequestFailedError handling
try:
    resp = fx.send_request(request)
except Exception as e:
    _type_of_exception = type(e).__name__
    
    if _type_of_exception == "RequestFailedError":
        print("Request failed Error Handling...")
        print("Input Stop value:", str_stop)
        # Often indicates invalid stop level (too close, wrong side)
        exit(1)
```

---

## Output

```
Adding a stop to an entry order with 
entry rate: 1.09500, stop: 1.09000
AccountID='12345678'
The order has been added. OrderID=456789, Type=SE, BuySell=B, Rate=1.09500, TimeInForce=GTC
```

---

## Dependencies

```python
from forexconnect import fxcorepy, ForexConnect, Common
from jgtutils import jgtconstants, jgtos, jgtcommon, jgtpov
import common_samples
from time import sleep
from threading import Event
```

---

## Quality Criteria

✅ **Entry + Stop**: Combined order with stop loss  
✅ **Lot Size Handling**: Proper unit conversion  
✅ **Demo/Real**: Account type selection  
✅ **Async Monitoring**: Wait for order confirmation  
✅ **Error Handling**: Clear messages for failures  
✅ **Timeout Protection**: 30-second wait limit

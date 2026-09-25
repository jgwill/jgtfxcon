# fxrmorder (Remove Order) Specification

> Delete Pending Orders from Broker

**Specification Version**: 1.0  
**Module**: `jgtfxcon/jgtfxremoveorder.py`  
**CLI Command**: `fxrmorder`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Removal of pending entry orders from the broker by order ID.

**Achievement Indicator**: Running `fxrmorder --demo -id 456789` produces:
- Order deleted from broker
- Confirmation message with order ID

**Value Proposition**: Cancel pending orders when signal is invalidated or trading plan changes.

---

## Structural Tension

**Current Reality**: Pending order exists on broker but is no longer wanted.

**Desired State**: Order removed, capital freed for other opportunities.

**Natural Progression**: Parse args → Connect → Find order → Delete request → Confirm deletion.

---

## CLI Interface

```python
def main():
    """
    JGT FX Remove Entry Order CLI.
    
    Arguments:
        --demo: Use demo account (vs real)
        -id, --orderid: Order ID to delete (required)
    
    Examples:
        # Remove order (demo)
        fxrmorder --demo -id 456789
        
        # Remove order (real)
        fxrmorder -id 456789
    """
```

---

## Order Deletion Flow

```python
def main():
    """
    Main entry point.
    
    Flow:
        1. Parse arguments
        2. Read broker credentials from config
        3. Connect to ForexConnect
        4. Query orders table by order_id
        5. If order not found: raise exception
        6. Create DELETE_ORDER request with:
           - COMMAND: DELETE_ORDER
           - ACCOUNT_ID: from order
           - ORDER_ID: from args
        7. Set up OrdersMonitor listener (on_delete)
        8. Send request
        9. Wait for deletion confirmation
        10. Print confirmation
        11. Logout
    """
```

---

## OrdersMonitor Class

```python
class OrdersMonitor:
    """Monitor for tracking order deletion."""
    
    def __init__(self):
        self.__order_id = None
        self.__deleted_orders = {}
        self.__event = threading.Event()
    
    def on_delete_order(self, _, __, order_row):
        """
        Callback when order is deleted.
        
        Stores deleted order and signals if this
        is the order we're waiting for.
        """
    
    def wait(self, time: float, order_id: str) -> Optional[OrderRow]:
        """
        Wait for order deletion with timeout.
        
        Returns order_row if deleted, None if timeout.
        """
    
    def find_order(self, order_id: str) -> Optional[OrderRow]:
        """Find order by ID in deleted orders."""
    
    def reset(self):
        """Clear tracked orders and reset event."""
```

---

## Delete Request

```python
# Find the order first
orders_table = fx.get_table(ForexConnect.ORDERS)
orders = orders_table.get_rows_by_column_value("order_id", order_id)

for order_row in orders:
    order = order_row
    break

if order is None:
    raise Exception(f"Order {order_id} not found")

# Create delete request
request = fx.create_request({
    fxcorepy.O2GRequestParamsEnum.COMMAND: fxcorepy.Constants.Commands.DELETE_ORDER,
    fxcorepy.O2GRequestParamsEnum.ACCOUNT_ID: order.account_id,
    fxcorepy.O2GRequestParamsEnum.ORDER_ID: str_old
})
```

---

## Output

```
The order has been deleted. Order ID: 456789
```

---

## Error Cases

| Scenario | Message |
|----------|---------|
| Order not found | "Order {id} not found" |
| Already filled | Cannot delete (order converted to trade) |
| Timeout | "Response waiting timeout expired." |

---

## Dependencies

```python
from forexconnect import fxcorepy, ForexConnect, Common
from jgtutils import jgtconstants, jgtos, jgtcommon, jgtpov
import common_samples
import threading
from time import sleep
```

---

## Quality Criteria

✅ **Order Lookup**: Verify order exists before delete  
✅ **Async Monitoring**: Wait for deletion confirmation  
✅ **Timeout Protection**: 30-second wait limit  
✅ **Demo/Real**: Account type selection  
✅ **Clear Output**: Confirmation message

# fxtr (Transaction Manager) Specification

> Trading Positions and Orders Management

**Specification Version**: 1.0  
**Module**: `jgtfxcon/jgtfxtransact.py`  
**CLI Command**: `fxtr`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Complete visibility into active trades and pending orders from the broker, with filtering and JSON export capabilities.

**Achievement Indicator**: Running `fxtr --demo -table all` produces:
- Account balance display
- List of all open trades with details
- List of all pending orders with details
- JSON export of transaction data

**Value Proposition**: Single command to see trading position state, essential for order management and risk assessment.

---

## Structural Tension

**Current Reality**: Trades and orders exist on broker but not visible in trading system.

**Desired State**: Complete transaction snapshot accessible via CLI with structured output.

**Natural Progression**: Connect → Query tables → Parse rows → Structure data → Output/Save.

---

## CLI Interface

```python
def main():
    """
    JGT FX Transact CLI.
    
    Arguments:
        --demo: Use demo account (vs real)
        -table: Table to display
            - "orders": Pending orders only
            - "trades": Open trades only
            - "all": Both tables (default)
        -account: Filter by account ID
        -id, --orderid: Filter by order/trade ID
        -i, --instrument: Filter by instrument
        -save: Save output to JSON file
    
    Examples:
        # Show all trades and orders (demo)
        fxtr --demo -table all
        
        # Show only pending orders
        fxtr --demo -table orders
        
        # Filter by instrument
        fxtr --demo -i EUR/USD
        
        # Save to file
        fxtr --demo -table trades -save
    """
```

---

## Data Structures

### FXOrder

```python
@dataclass
class FXOrder:
    """Represents a pending order."""
    order_id: str
    account_id: str
    offer_id: str
    instrument: str
    buy_sell: str              # "B" or "S"
    rate: float                # Entry rate
    rate_stop: float           # Stop rate (if set)
    rate_limit: float          # Limit rate (if set)
    amount: int                # Position size
    time_in_force: str         # Order duration
    status: str                # Order status
    
    @classmethod
    def from_string(cls, string: str) -> 'FXOrder':
        """Parse from ForexConnect row string."""
    
    def tojson(self) -> str:
        """Serialize to JSON."""
```

### FXTrade

```python
@dataclass
class FXTrade:
    """Represents an open trade."""
    trade_id: str
    account_id: str
    offer_id: str
    instrument: str
    buy_sell: str              # "B" or "S"
    open_rate: float           # Entry price
    amount: int                # Position size
    pl: float                  # Profit/Loss
    gross_pl: float            # Gross P/L
    stop: float                # Stop loss rate
    limit: float               # Take profit rate
    open_time: datetime        # Open timestamp
    
    @classmethod
    def from_string(cls, string: str) -> 'FXTrade':
        """Parse from ForexConnect row string."""
    
    def tojson(self) -> str:
        """Serialize to JSON."""
```

### FXTransactWrapper

```python
class FXTransactWrapper:
    """Container for orders and trades."""
    orders: FXOrders
    trades: FXTrades
    
    def add_orders(self, orders: FXOrders) -> None:
        """Add orders collection."""
    
    def add_trades(self, trades: FXTrades) -> None:
        """Add trades collection."""
    
    def tojson(self) -> str:
        """Serialize all to JSON."""
    
    def tojsonfile(self, filename: str) -> None:
        """Save to JSON file."""
```

---

## Core Flow

```python
def main():
    """
    Main entry point.
    
    Flow:
        1. Parse arguments
        2. Read broker credentials from config
        3. Connect to ForexConnect
        4. Get account information
        5. If table == "orders" or "all":
           - Query orders table
           - Parse each order row
           - Filter by ID/instrument if specified
           - Add to FXOrders collection
        6. If table == "trades" or "all":
           - Query trades table
           - Parse each trade row
           - Filter by ID/instrument if specified
           - Add to FXTrades collection
        7. Build FXTransactWrapper
        8. If -save: write to JSON file
        9. Logout
    """
```

---

## Table Parsing

```python
def parse_orders(
    table_manager,
    account_id: str
) -> FXOrders:
    """
    Parse orders table from ForexConnect.
    
    Returns FXOrders collection with all matching orders.
    """

def parse_trades(
    table_manager,
    account_id: str
) -> FXTrades:
    """
    Parse trades table from ForexConnect.
    
    Returns FXTrades collection with all matching trades.
    """

def _order_row_to_string(order_row) -> str:
    """Convert ForexConnect order row to parseable string."""

def _trade_row_to_string(trade_row, trade_data: dict) -> str:
    """Convert ForexConnect trade row to parseable string."""
```

---

## File Output

```python
def save_fxtransact_to_file(
    fxtransactwrapper: FXTransactWrapper,
    str_table: str = "all",
    str_connection: str = "",
    save_prefix: str = "fxtransact_"
) -> None:
    """
    Save transaction data to JSON file.
    
    Filename patterns:
        - All: {connection}_fxtransact_.json
        - Orders: {connection}_fxtransact_orders.json
        - Trades: {connection}_fxtransact_trades.json
        - By ID: {connection}_fxtransact_{order_id}.json
        - By Instrument: {connection}_fxtransact_{instrument}.json
    """
```

---

## Output Format

```json
{
    "orders": [
        {
            "order_id": "123456",
            "account_id": "12345678",
            "instrument": "EUR/USD",
            "buy_sell": "B",
            "rate": 1.0950,
            "rate_stop": 1.0900,
            "amount": 10000,
            "time_in_force": "GTC",
            "status": "Waiting"
        }
    ],
    "trades": [
        {
            "trade_id": "789012",
            "account_id": "12345678",
            "instrument": "GBP/USD",
            "buy_sell": "S",
            "open_rate": 1.2500,
            "amount": 20000,
            "pl": 150.25,
            "stop": 1.2600,
            "limit": 1.2300
        }
    ]
}
```

---

## Dependencies

```python
from forexconnect import ForexConnect, EachRowListener
from jgtutils import jgtconstants, jgtos, jgtcommon, jgtpov
from jgtutils.FXTransact import (
    FXTransactWrapper, FXOrder, FXOrders,
    FXTrade, FXTrades
)
import common_samples
```

---

## Quality Criteria

✅ **Dual Tables**: Orders and trades in one command  
✅ **Filtering**: By ID, instrument, or account  
✅ **JSON Export**: Structured output for automation  
✅ **Demo/Real**: Switch between account types  
✅ **Account Display**: Balance and ID shown  
✅ **Complete Data**: All order/trade fields captured

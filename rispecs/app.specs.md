# JGTfxcon Application Specification

> Master specification for the ForexConnect Broker Connection Library

**Specification Version**: 1.0  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Direct connection to FXCM broker for real-time price data acquisition and order execution, providing the raw market data substrate for all JGT trading operations.

**Achievement Indicator**: Users can fetch live/historical OHLCV data for any instrument/timeframe, create entry orders with stops and limits, and monitor trade execution.

**Value Proposition**: Bridge between FXCM ForexConnect API and the JGT Python ecosystem, abstracting broker complexity into simple function calls.

---

## Application Overview

JGTfxcon is a Python package that:
1. Connects to FXCM ForexConnect API for price data
2. Fetches historical and live OHLCV data
3. Creates entry orders with risk management
4. Monitors and modifies open positions
5. Exports trade reports for analysis

---

## Structural Tension

**Current Reality**: FXCM ForexConnect API requires complex session management, threading, and low-level calls.

**Desired State**: Simple Python functions fetch data and execute trades with broker complexity abstracted away.

**Natural Progression**: jgtfxcon provides `getPH()` for price history and `jgtfxcli` for command-line operations, used by higher-level packages.

---

## Core API

### Price Data Retrieval

```python
import jgtfxcon

# Get price history (default: 335 bars)
df = jgtfxcon.getPH('EUR/USD', 'H4')

# Get more bars with index
df = jgtfxcon.getPH('EUR/USD', 'H4', 3000, with_index=False)

# Add indicators from DataFrame
dfi = jgtfxcon.createFromDF(df)
```

### CLI Usage

```bash
# Fetch and cache price data
jgtfxcli -i EUR/USD -t H4 -c 500

# Fetch multiple instruments
jgtfxcli -i "EUR/USD,GBP/USD,SPX500" -t "H1,H4,D1"

# Fetch with timeline snapshot
jgtfxcli -i SPX500 -t H4 -c 500 -l "22101313"
```

---

## Price Data Service (JGTPDS)

### Data Model

```python
@dataclass
class PDSData:
    instrument: str      # "EUR/USD"
    timeframe: str       # "H4"
    open: float
    high: float
    low: float
    close: float
    volume: float
    date: datetime
```

### File Storage

```
$JGTPY_DATA/
├── pds/                 # Current price data
│   ├── EUR-USD_H4.csv
│   ├── SPX500_D1.csv
│   └── ...
└── pdl/                 # Timeline snapshots
    └── 22101313/
        ├── EUR-USD_H4.csv
        └── ...
```

### CSV Format

| Column | Type | Description |
|--------|------|-------------|
| Date | datetime | Bar timestamp |
| Open | float | Opening price |
| High | float | Highest price |
| Low | float | Lowest price |
| Close | float | Closing price |
| Volume | float | Tick volume |

---

## Order Execution

### Entry Order

```python
from jgtfxcon import jgtfxtransact

# Create entry order
order = jgtfxtransact.create_entry_order(
    instrument='EUR/USD',
    is_buy=True,
    amount=10000,
    rate=1.0950,
    stop=1.0900,
    limit=1.1050
)
```

### Order Types

| Type | Description |
|------|-------------|
| Entry | Pending order at specified price |
| Market | Execute at current market price |
| Stop | Stop-loss order |
| Limit | Take-profit order |

---

## Type Definitions

```python
from typing import Optional, List, Dict, Any
import pandas as pd
from datetime import datetime

# Instrument format: "EUR/USD", "SPX500", "XAU/USD"
Instrument = str

# Timeframe format: "m1", "m5", "m15", "m30", "H1", "H4", "D1", "W1", "M1"
Timeframe = str

def getPH(
    instrument: Instrument,
    timeframe: Timeframe,
    number: int = 335,
    with_index: bool = True,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> pd.DataFrame: ...

def createFromDF(
    df: pd.DataFrame,
    add_indicators: bool = True
) -> pd.DataFrame: ...

@dataclass
class EntryOrder:
    instrument: Instrument
    is_buy: bool
    amount: int
    rate: float
    stop: Optional[float] = None
    limit: Optional[float] = None
    
def create_entry_order(
    instrument: Instrument,
    is_buy: bool,
    amount: int,
    rate: float,
    stop: Optional[float] = None,
    limit: Optional[float] = None
) -> EntryOrder: ...
```

---

## Creative Advancement Scenarios

### Scenario: Initial Data Acquisition

**Desired Outcome**: Fresh price data for a new trading analysis

**Current Reality**: Need EUR/USD H4 data for indicator calculations

**Natural Progression**:
1. CLI invocation: `jgtfxcli -i EUR/USD -t H4 -c 500`
2. ForexConnect session established
3. Historical data fetched from broker
4. Data cached to `$JGTPY_DATA/pds/EUR-USD_H4.csv`
5. Ready for jgtpy/JGTIDS indicator enrichment

**Resolution**: PDS file contains 500 bars of OHLCV data

### Scenario: Entry Order Execution

**Desired Outcome**: Place a buy entry with stop and limit

**Current Reality**: FDB signal detected, ready to trade

**Natural Progression**:
1. Calculate entry: `rate = 1.0950`
2. Calculate stop: `stop = 1.0900` (below fractal)
3. Calculate limit: `limit = 1.1050` (1:2 R:R)
4. Execute: `create_entry_order('EUR/USD', True, 10000, rate, stop, limit)`
5. Order placed with broker

**Resolution**: Entry order pending at 1.0950 with risk managed

---

## Configuration

### Broker Credentials

Located at `~/.jgt/config.json`:

```json
{
  "user_id": "your_username",
  "password": "your_password",
  "url": "http://www.fxcorporate.com/Hosts.jsp",
  "connection": "Demo"
}
```

### Environment Variables

```bash
# Config location
JGT_CONFIG_DIR=~/.jgt

# Demo mode
JGT_DEMO=true

# Data storage
JGTPY_DATA=/path/to/data
```

---

## Module Structure

```
jgtfxcon/
├── __init__.py           # Package exports
├── jgtfxc.py             # Core ForexConnect wrapper
├── jgtfxcli.py           # CLI entry point
├── jgtfxcommon.py        # Shared utilities
├── JGTPDS.py             # Price Data Service
├── JGTPDSSvc.py          # PDS service layer
├── jgtfxtransact.py      # Order execution
├── jgtfxentryorder.py    # Entry order logic
├── jgtfxremoveorder.py   # Order removal
├── jgtfxreport.py        # Trade reporting
├── forexconnect/         # FXCM API bindings
└── scripts/              # Utility scripts
```

---

## Integration with JGT Ecosystem

```
FXCM ForexConnect API
    ↓
jgtfxcon (this package)
    ↓ provides OHLCV data
jgtpy/JGTPDS.py
    ↓ wraps PDS access
jgtpy/JGTIDS.py
    ↓ adds indicators (via jgtapy)
jgtpy/JGTCDS.py
    ↓ adds signals
jgtml
    ↓ analyzes patterns
```

---

## Quality Criteria

✅ **Simple API**: `getPH()` fetches data in one call  
✅ **Caching**: PDS files avoid redundant API calls  
✅ **Demo Mode**: Built-in demo/live credential switching  
✅ **CLI Complete**: All operations available via command line  
✅ **Order Management**: Entry, stop, limit, modification support

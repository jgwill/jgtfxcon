# PDS (Price Data Service) Specification

> OHLCV Price Data Acquisition and Storage

**Specification Version**: 1.0  
**Modules**: `jgtfxcon/JGTPDS.py`, `jgtfxcon/jgtfxc.py`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Clean OHLCV price data for any instrument/timeframe, retrieved from broker API or cached files, with proper column structure ready for indicator calculations.

**Achievement Indicator**: Calling `pds.getPH("EUR/USD", "H1")` produces:
- DataFrame with Date index
- OHLCV columns (Open, High, Low, Close, Volume)
- Optional Bid/Ask columns preserved
- Data from cache or fresh from broker

**Value Proposition**: Single interface for price data regardless of source - abstracts broker connectivity and caching.

---

## Structural Tension

**Current Reality**: Raw broker API returns data in various formats, connectivity required.

**Desired State**: Consistent DataFrame format with OHLCV columns, available offline from cache.

**Natural Progression**: Connect → Fetch → Transform → Cache → Return.

---

## Data Pipeline Position

```
[PDS] → IDS → CDS → TTF → MLF → MX
  ↑
Source of all data
```

**Dependencies**: jgtfxc for broker connectivity, jgtutils for file operations.

---

## Core Function: getPH

```python
def getPH(
    instrument: str,
    timeframe: str,
    quotes_count: int = -1,
    date_from: datetime = None,
    date_to: datetime = None,
    compressed: bool = False,
    quiet: bool = True,
    keep_bid_ask: bool = True
) -> pd.DataFrame:
    """
    Get Price History for instrument/timeframe.
    
    Args:
        instrument: Symbol (e.g., "EUR/USD", "SPX500")
        timeframe: Period (e.g., "m1", "H1", "D1")
        quotes_count: Number of bars to fetch (-1 = default)
        date_from: Start date for range
        date_to: End date for range
        compressed: Read/write gzip format
        quiet: Suppress output
        keep_bid_ask: Preserve Bid/Ask columns
    
    Logic:
        1. Check if cached file exists
        2. If cache valid and not fresh requested: read cache
        3. Otherwise: connect to broker, fetch, cache, return
    
    Returns:
        DataFrame with Date index and OHLCV columns
    """
```

---

## Data Sources

### Broker API (Fresh Data)

```python
def connect(quiet: bool = True, json_config_str: str = None):
    """
    Establish broker connection.
    
    Config loaded from:
        ~/.jgt/config.json or FXCON_CONFIG environment
    
    Connection parameters:
        - access_token: API authentication
        - account_id: Trading account
        - server: "demo" or "real"
    """

def disconnect(quiet: bool = True):
    """Close broker connection."""

def status(quiet: bool = True) -> bool:
    """Check if connected."""
```

### Filestore (Cached Data)

```python
def getPH_from_filestore(
    instrument: str,
    timeframe: str,
    quiet: bool = True,
    compressed: bool = False,
    with_index: bool = True,
    tlid_range: str = None,
    output_path: str = None,
    keep_bid_ask: bool = False
) -> pd.DataFrame:
    """
    Read cached PDS from filestore.
    
    File Paths:
        $JGTPY_DATA/pds/{instrument}_{timeframe}.csv
        Or with TLID range: {instrument}_{timeframe}_{tlid_range}.csv
    """
```

---

## Column Transformation

### Standard OHLC from Bid/Ask

```python
def pds_add_ohlc_stc_columns(
    dfsrc: pd.DataFrame,
    rounding_nb: int = 10
) -> pd.DataFrame:
    """
    Create standard OHLC from Bid/Ask columns.
    
    Transformation:
        Open = (BidOpen + AskOpen) / 2
        High = (BidHigh + AskHigh) / 2
        Low = (BidLow + AskLow) / 2
        Close = (BidClose + AskClose) / 2
        Median = (High + Low) / 2
    
    Rounding applied to prevent float precision issues.
    """
```

### Column Cleansing

```python
def _cleanse_original_columns(
    dfsrc: pd.DataFrame,
    quiet: bool = True
) -> pd.DataFrame:
    """
    Remove broker-specific columns not needed for analysis.
    
    Removed columns typically include:
        - tickqty (tick quantity)
        - Status, State columns
        - Internal broker identifiers
    """
```

---

## Output Schema

```python
{
    # Index
    "Date": datetime,          # Timestamp index
    
    # Standard OHLCV
    "Open": float,             # Opening price
    "High": float,             # Highest price
    "Low": float,              # Lowest price
    "Close": float,            # Closing price
    "Volume": int,             # Trade volume
    
    # Derived
    "Median": float,           # (High + Low) / 2
    
    # Bid/Ask (if keep_bid_ask=True)
    "BidOpen": float,
    "BidHigh": float,
    "BidLow": float,
    "BidClose": float,
    "AskOpen": float,
    "AskHigh": float,
    "AskLow": float,
    "AskClose": float,
}
```

---

## File Operations

### Read from File

```python
def read_ohlc_df_from_file(
    srcpath: str,
    quiet: bool = True,
    compressed: bool = False,
    with_index: bool = True,
    keep_bid_ask: bool = False
) -> pd.DataFrame:
    """
    Read OHLC DataFrame from CSV file.
    
    Supports:
        - Plain CSV
        - Gzip compressed CSV
        - Date as index or column
        - Bid/Ask column retention
    """
```

### Write to File

```python
def write_pds_to_file(
    df: pd.DataFrame,
    instrument: str,
    timeframe: str,
    compressed: bool = False,
    output_path: str = None
) -> str:
    """
    Write PDS DataFrame to cache file.
    
    Returns:
        File path where data was written
    """
```

---

## Timeframe Mapping

```python
TIMEFRAMES = {
    "m1": "1 minute",
    "m5": "5 minutes",
    "m15": "15 minutes",
    "m30": "30 minutes",
    "H1": "1 hour",
    "H2": "2 hours",
    "H3": "3 hours",
    "H4": "4 hours",
    "H6": "6 hours",
    "H8": "8 hours",
    "D1": "1 day",
    "W1": "1 week",
    "MN": "1 month"
}
```

---

## Instrument Properties

```python
# From iprops module
def get_pips(instrument: str) -> float:
    """
    Get pip size for instrument.
    
    Examples:
        "EUR/USD" -> 0.0001
        "USD/JPY" -> 0.01
        "SPX500" -> 1.0
    """

def get_precision(instrument: str) -> int:
    """Get decimal precision for prices."""
```

---

## File Locations

```python
# Environment variables:
JGTPY_DATA = "/src/jgtml/data/current"      # Current data
JGTPY_DATA_FULL = "/src/jgtml/data/full"    # Full historical

# PDS file paths:
$JGTPY_DATA/pds/{instrument}_{timeframe}.csv

# With TLID range:
$JGTPY_DATA/pds/{instrument}_{timeframe}_{tlid_from}_{tlid_to}.csv
```

---

## Error Handling

```python
# Connection errors
class ConnectionError(Exception):
    """Raised when broker connection fails."""

# Data errors
class DataNotFoundError(Exception):
    """Raised when requested data not available."""

# File errors  
class FileNotFoundError(Exception):
    """Raised when cache file missing and offline."""
```

---

## Dependencies

```python
import pandas as pd
import datetime
from jgtfxcon import jgtfxc as jfx      # Broker connectivity
from jgtfxcon import JGTPDHelper as jpd  # DataFrame helpers
from jgtfxcon import iprops              # Instrument properties
from jgtutils import jgtos               # File operations
from jgtutils import jgtconstants as c   # Constants
```

---

## Quality Criteria

✅ **Dual Source**: Broker API and file cache  
✅ **Column Standardization**: Consistent OHLCV format  
✅ **Bid/Ask Preservation**: Optional detailed prices  
✅ **Compression Support**: Gzip for storage efficiency  
✅ **Date Indexing**: Proper datetime index  
✅ **Connection Pooling**: Stay connected for batch operations

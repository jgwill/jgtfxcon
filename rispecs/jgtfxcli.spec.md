# jgtfxcli Specification

> Price Data CLI for Broker Connectivity

**Specification Version**: 1.0  
**Module**: `jgtfxcon/jgtfxcli.py`  
**CLI Command**: `jgtfxcli`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: Fresh OHLCV price data files downloaded from the broker and cached locally, ready for indicator calculations and signal detection.

**Achievement Indicator**: Running `jgtfxcli -i EUR/USD -t H1` produces:
- Price data fetched from broker API
- CSV saved to `$JGTPY_DATA/pds/EUR-USD_H1.csv`
- DataFrame with Date index, OHLCV columns, optional Bid/Ask

**Value Proposition**: Single command to refresh price data for any instrument/timeframe combination.

---

## Structural Tension

**Current Reality**: No local price data, or stale cached data.

**Desired State**: Fresh OHLCV data in standardized format, ready for analysis pipeline.

**Natural Progression**: Parse args → Connect broker → Fetch data → Transform → Cache → Return.

---

## CLI Interface

```python
def main():
    """
    JGT Price History CLI.
    
    Arguments:
        -i, --instrument: Instrument symbol(s), comma-separated
        -t, --timeframe: Timeframe(s), comma-separated
        -n, --quotescount: Number of bars to fetch
        --full: Use full historical data mode
        --tlidrange: TLID range for specific date range
        --viewpath: Show output path only (no fetch)
        --compress: Use gzip compression
        --keepbidask: Preserve Bid/Ask columns
        --dropna-volume: Drop zero-volume bars
        --server: Start PDS server (deprecated)
        --iprop: Download instrument properties (deprecated)
        -v, --verbose: Verbosity level (0-2)
        --debug: Enable debug mode
    
    Examples:
        # Single instrument/timeframe
        jgtfxcli -i EUR/USD -t H1
        
        # Multiple instruments and timeframes
        jgtfxcli -i EUR/USD,GBP/USD -t H1,H4,D1
        
        # Full historical data
        jgtfxcli -i SPX500 -t D1 --full
        
        # View output path only
        jgtfxcli -i EUR/USD -t H1 --viewpath
        
        # Keep bid/ask columns
        jgtfxcli -i EUR/USD -t H1 --keepbidask
    """
```

---

## Core Function Flow

```python
def main():
    """
    Main entry point.
    
    Flow:
        1. Parse arguments
        2. Split instruments and timeframes (comma-separated)
        3. For each instrument/timeframe pair:
           a. Call JGTPDSSvc.getPHs()
           b. Connect to broker if not connected
           c. Fetch price history
           d. Transform columns (Bid/Ask → OHLC)
           e. Write to cache file
        4. Print output paths
    """
```

---

## Service Layer: JGTPDSSvc

```python
def getPHs(
    instrument: str,              # Single or comma-separated
    timeframe: str,               # Single or comma-separated
    quote_count: int = -1,        # Bars to fetch
    start: datetime = None,       # Start date
    end: datetime = None,         # End date
    with_index: bool = True,      # Include date index
    quiet: bool = True,           # Suppress output
    compressed: bool = False,     # Gzip output
    tlid_range: str = None,       # TLID date range
    use_full: bool = False,       # Full historical mode
    default_quote_count: int = 335,
    default_add_quote_count: int = 89,
    verbose_level: int = 0,
    view_output_path_only: bool = False,
    keep_bid_ask: bool = False,
    dropna_volume: bool = True
) -> List[str]:
    """
    Fetch price history for multiple instruments/timeframes.
    
    Algorithm:
        1. Parse comma-separated instruments/timeframes
        2. Set stayConnected=True (single broker connection)
        3. For each pair: call getPH()
        4. Disconnect when complete
        5. Return list of updated POVs
    """

def getPH(
    instrument: str,
    timeframe: str,
    quote_count: int = -1,
    ...
) -> Tuple[str, pd.DataFrame]:
    """
    Fetch price history for single instrument/timeframe.
    
    Algorithm:
        1. If view_output_path_only: return path, None
        2. If use_full: calculate quote count for timeframe
        3. Convert TLID range to datetime if provided
        4. Call JGTPDS.getPH2file()
        5. If exception: try alternative command (fxcli2console)
        6. Return (filepath, dataframe)
    """
```

---

## Quote Count Calculation

```python
# For full historical mode, calculate proportional quote count
# Based on M1 as reference (pov_full_M1 default: 1000)

TIMEFRAME_RATIOS = {
    "m1": 1,
    "m5": 5,
    "m15": 15,
    "m30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
    "W1": 10080,
    "MN": 43200
}

def calculate_quote_counts_tf(m1_count: int) -> Dict[str, int]:
    """
    Calculate quote counts for all timeframes based on M1.
    
    Example with m1_count=1000:
        m1: 1000, m5: 200, H1: 16, D1: 1, ...
    """
```

---

## Alternative Command Fallback

```python
def _run_get_ph_using_alt_command(
    instrument: str,
    timeframe: str,
    use_full: bool,
    tlid_range: str,
    compressed: bool,
    quiet: bool,
    fxcli2console: str = "fxcli2console",
    keep_bid_ask: bool = False
) -> Tuple[bool, str]:
    """
    Fallback to fxcli2console if primary fetch fails.
    
    Runs: fxcli2console -i {instrument} -t {timeframe} [-kba]
    Output redirected to: $JGTPY_DATA/pds/{instrument}_{timeframe}.csv
    
    Used when ForexConnect fails but external tool works.
    """
```

---

## Output Paths

```python
def _make_output_fullpath(
    instrument: str,
    timeframe: str,
    use_full: bool,
    tlid_range: str,
    compress: bool,
    quiet: bool
) -> str:
    """
    Generate output file path.
    
    Patterns:
        Current: $JGTPY_DATA/pds/{i}_{t}.csv
        Full: $JGTPY_DATA_FULL/pds/{i}_{t}.csv
        TLID: $JGTPY_DATA/pds/{i}_{t}_{tlid_from}_{tlid_to}.csv
        Compressed: {path}.gz
    
    Example:
        /src/jgtml/data/current/pds/EUR-USD_H1.csv
    """
```

---

## Configuration

```python
# Environment variables
JGTPY_DATA = "/src/jgtml/data/current"
JGTPY_DATA_FULL = "/var/lib/jgt/full/data"
pov_full_M1 = 1000  # Reference bars for M1
JGT_KEEP_BID_ASK = "0"  # Override keep_bid_ask flag
RUN_ALT = "1"  # Enable alternative command fallback

# Config file (~/.jgt/config.json)
{
    "keep_bid_ask": false,
    "columns_to_remove": [...]
}
```

---

## Output Schema

```python
# Standard PDS DataFrame
{
    "Date": datetime,      # Index
    "Open": float,         # (BidOpen + AskOpen) / 2
    "High": float,         # (BidHigh + AskHigh) / 2
    "Low": float,          # (BidLow + AskLow) / 2
    "Close": float,        # (BidClose + AskClose) / 2
    "Volume": int,         # Trade volume
    
    # Optional (--keepbidask)
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

## Dependencies

```python
import pandas as pd
from jgtutils import jgtconstants, jgtos, jgtcommon, jgtpov
import JGTPDS as pds
import JGTPDSSvc as svc
```

---

## Quality Criteria

✅ **Multi-POV Support**: Comma-separated instruments/timeframes  
✅ **Full Mode**: Proportional quote counts for historical data  
✅ **Fallback**: Alternative command if primary fails  
✅ **Bid/Ask Preservation**: Optional detailed prices  
✅ **View Path**: Check output without fetching  
✅ **Zero-Volume Drop**: Clean data quality

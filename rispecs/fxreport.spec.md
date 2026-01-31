# fxreport Specification

> Trading Account Reports from Broker

**Specification Version**: 1.0  
**Module**: `jgtfxcon/jgtfxreport.py`  
**CLI Command**: `fxreport`  
**RISE Framework Compliance**: Full  
**Last Updated**: 2026-01-31

---

## Desired Outcome Definition

**What Users Create**: HTML trading reports downloaded from the broker for specified date range.

**Achievement Indicator**: Running `fxreport --demo` produces:
- Account balance displayed
- Report URL obtained
- HTML report saved to current directory

**Value Proposition**: Access broker trading reports for performance analysis and record keeping.

---

## Structural Tension

**Current Reality**: Trading history exists on broker but not accessible locally.

**Desired State**: HTML report saved locally for review and archiving.

**Natural Progression**: Parse args → Connect → Get accounts → Request report URL → Download → Save.

---

## CLI Interface

```python
def main():
    """
    JGT FX Report CLI.
    
    Arguments:
        --demo: Use demo account (vs real)
        --datefrom: Report start date (default: 1 month ago)
        --dateto: Report end date (default: today)
    
    Examples:
        # Default report (last month, demo)
        fxreport --demo
        
        # Specific date range
        fxreport --demo --datefrom 2026-01-01 --dateto 2026-01-31
        
        # Real account report
        fxreport --datefrom 2026-01-01
    """
```

---

## Report Generation Flow

```python
def main():
    """
    Main entry point.
    
    Flow:
        1. Parse arguments
        2. Read broker credentials from config
        3. Set date_from (default: 1 month ago)
        4. Set date_to (default: today)
        5. Connect to ForexConnect
        6. For each account:
           a. Get report URL from session
           b. Print account ID and balance
           c. Download HTML from URL
           d. Fix relative URLs to absolute
           e. Save to {account_id}.html
        7. Logout
    """
```

---

## Core Functions

```python
def get_reports(
    fc: ForexConnect,
    dt_from: datetime,
    dt_to: datetime
) -> None:
    """
    Download reports for all accounts.
    
    For each account:
        1. Get report URL via session.get_report_url()
        2. Print account info
        3. Download and save HTML
    """

def month_delta(
    date: datetime,
    delta: int
) -> datetime:
    """
    Calculate date offset by months.
    
    Handles month/year boundaries correctly.
    """
```

---

## Report Download

```python
# Get report URL from broker
url = fc.session.get_report_url(
    account.account_id,
    dt_from,
    dt_to,
    "html",       # Format
    None          # Additional params
)

# Download and process
response = urlopen(url)
report = response.read().decode('utf-8')

# Fix relative URLs to absolute
abs_path = '{0.scheme}://{0.netloc}/'.format(urlsplit(url))
report = re.sub(
    r'((?:src|href)=")[/\\](.*?")',
    r'\1' + abs_path + r'\2',
    report
)

# Save to file
with open(file_name, 'w') as file:
    file.write(report)
```

---

## Output

```
Obtaining report URL...
account_id=12345678; Balance=10532.25000
Report URL=https://fxcm.com/reports/...

Connecting...
OK
Downloading report...
Report is saved to 12345678.html
```

---

## Output File

- **Location**: Current working directory
- **Filename**: `{account_id}.html`
- **Content**: Complete HTML report with fixed resource URLs

---

## Dependencies

```python
from forexconnect import ForexConnect
from jgtutils import jgtconstants, jgtos, jgtcommon, jgtpov
import common_samples
import re
from urllib.parse import urlsplit
from urllib.request import urlopen
```

---

## Quality Criteria

✅ **Multi-Account**: Reports for all accounts  
✅ **Date Range**: Configurable start/end dates  
✅ **Default Range**: Sensible month default  
✅ **URL Fixing**: Relative paths made absolute  
✅ **Demo/Real**: Account type selection

# JGTfxcon RISE Specifications

> Reverse-engineer → Intent-extract → Specify → Export

This directory contains RISE-compliant specifications for JGTfxcon - the ForexConnect broker connection library for price data acquisition and order execution.

## Quick Start

1. **Start Here**: [`app.specs.md`](./app.specs.md) - Master specification
2. **Price Data**: [`pds.spec.md`](./pds.spec.md) - Price Data Service
3. **Trading**: [`fxtransact.spec.md`](./fxtransact.spec.md) - Order execution

## Specification Map

| Spec File | CLI Command | Module | Status |
|-----------|-------------|--------|--------|
| [`app.specs.md`](./app.specs.md) | - | Master Overview | ✅ |
| [`pds.spec.md`](./pds.spec.md) | - | JGTPDS.py (core) | ✅ |
| [`jgtfxcli.spec.md`](./jgtfxcli.spec.md) | `jgtfxcli` | Price data CLI + Service | ✅ |
| [`fxtransact.spec.md`](./fxtransact.spec.md) | `fxtr` | Orders/trades viewer | ✅ |
| [`fxaddorder.spec.md`](./fxaddorder.spec.md) | `fxaddorder` | Entry order creation | ✅ |
| [`fxrmorder.spec.md`](./fxrmorder.spec.md) | `fxrmorder` | Order deletion | ✅ |
| [`fxreport.spec.md`](./fxreport.spec.md) | `fxreport` | Trade reports | ✅ |

```
app.specs.md                    ← Master specification (start here)
├── pds.spec.md                 ← Price Data Service (OHLCV fetching)
├── jgtfxcli.spec.md            ← CLI for price data + JGTPDSSvc
├── fxtransact.spec.md          ← Orders/trades viewing (fxtr)
├── fxaddorder.spec.md          ← Entry order creation
├── fxrmorder.spec.md           ← Order deletion
└── fxreport.spec.md            ← Trade reporting
```

## RISE Framework Compliance

✅ **Desired Outcome Definition** - What users CREATE, not problems to solve  
✅ **Structural Tension** - Current reality vs desired state drives progression  
✅ **Natural Advancement** - Clear flow from current to desired  
✅ **Autonomous Specification** - Another LLM could implement from spec alone

## Key Concepts

### Core Capabilities
- **Price Data**: Fetch OHLCV data from FXCM broker
- **Order Execution**: Create entry orders, stops, limits
- **Trade Management**: Monitor and modify open trades
- **Reporting**: Export trade history

### Data Flow
```
ForexConnect API
    ↓
JGTPDS (Price Data Service)
    ↓
PDS files (cached OHLCV)
    ↓
jgtpy (adds indicators)
```

## Specification Version

- **Version**: 1.0
- **Framework**: RISE
- **Created**: 2026-01-31

# JGTfxcon RISE Specifications

> Reverse-engineer → Intent-extract → Specify → Export

This directory contains RISE-compliant specifications for JGTfxcon - the ForexConnect broker connection library for price data acquisition and order execution.

## Quick Start

1. **Start Here**: [`app.specs.md`](./app.specs.md) - Master specification
2. **Price Data**: [`pds.spec.md`](./pds.spec.md) - Price Data Service
3. **Trading**: [`fxtransact.spec.md`](./fxtransact.spec.md) - Order execution

## Specification Map

```
app.specs.md                    ← Master specification (start here)
├── pds.spec.md                 ← Price Data Service (OHLCV fetching)
├── fxcli.spec.md               ← CLI for price data operations
├── fxtransact.spec.md          ← Order creation and management
├── fxentryorder.spec.md        ← Entry order logic
├── fxreport.spec.md            ← Trade reporting
└── config.spec.md              ← Broker configuration
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

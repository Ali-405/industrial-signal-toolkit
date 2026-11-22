# Industrial Signal Toolkit

**Dependency-free Python utilities for industrial analog signals and tag scaling.**

Industrial Signal Toolkit provides reusable, testable numerical operations for automation engineers and developers working with PLC, SCADA, historians, industrial IoT, and manufacturing applications.

> **Status:** Alpha, version 0.1.0. Intended for evaluation and integration testing. This is not a safety system, certified measurement library, or replacement for instrument commissioning and validation.

## Features

- Decimal-based analog scaling: `engineering = raw × gain + offset`.
- Fractional Gain and Offset.
- Separate raw, engineering, and display values.
- Display-only rounding using `ROUND_HALF_UP`; engineering precision is retained.
- Low/high limit assessment without silently clamping values.
- Linear range mapping, reversed spans, and explicit opt-in clamping.
- Inverse Gain/Offset calculation for diagnostics.
- CSV batch processing with row-level error reporting.
- Python API and `istk` command-line interface.
- No runtime third-party dependencies; Python 3.10+.

## Installation

```bash
python -m pip install .
```

## Quick start

```python
from industrial_signal_toolkit import AnalogScaling, scale_analog_value

result = scale_analog_value(
    raw_value="10.25",
    config=AnalogScaling(
        gain="0.125",
        offset="-0.5",
        display_decimals=3,
        low_limit=0,
        high_limit=2,
    ),
)

print(result.raw_value)          # 10.25
print(result.engineering_value)  # 0.78125
print(result.display_value)      # 0.781
print(result.within_limits)      # True
```

## CLI

Scale one value:

```bash
istk scale --raw 10.25 --gain 0.125 --offset -0.5 --decimals 3
```

Process tag rows from CSV:

```bash
istk batch examples/tags.csv output/scaled-tags.csv
```

Required CSV columns: `tag_code`, `raw_value`. Optional columns: `scaling_enabled`, `gain`, `offset`, `display_decimals`, `low_limit`, `high_limit`.

Invalid rows remain in the output with `range_status=INVALID` and a diagnostic in `processing_error`. The batch command exits with status 1 when one or more rows are invalid.

## Engineering boundaries

- Raw input is always retained.
- Engineering values are not rounded to display precision.
- Limits classify a value; they do not clip, clamp, trip, or write a signal.
- `linear_map(..., clamp=True)` clamps only when explicitly requested.
- This toolkit performs local calculations only. It does not connect to PLCs, OPC UA, MQTT, databases, or control networks.
- No function writes a setpoint, output, tag, or control command.

Read [Engineering notes](docs/engineering-notes.md) before using calculated values in a plant application.

## Development

```bash
python -m pip install -e ".[test]"
pytest
```

GitHub Actions runs tests on Python 3.10–3.14. See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), and [Code of Conduct](CODE_OF_CONDUCT.md).

## License

MIT. See [LICENSE](LICENSE).

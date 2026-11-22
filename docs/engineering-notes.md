# Engineering notes and limitations

## Analog scaling

The library applies the configured affine transformation:

`EU = Raw × Gain + Offset`

Inputs are converted to Python `Decimal` to avoid introducing binary floating-point artifacts during ordinary decimal calculations. The raw input and engineering result remain distinct.

## Display precision

`display_decimals` controls the formatted display string only. It does not quantize or overwrite the engineering value. Display rounding uses `ROUND_HALF_UP`.

## Range assessment

Low and high limits classify the calculated engineering value. They do not clamp it, generate an alarm, trip equipment, or write to a controller.

## Linear mapping

`linear_map` supports reversed spans. Clamping is disabled by default and must be explicitly requested.

## Safety boundary

This package performs local calculations. It has no PLC, OPC UA, MQTT, historian, database, or control-system driver. Validate units, sensor ranges, wiring, scaling parameters, calibration, and failure behavior in the target plant before operational use. Do not use this alpha package as a safety function or as the sole basis for a control decision.

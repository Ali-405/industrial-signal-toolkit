"""Minimal API example for Industrial Signal Toolkit."""

from industrial_signal_toolkit import AnalogScaling, scale_analog_value, linear_map

reading = scale_analog_value(
    raw_value="10.25",
    config=AnalogScaling(
        gain="0.125",
        offset="-0.5",
        display_decimals=3,
        low_limit=0,
        high_limit=2,
    ),
)
print(f"Raw: {reading.raw_value}")
print(f"Engineering: {reading.engineering_value}")
print(f"Display: {reading.display_value}")
print(f"Within limits: {reading.within_limits}")

# Illustrative 4–20 mA to 0–100% mapping; confirm instrument configuration
# and units against the actual transmitter and PLC range before use.
percent = linear_map("12.0", "4.0", "20.0", "0", "100")
print(f"12 mA -> {percent}%")

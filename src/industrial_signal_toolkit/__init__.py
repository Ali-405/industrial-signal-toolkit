"""Industrial Signal Toolkit public API."""

from .scaling import (
    AnalogScaling,
    RangeState,
    ScaledValue,
    ScalingError,
    assess_range,
    format_engineering_value,
    inverse_gain_offset,
    linear_map,
    scale_analog_value,
)

__all__ = [
    "AnalogScaling",
    "RangeState",
    "ScaledValue",
    "ScalingError",
    "assess_range",
    "format_engineering_value",
    "inverse_gain_offset",
    "linear_map",
    "scale_analog_value",
]
__version__ = "0.1.0"

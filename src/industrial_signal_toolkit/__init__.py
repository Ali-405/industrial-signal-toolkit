"""Industrial Signal Toolkit public API."""

from .scaling import (
    AnalogScaling,
    ScaledValue,
    ScalingError,
    RangeState,
    scale_analog_value,
    linear_map,
    inverse_gain_offset,
    assess_range,
    format_engineering_value,
)

__all__ = [
    "AnalogScaling", "ScaledValue", "ScalingError", "RangeState",
    "scale_analog_value", "linear_map", "inverse_gain_offset",
    "assess_range", "format_engineering_value",
]
__version__ = "0.1.0"

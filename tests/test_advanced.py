from decimal import Decimal

import pytest

from industrial_signal_toolkit import (
    AnalogScaling,
    ScalingError,
    format_engineering_value,
    inverse_gain_offset,
    linear_map,
    scale_analog_value,
)


def test_negative_gain_is_supported():
    result = scale_analog_value("5", AnalogScaling(gain="-2", offset="1"))
    assert result.engineering_value == Decimal(-9)


def test_positive_offset_is_applied():
    assert scale_analog_value(4, AnalogScaling(gain=2, offset=3)).engineering_value == 11


def test_low_limit_is_inclusive():
    assert scale_analog_value(0, AnalogScaling(low_limit=0)).within_limits is True


def test_high_limit_is_inclusive():
    assert scale_analog_value(10, AnalogScaling(high_limit=10)).within_limits is True


def test_invalid_limit_order_rejected():
    with pytest.raises(ScalingError, match="low_limit"):
        scale_analog_value(5, AnalogScaling(low_limit=8, high_limit=2))


@pytest.mark.parametrize("decimals", [-1, 13, True, 1.5])
def test_invalid_display_precision_rejected(decimals):
    with pytest.raises(ScalingError):
        scale_analog_value(1, AnalogScaling(display_decimals=decimals))


@pytest.mark.parametrize("gain", ["NaN", "Infinity", "not-a-number"])
def test_invalid_gain_rejected(gain):
    with pytest.raises(ScalingError):
        scale_analog_value(1, AnalogScaling(gain=gain))


@pytest.mark.parametrize("offset", ["NaN", "-Infinity"])
def test_nonfinite_offset_rejected(offset):
    with pytest.raises(ScalingError):
        scale_analog_value(1, AnalogScaling(offset=offset))


def test_reversed_linear_mapping():
    assert linear_map(25, 100, 0, 0, 10) == Decimal("7.5")


def test_reversed_span_clamping():
    assert linear_map(120, 100, 0, 0, 10, clamp=True) == Decimal(0)


def test_zero_width_input_span_rejected():
    with pytest.raises(ScalingError, match="different"):
        linear_map(1, 5, 5, 0, 10)


def test_disabled_scaling_still_assesses_limits():
    result = scale_analog_value(12, AnalogScaling(enabled=False, low_limit=0, high_limit=10))
    assert result.engineering_value == Decimal(12)
    assert result.within_limits is False


def test_inverse_negative_gain():
    assert inverse_gain_offset(-9, -2, 1) == Decimal(5)


def test_zero_decimal_display():
    assert format_engineering_value("12.6", 0) == "13"


def test_two_decimal_display():
    assert format_engineering_value("12.345", 2) == "12.35"

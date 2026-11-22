from decimal import Decimal

import pytest

from industrial_signal_toolkit import (
    AnalogScaling,
    RangeState,
    ScalingError,
    assess_range,
    format_engineering_value,
    inverse_gain_offset,
    linear_map,
    scale_analog_value,
)


def test_fractional_gain_offset_preserves_raw_and_precision():
    r = scale_analog_value("10.25", AnalogScaling(gain="0.125", offset="-0.5", display_decimals=3))
    assert r.raw_value == Decimal("10.25")
    assert r.engineering_value == Decimal("0.78125")
    assert r.display_value == "0.781"


def test_display_rounding_is_half_up():
    assert format_engineering_value("1.2345", 3) == "1.235"
    assert format_engineering_value("-1.2345", 3) == "-1.235"


def test_disabled_scaling_passes_through():
    r = scale_analog_value("1.23456", AnalogScaling(enabled=False, gain=100, offset=50))
    assert r.engineering_value == Decimal("1.23456")


@pytest.mark.parametrize("value", [True, False, "NaN", "Infinity", "bad"])
def test_invalid_inputs_rejected(value):
    with pytest.raises(ScalingError):
        scale_analog_value(value, AnalogScaling())


def test_range_assessment_does_not_clamp():
    r = scale_analog_value(15, AnalogScaling(low_limit=0, high_limit=10))
    assert r.engineering_value == Decimal(15)
    assert r.within_limits is False


def test_inverse_scaling():
    assert inverse_gain_offset("12.55", "0.1", "0.25") == Decimal(123)


def test_inverse_rejects_zero_gain():
    with pytest.raises(ScalingError):
        inverse_gain_offset(10, 0, 2)


def test_linear_map_and_clamp():
    assert linear_map(50, 0, 100, 4, 20) == Decimal("12.0")
    assert linear_map(120, 0, 100, 0, 10) == Decimal(12)
    assert linear_map(120, 0, 100, 0, 10, clamp=True) == Decimal(10)


def test_assess_range_states():
    assert assess_range(-1, low_limit=0, high_limit=10).state is RangeState.LOW
    assert assess_range(5, low_limit=0, high_limit=10).state is RangeState.NORMAL
    assert assess_range(11, low_limit=0, high_limit=10).state is RangeState.HIGH

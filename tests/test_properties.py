"""Property-based invariants for industrial analog scaling."""

from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from industrial_signal_toolkit import (
    AnalogScaling,
    format_engineering_value,
    inverse_gain_offset,
    linear_map,
    scale_analog_value,
)

finite_values = st.decimals(
    min_value=Decimal(-10000),
    max_value=Decimal(10000),
    places=3,
    allow_nan=False,
    allow_infinity=False,
)
nonzero_gains = st.one_of(
    st.decimals(
        min_value=Decimal(-1000),
        max_value=Decimal("-0.001"),
        places=3,
        allow_nan=False,
        allow_infinity=False,
    ),
    st.decimals(
        min_value=Decimal("0.001"),
        max_value=Decimal(1000),
        places=3,
        allow_nan=False,
        allow_infinity=False,
    ),
)


@settings(max_examples=250, deadline=None, derandomize=True)
@given(
    raw=finite_values,
    gain=nonzero_gains,
    offset=finite_values,
)
def test_affine_scaling_inverse_round_trip(raw, gain, offset):
    result = scale_analog_value(raw, AnalogScaling(gain=gain, offset=offset))
    assert result.raw_value == raw
    assert result.engineering_value == raw * gain + offset
    assert inverse_gain_offset(result.engineering_value, gain, offset) == raw


@settings(max_examples=200, deadline=None, derandomize=True)
@given(
    input_min=st.integers(min_value=-10000, max_value=10000),
    input_width=st.integers(min_value=1, max_value=10000),
    output_min=st.integers(min_value=-10000, max_value=10000),
    output_width=st.integers(min_value=1, max_value=10000),
)
def test_linear_mapping_preserves_both_endpoints(
    input_min, input_width, output_min, output_width
):
    input_max = input_min + input_width
    output_max = output_min + output_width
    assert linear_map(input_min, input_min, input_max, output_min, output_max) == Decimal(output_min)
    assert linear_map(input_max, input_min, input_max, output_min, output_max) == Decimal(output_max)


@settings(max_examples=250, deadline=None, derandomize=True)
@given(
    value=st.integers(min_value=-100000, max_value=100000),
    input_start=st.integers(min_value=-1000, max_value=1000),
    input_width=st.integers(min_value=1, max_value=1000),
    output_start=st.integers(min_value=-1000, max_value=1000),
    output_width=st.integers(min_value=1, max_value=1000),
    reverse_input=st.booleans(),
    reverse_output=st.booleans(),
)
def test_clamped_mapping_stays_inside_output_range(
    value, input_start, input_width, output_start, output_width,
    reverse_input, reverse_output
):
    input_end = input_start + input_width
    output_end = output_start + output_width
    if reverse_input:
        input_start, input_end = input_end, input_start
    if reverse_output:
        output_start, output_end = output_end, output_start
    mapped = linear_map(
        value, input_start, input_end, output_start, output_end, clamp=True
    )
    assert Decimal(min(output_start, output_end)) <= mapped
    assert mapped <= Decimal(max(output_start, output_end))


@settings(max_examples=200, deadline=None, derandomize=True)
@given(value=finite_values, decimals=st.integers(min_value=0, max_value=6))
def test_display_precision_changes_only_the_formatted_value(value, decimals):
    result = scale_analog_value(
        value,
        AnalogScaling(enabled=False, display_decimals=decimals),
    )
    expected = Decimal(format_engineering_value(value, decimals))
    assert result.engineering_value == value
    assert Decimal(result.display_value) == expected

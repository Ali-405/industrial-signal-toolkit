"""Decimal-safe scaling and range assessment for numeric analog signals."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from enum import Enum
from typing import TypeAlias

Numeric: TypeAlias = Decimal | int | float | str


class ScalingError(ValueError):
    """Raised when a signal or scaling configuration is invalid."""


class RangeState(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


@dataclass(frozen=True)
class AnalogScaling:
    gain: Numeric = 1
    offset: Numeric = 0
    display_decimals: int = 3
    enabled: bool = True
    low_limit: Numeric | None = None
    high_limit: Numeric | None = None


@dataclass(frozen=True)
class ScaledValue:
    raw_value: Decimal
    engineering_value: Decimal
    display_value: str
    within_limits: bool | None


def decimal_value(value: Numeric, *, field: str = "value") -> Decimal:
    if isinstance(value, bool):
        raise ScalingError(f"{field} must be numeric, not boolean")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ScalingError(f"{field} must be a valid number") from exc
    if not result.is_finite():
        raise ScalingError(f"{field} must be finite")
    return result


def _decimals(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 12:
        raise ScalingError("display_decimals must be an integer between 0 and 12")
    return value


def format_engineering_value(value: Numeric, decimals: int = 3) -> str:
    number = decimal_value(value)
    places = _decimals(decimals)
    quantum = Decimal(1).scaleb(-places)
    try:
        with localcontext() as ctx:
            ctx.prec = max(34, len(number.as_tuple().digits) + places + 4)
            rounded = number.quantize(quantum, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ScalingError("value cannot be formatted at requested precision") from exc
    return f"{rounded:.{places}f}"


def scale_analog_value(raw_value: Numeric, config: AnalogScaling) -> ScaledValue:
    raw = decimal_value(raw_value, field="raw_value")
    if not isinstance(config, AnalogScaling):
        raise ScalingError("config must be an AnalogScaling instance")
    places = _decimals(config.display_decimals)
    if not isinstance(config.enabled, bool):
        raise ScalingError("enabled must be a boolean")
    if config.enabled:
        gain = decimal_value(config.gain, field="gain")
        offset = decimal_value(config.offset, field="offset")
        with localcontext() as ctx:
            ctx.prec = 34
            engineering = raw * gain + offset
    else:
        engineering = raw
    low = decimal_value(config.low_limit, field="low_limit") if config.low_limit is not None else None
    high = decimal_value(config.high_limit, field="high_limit") if config.high_limit is not None else None
    if low is not None and high is not None and low > high:
        raise ScalingError("low_limit must be less than or equal to high_limit")
    within = None if low is None and high is None else (
        (low is None or engineering >= low) and (high is None or engineering <= high)
    )
    return ScaledValue(raw, engineering, format_engineering_value(engineering, places), within)


def inverse_gain_offset(engineering_value: Numeric, gain: Numeric, offset: Numeric) -> Decimal:
    eu = decimal_value(engineering_value, field="engineering_value")
    g = decimal_value(gain, field="gain")
    off = decimal_value(offset, field="offset")
    if g == 0:
        raise ScalingError("gain must not be zero for inverse scaling")
    with localcontext() as ctx:
        ctx.prec = 34
        return (eu - off) / g


def linear_map(value: Numeric, input_min: Numeric, input_max: Numeric,
               output_min: Numeric, output_max: Numeric, *, clamp: bool = False) -> Decimal:
    x, xmin, xmax = map(decimal_value, (value, input_min, input_max))
    ymin, ymax = map(decimal_value, (output_min, output_max))
    if xmin == xmax:
        raise ScalingError("input_min and input_max must be different")
    if not isinstance(clamp, bool):
        raise ScalingError("clamp must be a boolean")
    if clamp:
        x = min(max(x, min(xmin, xmax)), max(xmin, xmax))
    with localcontext() as ctx:
        ctx.prec = 34
        return ymin + ((x - xmin) / (xmax - xmin)) * (ymax - ymin)


@dataclass(frozen=True)
class RangeAssessment:
    state: RangeState
    value: Decimal
    low_limit: Decimal | None
    high_limit: Decimal | None


def assess_range(value: Numeric, *, low_limit: Numeric | None = None,
                 high_limit: Numeric | None = None) -> RangeAssessment:
    number = decimal_value(value)
    low = decimal_value(low_limit, field="low_limit") if low_limit is not None else None
    high = decimal_value(high_limit, field="high_limit") if high_limit is not None else None
    if low is not None and high is not None and low > high:
        raise ScalingError("low_limit must be less than or equal to high_limit")
    state = RangeState.LOW if low is not None and number < low else (
        RangeState.HIGH if high is not None and number > high else RangeState.NORMAL
    )
    return RangeAssessment(state, number, low, high)

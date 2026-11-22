"""Command-line interface for Industrial Signal Toolkit."""

import argparse
import sys

from .batch import scale_csv
from .scaling import AnalogScaling, ScalingError, scale_analog_value


def main(argv=None):
    parser = argparse.ArgumentParser(prog="istk", description="Industrial analog signal utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("scale", help="scale one analog value")
    one.add_argument("--raw", required=True)
    one.add_argument("--gain", default="1")
    one.add_argument("--offset", default="0")
    one.add_argument("--decimals", type=int, default=3)
    one.add_argument("--disabled", action="store_true")
    one.add_argument("--low-limit")
    one.add_argument("--high-limit")
    batch = sub.add_parser("batch", help="process a tag CSV")
    batch.add_argument("input_csv")
    batch.add_argument("output_csv")
    args = parser.parse_args(argv)
    try:
        if args.command == "scale":
            result = scale_analog_value(args.raw, AnalogScaling(
                enabled=not args.disabled, gain=args.gain, offset=args.offset,
                display_decimals=args.decimals, low_limit=args.low_limit,
                high_limit=args.high_limit,
            ))
            print(f"raw_value={result.raw_value}")
            print(f"engineering_value={result.engineering_value}")
            print(f"display_value={result.display_value}")
            if result.within_limits is not None:
                print(f"within_limits={str(result.within_limits).lower()}")
            return 0
        processed, invalid = scale_csv(args.input_csv, args.output_csv)
        print(f"processed={processed} invalid={invalid} output={args.output_csv}")
        return 1 if invalid else 0
    except (OSError, ScalingError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

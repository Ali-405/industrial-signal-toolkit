"""CSV batch processing for analog tag scaling."""

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .scaling import AnalogScaling, ScalingError, scale_analog_value

REQUIRED_COLUMNS = {"tag_code", "raw_value"}
OUTPUT_COLUMNS = ["engineering_value", "display_value", "range_status", "processing_error"]


def _spreadsheet_safe(value: str) -> str:
    text = str(value)
    candidate = text.lstrip()
    if not candidate or candidate[0] not in "=+@-":
        return text
    try:
        if Decimal(candidate).is_finite():
            return text
    except InvalidOperation:
        pass
    return "'" + text


def process_rows(rows):
    results = []
    for source in rows:
        row = dict(source)
        row.update({c: "" for c in OUTPUT_COLUMNS})
        try:
            if not (row.get("tag_code") or "").strip():
                raise ScalingError("tag_code must not be empty")
            enabled_text = (row.get("scaling_enabled") or "true").strip().lower()
            if enabled_text not in {"true", "false", "1", "0", "yes", "no"}:
                raise ScalingError("scaling_enabled must be true/false, 1/0, or yes/no")
            config = AnalogScaling(
                enabled=enabled_text in {"true", "1", "yes"},
                gain=row.get("gain") or "1",
                offset=row.get("offset") or "0",
                display_decimals=int(row.get("display_decimals") or "3"),
                low_limit=row.get("low_limit") or None,
                high_limit=row.get("high_limit") or None,
            )
            result = scale_analog_value(row["raw_value"], config)
            row["engineering_value"] = str(result.engineering_value)
            row["display_value"] = result.display_value
            row["range_status"] = (
                "NOT_CONFIGURED" if result.within_limits is None
                else "IN_RANGE" if result.within_limits else "OUT_OF_RANGE"
            )
        except (KeyError, ValueError, TypeError, ScalingError) as exc:
            row["processing_error"] = str(exc)
            row["range_status"] = "INVALID"
        results.append(row)
    return results


def scale_csv(input_path, output_path):
    source_path, target_path = Path(input_path), Path(output_path)
    with source_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - headers)
        if missing:
            raise ScalingError("missing required CSV columns: " + ", ".join(missing))
        rows = process_rows(reader)
        fields = list(reader.fieldnames or []) + [c for c in OUTPUT_COLUMNS if c not in headers]
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _spreadsheet_safe(v) for k, v in row.items()})
    invalid = sum(bool(r["processing_error"]) for r in rows)
    return len(rows), invalid

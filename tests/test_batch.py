import csv

from industrial_signal_toolkit.batch import process_rows, scale_csv


def test_invalid_row_retained_with_error():
    rows = process_rows([
        {"tag_code": "AI_01", "raw_value": "10", "gain": "2"},
        {"tag_code": "AI_02", "raw_value": "bad"},
    ])
    assert rows[0]["engineering_value"] == "20"
    assert rows[1]["range_status"] == "INVALID"
    assert rows[1]["processing_error"]


def test_csv_export_and_formula_text_protection(tmp_path):
    source = tmp_path / "in.csv"
    target = tmp_path / "out.csv"
    source.write_text(
        'tag_code,raw_value,note\nAI_1,-2.5,=HYPERLINK("https://example.invalid")\n',
        encoding="utf-8",
    )
    assert scale_csv(source, target) == (1, 0)
    with target.open(encoding="utf-8", newline="") as f:
        row = next(csv.DictReader(f))
    assert row["engineering_value"] == "-2.5"
    assert row["note"].startswith("'=")

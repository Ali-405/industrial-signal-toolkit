import csv

from industrial_signal_toolkit.cli import main


def test_cli_scale_success(capsys):
    code = main(["scale", "--raw", "10.25", "--gain", "0.125", "--offset", "-0.5", "--decimals", "3"])
    output = capsys.readouterr().out
    assert code == 0
    assert "engineering_value=0.78125" in output
    assert "display_value=0.781" in output


def test_cli_scale_invalid_value_returns_error(capsys):
    code = main(["scale", "--raw", "NaN"])
    captured = capsys.readouterr()
    assert code == 2
    assert "error:" in captured.err


def test_cli_batch_success(tmp_path, capsys):
    source = tmp_path / "tags.csv"
    target = tmp_path / "scaled.csv"
    source.write_text("tag_code,raw_value,gain,offset\nAI_1,5,2,1\n", encoding="utf-8")

    code = main(["batch", str(source), str(target)])
    assert code == 0
    assert "processed=1 invalid=0" in capsys.readouterr().out
    with target.open(encoding="utf-8", newline="") as stream:
        row = next(csv.DictReader(stream))
    assert row["engineering_value"] == "11"


def test_cli_batch_invalid_row_returns_nonzero(tmp_path, capsys):
    source = tmp_path / "tags.csv"
    target = tmp_path / "scaled.csv"
    source.write_text("tag_code,raw_value\nAI_1,not-a-number\n", encoding="utf-8")

    code = main(["batch", str(source), str(target)])
    assert code == 1
    assert "invalid=1" in capsys.readouterr().out

import json
import subprocess
import sys
from pathlib import Path

import pytest

from evalkit.cli import main
from evalkit.results import grade_rows, load_samples, per_task_pass_at_k, summarize

DATA = Path(__file__).resolve().parent.parent / "data"


def write(tmp_path, rows):
    path = tmp_path / "runs.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return path


def test_load_samples_groups_by_task(tmp_path):
    path = write(tmp_path, [
        {"task_id": "a", "passed": True},
        {"task_id": "a", "passed": False},
        {"task_id": "b", "passed": True},
    ])
    assert load_samples(path) == {"a": [True, False], "b": [True]}


@pytest.mark.parametrize("row", [{"task_id": "a", "passed": 1}, {"passed": True}])
def test_load_samples_rejects_malformed_rows(tmp_path, row):
    with pytest.raises(ValueError):
        load_samples(write(tmp_path, [row]))


def test_k_larger_than_sample_count_is_an_error():
    with pytest.raises(ValueError, match="fewer than k"):
        per_task_pass_at_k({"a": [True, False]}, k=3)


def test_summarize_pass_at_one_is_mean_rate():
    samples = {"a": [True, True], "b": [False, False]}
    mean, (lo, hi) = summarize(samples, [1])[1]
    assert mean == 0.5 and lo <= mean <= hi


def test_grade_rows_and_unknown_grader():
    rows = [{"task_id": "x", "output": "12", "expected": "12"}]
    assert grade_rows(rows, "numeric") == [{"task_id": "x", "passed": True}]
    with pytest.raises(ValueError):
        grade_rows(rows, "vibes")


def test_bundled_data_has_expected_shape():
    for name in ("system_a", "system_b"):
        samples = load_samples(DATA / f"{name}.jsonl")
        assert len(samples) == 60 and {len(v) for v in samples.values()} == {10}


def test_sample_data_is_reproducible(tmp_path):
    script = Path(__file__).resolve().parent.parent / "scripts" / "make_sample_data.py"
    before = {n: (DATA / n).read_text() for n in ("system_a.jsonl", "system_b.jsonl")}
    subprocess.run([sys.executable, "-I", str(script)], check=True)
    assert {n: (DATA / n).read_text() for n in before} == before


def test_cli_report_and_compare(capsys):
    main(["report", str(DATA / "system_a.jsonl"), "-k", "1", "5"])
    out = capsys.readouterr().out
    assert "pass@1" in out and "pass@5" in out and "95% CI" in out
    main(["compare", str(DATA / "system_b.jsonl"), str(DATA / "system_a.jsonl")])
    out = capsys.readouterr().out
    assert "paired CI" in out and "sign test p" in out


def test_cli_grade_outputs_jsonl(capsys):
    main(["grade", str(DATA / "graded_example.jsonl"), "--grader", "numeric"])
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [r["passed"] for r in rows] == [True, True, False, False]

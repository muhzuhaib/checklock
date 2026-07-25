from pathlib import Path

import pytest

from checklock.scanner import InputError, load_snapshot, load_workflows, scan


def write(path: Path, contents: str) -> Path:
    path.write_text(contents, encoding="utf-8")
    return path


def test_reports_filter_and_missing_merge_group_for_required_job(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    write(workflows / "test.yml", """on:
  pull_request:
    paths:
      - 'src/**'
jobs:
  verify:
    name: test
    runs-on: ubuntu-latest
    steps: []
""")
    merge_queue, checks = load_snapshot(write(tmp_path / "snapshot.json", '{"merge_queue": true, "required_checks": [{"name": "test", "source": "main"}]}'))

    findings = scan(merge_queue, checks, load_workflows(workflows))

    assert [(finding.code, finding.severity) for finding in findings] == [("CHK001", "warning"), ("CHK002", "error")]
    assert findings[0].line == 3


def test_accepts_merge_group_and_reports_no_findings(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    write(workflows / "test.yaml", """on: [pull_request, merge_group]
jobs:
  test:
    runs-on: ubuntu-latest
    steps: []
""")
    merge_queue, checks = load_snapshot(write(tmp_path / "snapshot.json", '{"merge_queue": true, "required_checks": [{"name": "test"}]}'))

    assert scan(merge_queue, checks, load_workflows(workflows)) == []


def test_reports_unknown_required_check(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    write(workflows / "test.yml", """on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
""")
    merge_queue, checks = load_snapshot(write(tmp_path / "snapshot.json", '{"merge_queue": false, "required_checks": [{"name": "lint"}]}'))

    findings = scan(merge_queue, checks, load_workflows(workflows))

    assert len(findings) == 1
    assert findings[0].code == "CHK003"


def test_rejects_malformed_snapshot(tmp_path: Path) -> None:
    with pytest.raises(InputError, match="boolean 'merge_queue'"):
        load_snapshot(write(tmp_path / "snapshot.json", '{"required_checks": []}'))

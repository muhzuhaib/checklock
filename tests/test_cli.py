from pathlib import Path

from checklock.cli import main


def test_cli_emits_json_and_a_finding(tmp_path: Path, capsys) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "test.yml").write_text("""on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
""", encoding="utf-8")
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text('{"merge_queue": false, "required_checks": [{"name": "lint"}]}', encoding="utf-8")

    assert main(["scan", "--required-checks", str(snapshot), "--workflows", str(workflows), "--format", "json"]) == 1
    assert '"code": "CHK003"' in capsys.readouterr().out

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from .models import Finding, RequiredCheck, Workflow

_SKIP_FILTERS = {"paths", "paths-ignore", "branches", "branches-ignore"}


class InputError(ValueError):
    """Raised when an input cannot be safely scanned."""


def load_snapshot(path: Path) -> tuple[bool, list[RequiredCheck]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"Cannot read required-check snapshot {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON in required-check snapshot {path}: {exc.msg}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("merge_queue"), bool):
        raise InputError("Snapshot must be an object with a boolean 'merge_queue'.")
    raw_checks = data.get("required_checks")
    if not isinstance(raw_checks, list):
        raise InputError("Snapshot field 'required_checks' must be a list.")

    checks: list[RequiredCheck] = []
    for index, item in enumerate(raw_checks, start=1):
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise InputError(f"required_checks[{index}] needs a non-empty string 'name'.")
        source = item.get("source")
        if source is not None and not isinstance(source, str):
            raise InputError(f"required_checks[{index}].source must be a string when present.")
        checks.append(RequiredCheck(name=item["name"].strip(), source=source))
    return data["merge_queue"], checks


def _mapping_value(mapping: dict[Any, Any], key: str) -> Any:
    """Accept YAML 1.1 loaders that turn the unquoted key `on` into True."""
    return mapping.get(key, mapping.get(True) if key == "on" else None)


def _line_for_filter(text: str) -> int | None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        key = line.lstrip().split("#", 1)[0].strip().split(":", 1)[0]
        if key in _SKIP_FILTERS:
            return line_number
    return None


def _workflow_from_file(path: Path) -> Workflow:
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except OSError as exc:
        raise InputError(f"Cannot read workflow {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise InputError(f"Invalid YAML in workflow {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError(f"Workflow {path} must contain a YAML mapping.")

    raw_on = _mapping_value(data, "on")
    if isinstance(raw_on, str):
        triggers = {raw_on}
        has_filter = False
    elif isinstance(raw_on, list):
        triggers = {item for item in raw_on if isinstance(item, str)}
        has_filter = False
    elif isinstance(raw_on, dict):
        triggers = {str(key) for key in raw_on}
        has_filter = any(
            isinstance(config, dict) and any(key in config for key in _SKIP_FILTERS)
            for config in raw_on.values()
        )
    elif raw_on is None:
        triggers = set()
        has_filter = False
    else:
        raise InputError(f"Workflow {path} has an invalid 'on' value.")

    jobs = data.get("jobs", {})
    if not isinstance(jobs, dict):
        raise InputError(f"Workflow {path} has an invalid 'jobs' mapping.")
    job_names = {
        str(config.get("name", job_id)) if isinstance(config, dict) else str(job_id)
        for job_id, config in jobs.items()
    }
    return Workflow(
        path=path,
        triggers=frozenset(triggers),
        has_skip_filter=has_filter,
        filter_line=_line_for_filter(text) if has_filter else None,
        job_names=frozenset(job_names),
    )


def load_workflows(directory: Path) -> list[Workflow]:
    if not directory.is_dir():
        raise InputError(f"Workflow directory does not exist: {directory}")
    paths = sorted({*directory.glob("*.yml"), *directory.glob("*.yaml")})
    return [_workflow_from_file(path) for path in paths]


def scan(merge_queue: bool, required_checks: Iterable[RequiredCheck], workflows: Iterable[Workflow]) -> list[Finding]:
    workflow_list = list(workflows)
    findings: list[Finding] = []
    for check in required_checks:
        producers = [workflow for workflow in workflow_list if check.name in workflow.job_names]
        if not producers:
            findings.append(Finding(
                code="CHK003", severity="warning",
                message=f"No scanned workflow job is known to produce required check '{check.name}'.",
                required_check=check.name, source=check.source,
            ))
            continue
        for workflow in producers:
            if workflow.has_skip_filter:
                findings.append(Finding(
                    code="CHK001", severity="warning",
                    message=(f"Required check '{check.name}' is produced by a workflow with top-level "
                             "branch or path filters, so it can remain pending when that workflow is skipped."),
                    required_check=check.name, path=str(workflow.path), line=workflow.filter_line, source=check.source,
                ))
            if merge_queue and "merge_group" not in workflow.triggers:
                findings.append(Finding(
                    code="CHK002", severity="error",
                    message=(f"Required check '{check.name}' is produced by a workflow that omits the "
                             "merge_group trigger while merge queues are enabled."),
                    required_check=check.name, path=str(workflow.path), source=check.source,
                ))
    return findings

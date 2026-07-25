# Checklock v0.1 specification

## Goal

Prevent GitHub pull-request merge deadlocks caused by a required check whose workflow does not run.

## Inputs

1. A workflow directory (default: `.github/workflows`).
2. A JSON snapshot with a boolean `merge_queue` and `required_checks`, a list of objects containing non-empty `name` and optional `source` strings.

## Findings

| Code | Meaning | Severity |
| --- | --- | --- |
| `CHK001` | A required check is produced by a workflow with a top-level skip filter. | warning |
| `CHK002` | A required check's producer omits `merge_group` while the snapshot enables merge queues. | error |
| `CHK003` | No scanned job is known to produce a configured required check. | warning |

Each finding contains the required check, workflow path where applicable, a 1-based line number where available, and the snapshot source.

## Non-goals

- Editing GitHub settings or workflow files.
- Calling GitHub APIs during a scan.
- Proving every conditional job is reachable.
- Supporting reusable-workflow expansion in v0.1.

## Exit codes

- `0`: no findings.
- `1`: one or more findings.
- `2`: invalid command input, snapshot, or workflow YAML.

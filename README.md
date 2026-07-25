# Checklock

Checklock finds GitHub Actions configurations that can leave a required check pending forever and block a pull request from merging.

It is a local-first Python CLI: scan workflow files alongside a checked-in snapshot of the required checks and merge-queue setting. The scan makes no network calls and changes no repository files.

## What v0.1 detects

- required checks produced by workflows with top-level `paths`, `paths-ignore`, `branches`, or `branches-ignore` filters;
- required checks produced by workflows that omit the `merge_group` trigger when merge queues are enabled;
- required-check names that do not match any job name in the scanned workflows.

## Quick start

```powershell
python -m pip install -e ".[dev]"
checklock scan --required-checks .checklock/required-checks.json
```

The snapshot is deliberately simple and reviewable:

```json
{
  "merge_queue": true,
  "required_checks": [
    {"name": "test", "source": "main branch protection"}
  ]
}
```

Use `--format json` for CI-friendly output. A nonzero exit status means a finding was produced.

## Try it

The intentionally risky example emits `CHK001` and `CHK002`:

```powershell
checklock scan --required-checks examples/deadlock/required-checks.json --workflows examples/deadlock/workflows
```

The equivalent safe example exits successfully:

```powershell
checklock scan --required-checks examples/safe/required-checks.json --workflows examples/safe/workflows
```

## Limitations

This first release matches required checks to GitHub Actions job display names (or job IDs when no display name is set). It does not fetch branch protection or rulesets yet; create the snapshot from a reviewed export.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

## Why this exists

GitHub states that a required check can remain pending when its workflow is skipped by branch or path filtering, and that merge queues need a `merge_group` trigger for required checks to run. Checklock catches those configuration hazards before a pull request is blocked.

- [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-with-code-quality-features/troubleshooting-required-status-checks)
- [Events that trigger workflows](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows)

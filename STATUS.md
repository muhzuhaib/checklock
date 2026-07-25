# Checklock status

- Status: published.
- Purpose: a local Python scanner for required GitHub Actions checks that can deadlock a pull request.
- Current version: `v0.1.0`.
- Repository: https://github.com/muhzuhaib/checklock
- Release: https://github.com/muhzuhaib/checklock/releases/tag/v0.1.0
- Current scope: offline workflow/snapshot scan for top-level filters, merge-queue triggers, and unknown required checks.
- Verification: 5 automated tests pass on Python 3.14.4; included risky and safe examples produce the expected JSON findings and no findings, respectively. GitHub release `v0.1.0` is public and contains the wheel and source archive. The initial GitHub Actions run passed: https://github.com/muhzuhaib/checklock/actions/runs/30174233171
- Next: maintain issues and release follow-up fixes as needed.

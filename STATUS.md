# Checklock status

- Status: release-ready locally; publication blocked by invalid GitHub CLI authentication.
- Purpose: a local Python scanner for required GitHub Actions checks that can deadlock a pull request.
- Current version: unreleased (`0.1.0`).
- Current scope: offline workflow/snapshot scan for top-level filters, merge-queue triggers, and unknown required checks.
- Verification: 5 automated tests pass on Python 3.14.4; included risky and safe examples produce the expected JSON findings and no findings, respectively. Built and inspected `checklock-0.1.0-py3-none-any.whl` and `checklock-0.1.0.tar.gz`.
- Next: re-authenticate the GitHub CLI, then create and publish the public `muhzuhaib/checklock` repository and release `v0.1.0`.

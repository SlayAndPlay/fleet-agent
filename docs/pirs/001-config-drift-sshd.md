# PIR 001: Config drift on app01 (sshd MaxAuthTries)

## Summary
A manual change set MaxAuthTries to 10 on app01, contradicting the managed
baseline value of 4. The drift-check pipeline detected it.

## Impact
Weakened SSH brute-force protection on one host. No outage.

## Timeline (2026-11-10, local time, from Jenkins logs)
- Manual edit via ansible lineinfile on app01 (exact time not recorded)
- 18:16:38  Drift check shows changed=2 on app01, build still SUCCESS (detection gap)
- 18:18:32  Pipeline updated to fail on drift, build FAILURE with diff
- 18:19:52-18:20:29  After remediation, build SUCCESS, changed=0 on all hosts

## Detection
ansible-playbook --check --diff in Jenkins. Initially passive: it reported drift
but did not fail the build.

## Root cause
Out-of-band change on a managed host with no guard against manual edits.

## Resolution
Re-ran the playbook, restoring MaxAuthTries 4 and restarting sshd.

## What went well
Drift was visible in the diff the first time the check ran.

## What went poorly
The first pipeline version treated drift as success. A check that cannot fail
is not a control. The manual edit time was not recorded.

## Follow-ups
- Alert on red builds (Slack or ServiceNow)
- Audit manual root edits with auditd
- Auto-remediation only after human approval (see approval-boundaries.md)

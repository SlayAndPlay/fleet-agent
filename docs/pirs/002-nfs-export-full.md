# PIR 002: NFS export full (nfs01 /srv/nfs/data)

## Summary
The NFS export was filled with fallocate. Server and client both reported 100%
used. Fixed first by extending the LV, then (on a repeat) by deleting the file.

## Impact
Clients on app01 could not write more than ~1 MiB to /mnt/data.

## Timeline (2026-11-10, exact times not recorded)
1. Baseline detect passes (~1.5% used)
2. Fault injected, detect fails at 100% on nfs01 and app01
3. A small write (echo) succeeded; only a larger dd failed with ENOSPC at fsync
4. lvextend via lvol resizefs used the 4 GB free in the VG, detect passes (~60%)
5. Second injection, no VG headroom, fill.bin deleted, detect passes (~1%)
6. site.yml failed on nfs01: "no shrinking of lv_export" (role said 6g, LV was 10g)
7. Role changed to nfs_server_lv_size: 100%VG, pipeline green

## Detection
Manual: a detect playbook run by the operator. The Jenkins drift check would not
catch this, since a full disk is not config drift.

## Root cause
Injected fault (fallocate of nearly all free space).

## What went well
Two remediation paths were exercised. The manual fix was codified in the role.

## What went poorly
A tiny write succeeded while larger writes failed, so a small-write health check
would have missed the outage. The manual LV change was not put into the role
until the next playbook run failed.

## Follow-ups
- Alert on filesystem usage (done in PIR 003)
- Require approval for any LV extension (consumes shared VG capacity)
- Put manual remediation into the roles in the same change

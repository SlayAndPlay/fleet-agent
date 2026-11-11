# PIR 003: NFS full detected by monitoring

## Summary
The same NFS-full fault was injected again. Prometheus detected it and
Alertmanager received the alerts without operator action.

## Timeline (2026-11-11, EST)
- ~09:19-09:20  inject_nfs_full.yml run
- 09:21:09  FleetFilesystemAlmostFull firing for app01 /mnt/data
- 09:21:39  FleetFilesystemAlmostFull firing for nfs01 /srv/nfs/data
- 09:23-09:26  fill.bin deleted (exact time not recorded)
- by 09:26  Only Watchdog remained in Alertmanager; df showed 2% used

## Detection
node_exporter on each VM, scraped every 30s, rule fires after a 1m for: window.
Time to detect was about 2 minutes from injection.

## Findings
- One root cause produced two alerts (server and client), so alerts need grouping
- The cleanup time was not recorded because shell history had no timestamps

## Follow-ups
- Alertmanager receiver for ServiceNow with send_resolved and grouping by
  alertname and severity
- auditd rule on /srv/nfs/data
- HISTTIMEFORMAT set in .bashrc (done)

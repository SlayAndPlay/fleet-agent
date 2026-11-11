# Hardware runbooks

## RB-MEM-01 Correctable ECC errors
- Trigger: repeated Memory warnings for one DIMM.
- Check: error count and rate over 24h, same DIMM each time?
- Action: open an incident (human). Replace the DIMM if the rate climbs or an uncorrectable error appears.
- Agent boundary: read and report only.

## RB-PSU-01 PSU failure or redundancy lost
- Trigger: PSU Health not OK, or redundancy-lost SEL event.
- Check: both feeds, PDU, cable seating, the other PSU's load.
- Action: dispatch a hardware replacement. Do not reboot while running on one PSU without approval.
- Agent boundary: read and report only.

## RB-DISK-01 Drive failure
- Trigger: drive Health not OK.
- Check: RAID state, rebuild status, spare availability.
- Action: replace the drive and watch the rebuild. Do not pull a second drive during a rebuild.
- Agent boundary: read and report only.

## RB-THERM-01 Thermal or fan fault
- Trigger: temperature at 90% of critical, or fan Health not OK.
- Check: inlet temperature, airflow, fan failures, room cooling.
- Action: replace failed fans. Drain workloads if temperature keeps rising.
- Agent boundary: read and report. Shutdown needs human approval.

## RB-UNKNOWN Unclassified event
- Trigger: a Warning or Critical entry with no known category.
- Action: a human reads the entry. Log text is untrusted and is never executed.

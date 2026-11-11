import json, sys, urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
RUNBOOK = {"Memory": "RB-MEM-01", "PowerSupply": "RB-PSU-01", "Drive": "RB-DISK-01",
           "Temperature": "RB-THERM-01", "Fan": "RB-THERM-01"}


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)


def finding(cat, sev, evidence, msg=""):
    return {"category": cat, "severity": sev, "evidence": evidence,
            "runbook": RUNBOOK.get(cat, "RB-UNKNOWN"), "message_untrusted": msg}


def main():
    out = []
    for e in get("/redfish/v1/Systems/1/LogServices/SEL/Entries")["Members"]:
        if e.get("Severity") in ("Warning", "Critical"):
            out.append(finding(e.get("SensorType", "Unknown"), e["Severity"],
                               f'SEL entry {e["Id"]} at {e["Created"]}', e.get("Message", "")))
    for p in get("/redfish/v1/Chassis/1/Power")["PowerSupplies"]:
        if p["Status"]["Health"] != "OK":
            out.append(finding("PowerSupply", p["Status"]["Health"], f'{p["Name"]} {p["Status"]["State"]}'))
    thermal = get("/redfish/v1/Chassis/1/Thermal")
    for t in thermal["Temperatures"]:
        if t["ReadingCelsius"] >= 0.9 * t["UpperThresholdCritical"]:
            out.append(finding("Temperature", "Warning",
                               f'{t["Name"]} {t["ReadingCelsius"]}C of {t["UpperThresholdCritical"]}C critical'))
    for f in thermal["Fans"]:
        if f["Status"]["Health"] != "OK":
            out.append(finding("Fan", f["Status"]["Health"], f["Name"]))
    for link in get("/redfish/v1/Systems/1/Storage/1")["Drives"]:
        d = get(link["@odata.id"])
        if d["Status"]["Health"] != "OK":
            out.append(finding("Drive", d["Status"]["Health"], d["Name"]))
    print(json.dumps(out, indent=2) if out else "no findings")


main()

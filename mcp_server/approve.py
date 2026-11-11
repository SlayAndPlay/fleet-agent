import hashlib, json, os, sys, time

PROPOSALS = "/var/lib/fleet-mcp/proposals.json"
APPROVALS = "/etc/fleet-mcp/approvals.json"

if os.geteuid() != 0:
    sys.exit("Run with sudo.")
if len(sys.argv) != 2:
    sys.exit("usage: approve.py <proposal_id>")

pid = sys.argv[1]
p = json.load(open(PROPOSALS)).get(pid)
if not p or p["status"] != "pending":
    sys.exit("No pending proposal with that id.")

print("ACTION:", json.dumps(p["action"], indent=2))
print("Agent's stated reason (untrusted text):", p["reason"])
if input("Approve this exact action? [y/N] ").strip().lower() != "y":
    sys.exit("Not approved.")

digest = hashlib.sha256(json.dumps(p["action"], sort_keys=True).encode()).hexdigest()
approvals = json.load(open(APPROVALS))
approvals.append({"id": pid, "hash": digest, "approved_at": time.time()})
json.dump(approvals, open(APPROVALS, "w"), indent=2)
print("Approved.")

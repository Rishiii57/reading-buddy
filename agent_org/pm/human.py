"""Record a human (team) decision on a backlog item: the only way items needing human approval move.

    python -m agent_org.pm.human REQ-MIC-TOGGLE approve --by "team" --note "fix the mic bug"
    python -m agent_org.pm.human REQ-CONSENT-GATE approve --by "team" --note "remove the consent gate" \
        --scope "Remove the parent-consent dialog entirely"
    python -m agent_org.pm.human REQ-X reject --by "team" --note "..."
"""
import argparse
import json
import time
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("req")
    ap.add_argument("decision", choices=["approve", "reject", "defer", "accept"],
                    help="accept = take a change QA returned, on a human's explicit directive (recorded, never silent)")
    ap.add_argument("--by", required=True)
    ap.add_argument("--note", required=True)
    ap.add_argument("--scope", help="the human changed what is to be built")
    a = ap.parse_args(argv)
    rc_id = "RC-" + a.req.removeprefix("REQ-")
    b = json.loads((STATE / "backlog.json").read_text())
    item = b["items"][rc_id]
    status = {"approve": "approved", "reject": "rejected", "defer": "deferred", "accept": "accepted_by_human"}[a.decision]
    if a.decision == "accept" and item.get("status") != "returned_to_engineering":
        raise SystemExit("accept is only for a change QA returned; it records a human override of QA")
    at = time.strftime("%Y-%m-%dT%H:%M:%S")
    item["status"] = status
    if a.scope:
        item["human_scope"] = a.scope
    item.setdefault("history", []).append({"event": f"human_{status}", "at": at, "by": a.by, "note": a.note,
                                           **({"scope": a.scope} if a.scope else {})})
    (STATE / "backlog.json").write_text(json.dumps(b, indent=1, ensure_ascii=False))
    with open(STATE / "decisions.jsonl", "a") as f:
        f.write(json.dumps({"at": at, "rc": rc_id, "status": status, "why": f"human decision by {a.by}: {a.note}",
                            **({"scope": a.scope} if a.scope else {})}, ensure_ascii=False) + "\n")
    print(rc_id, "->", status)


if __name__ == "__main__":
    main()

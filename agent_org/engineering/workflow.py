"""Engineering workflow: approved requirement -> isolated branch + worktree -> tests -> submit to QA.

    python -m agent_org.engineering.workflow start  REQ-STALL-TIMING --role "Backend Engineer"
    (edit code in the printed worktree)
    python -m agent_org.engineering.workflow submit REQ-STALL-TIMING --summary "..." --root-cause "..."
    python -m agent_org.engineering.workflow merge  REQ-STALL-TIMING      # only after QA validated it
    python -m agent_org.engineering.workflow status

Rules enforced here (not just documented):
  * start refuses a requirement the PM has not approved (backlog status 'approved' or 'returned_to_engineering');
  * every requirement gets its own branch eng/<REQ> and git worktree, so parallel work cannot collide;
  * submit runs pytest and the offline tutor replay in the worktree and refuses to submit if tests fail;
  * submit flags files outside the owning roles' areas (ownership.json) and never allows .env;
  * merge refuses anything QA has not validated, and never pushes or deploys.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
ROOT = PKG.parent
WT_ROOT = ROOT.parent / "rb-worktrees"
CHANGES = Path(__file__).resolve().parent / "changes"
OWN = json.loads((Path(__file__).resolve().parent / "ownership.json").read_text())
BACKLOG = PKG / "pm" / "state" / "backlog.json"


def sh(cmd, cwd=ROOT, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"$ {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def backlog() -> dict:
    return json.loads(BACKLOG.read_text()) if BACKLOG.exists() else {"items": {}}


def set_status(rc_id: str, status: str, note: str):
    b = backlog()
    item = b["items"][rc_id]
    item["status"] = status
    item.setdefault("history", []).append({"event": status, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "note": note})
    BACKLOG.write_text(json.dumps(b, indent=1, ensure_ascii=False))


def rc_of(req: str) -> str:
    return "RC-" + req.removeprefix("REQ-")


def record(req: str) -> dict:
    f = CHANGES / f"{req}.json"
    return json.loads(f.read_text()) if f.exists() else {}


def save_record(req: str, rec: dict):
    CHANGES.mkdir(parents=True, exist_ok=True)
    (CHANGES / f"{req}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))


def start(req: str, role: str):
    item = backlog()["items"].get(rc_of(req))
    if not item or item.get("status") not in ("approved", "returned_to_engineering"):
        raise SystemExit(f"{req} is not approved for engineering (status: {item and item.get('status')}).")
    if role not in OWN["roles"]:
        raise SystemExit(f"unknown role {role}")
    base_branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    base = sh(["git", "rev-parse", "HEAD"])
    branch = f"eng/{req}"
    wt = WT_ROOT / req
    WT_ROOT.mkdir(exist_ok=True)
    if not wt.exists():
        exists = sh(["git", "branch", "--list", branch])
        sh(["git", "worktree", "add", str(wt), branch] if exists else ["git", "worktree", "add", "-b", branch, str(wt), base])
    rec = record(req) or {"requirement": req, "rounds": []}
    rec.update(branch=branch, worktree=str(wt), base_branch=base_branch, base_commit=base, role=role,
               started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    save_record(req, rec)
    set_status(rc_of(req), "in_progress", f"{role} started on {branch}")
    print(wt)


def owned(files: list[str], roles: list[str]) -> list[str]:
    areas = [a for r in roles for a in OWN["roles"].get(r, [])] + OWN["always_allowed"]
    return [f for f in files if not any(f == a or f.startswith(a.rstrip("/") + "/") or f.startswith(a) for a in areas)]


def run_checks(wt: Path) -> dict:
    py = sys.executable
    t = subprocess.run([py, "-m", "pytest", "-q"], cwd=wt, capture_output=True, text=True)
    tests = {"passed": t.returncode == 0, "tail": t.stdout.strip().splitlines()[-1:] if t.stdout else []}
    rp = subprocess.run([py, "-c", "import json; from eval.replay import score; from backend.tutor import TutorConfig; "
                         "print(json.dumps(score(TutorConfig())['summary']))"], cwd=wt, capture_output=True, text=True)
    replay = json.loads(rp.stdout.strip().splitlines()[-1]) if rp.returncode == 0 and rp.stdout.strip() else {"error": rp.stderr[-400:]}
    return {"tests": tests, "replay": replay}


def submit(req: str, summary: str, root_cause: str, roles: list[str] | None):
    rec = record(req)
    if not rec:
        raise SystemExit(f"{req} was never started")
    wt = Path(rec["worktree"])
    if sh(["git", "status", "--porcelain"], cwd=wt):
        sh(["git", "add", "-A"], cwd=wt)
        sh(["git", "-c", "user.name=Reading Buddy Engineering (AI)", "-c", "user.email=noreply@anthropic.com", "commit", "-q",
            "-m", f"{req}: {summary}\n\nRoot cause: {root_cause}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=wt)
    files = sh(["git", "diff", "--name-only", f"{rec['base_commit']}...HEAD"], cwd=wt).splitlines()
    if not files:
        raise SystemExit("no changes to submit")
    if any(f == ".env" or f.endswith("/.env") for f in files):
        raise SystemExit("refusing: .env must never be committed")
    from ..pm.catalog import ROOT_CAUSES
    rc = next(r for r in ROOT_CAUSES if r["id"] == rc_of(req))
    roles = roles or rc["owners"]
    outside = owned(files, roles)
    checks = run_checks(wt)
    rnd = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "summary": summary, "root_cause": root_cause,
           "commit": sh(["git", "rev-parse", "HEAD"], cwd=wt), "files": files, "outside_ownership": outside,
           "roles": roles, **checks}
    rec["rounds"].append(rnd)
    save_record(req, rec)
    if not checks["tests"]["passed"]:
        raise SystemExit(f"unit tests fail in {wt}; not submitted:\n{checks['tests']}")
    set_status(rc_of(req), "awaiting_qa", f"submitted {rnd['commit'][:8]}: {summary}")
    print(json.dumps({k: rnd[k] for k in ("commit", "files", "outside_ownership", "tests")}, indent=1))
    if outside:
        print("WARNING: files outside the owning roles' areas; QA/human review should look at:", outside)


def refresh(req: str):
    """Bring a requirement branch up to date with the integration branch (after other validated merges).
    QA then compares against the new integration commit, so only this requirement's change is measured."""
    rec = record(req)
    wt = Path(rec["worktree"])
    head = sh(["git", "rev-parse", "HEAD"])
    sh(["git", "-c", "user.name=Reading Buddy Integration (AI)", "-c", "user.email=noreply@anthropic.com", "merge", "-q",
        "--no-edit", head], cwd=wt)
    rec.setdefault("refreshes", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "from_base": rec["base_commit"], "to_base": head})
    rec["base_commit"] = head
    save_record(req, rec)
    set_status(rc_of(req), "in_progress", f"branch refreshed onto integration {head[:8]}")
    print(f"{req}: merged integration {head[:8]} into {rec['branch']}; QA base is now {head[:8]}")


def merge(req: str):
    item = backlog()["items"].get(rc_of(req), {})
    if item.get("status") != "validated_fixed":
        raise SystemExit(f"{req} has not been validated by QA (status: {item.get('status')}); not merging.")
    rec = record(req)
    sh(["git", "-c", "user.name=Reading Buddy Integration (AI)", "-c", "user.email=noreply@anthropic.com",
        "merge", "--no-ff", "-q", "-m", f"Merge {req} (QA validated)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
        rec["branch"]])
    rec["merged"] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "into": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
                     "commit": sh(["git", "rev-parse", "HEAD"])}
    save_record(req, rec)
    print(f"merged {rec['branch']} (not pushed, not deployed)")


def status():
    b = backlog()
    for rc_id, item in b["items"].items():
        rec = record("REQ-" + rc_id[3:])
        print(f"{item.get('priority', '-'):3} {('REQ-' + rc_id[3:]):30} {item.get('status', '-'):26} {rec.get('branch', '')}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("req"); s.add_argument("--role", required=True)
    s = sub.add_parser("submit"); s.add_argument("req"); s.add_argument("--summary", required=True)
    s.add_argument("--root-cause", required=True); s.add_argument("--roles")
    s = sub.add_parser("merge"); s.add_argument("req")
    s = sub.add_parser("refresh"); s.add_argument("req")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        start(a.req, a.role)
    elif a.cmd == "submit":
        submit(a.req, a.summary, a.root_cause, a.roles.split(",") if a.roles else None)
    elif a.cmd == "refresh":
        refresh(a.req)
    elif a.cmd == "merge":
        merge(a.req)
    else:
        status()


if __name__ == "__main__":
    main()

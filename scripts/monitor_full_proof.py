#!/usr/bin/env python3
"""Resume bounded CI source builds; publish only after every proof check passes."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time

from verify_upstream import COMMIT, LEAN_SHA256

REPOSITORY = "Federico2014/perelman-lean"
BRANCH = "verify/upstream-complete"
REQUIRED_STEPS = {
    "Build all original proof sources offline",
    "Check original targets and independent statement bridge",
    "Replay target modules with the Lean kernel",
    "Check the integrated full target and completeness gate",
}


def call(args, *, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def api(path, *args):
    for attempt in range(5):
        try:
            return json.loads(call(["gh", "api", f"repos/{REPOSITORY}/{path}", *args]))
        except subprocess.CalledProcessError:
            if attempt == 4:
                raise
            time.sleep(20)


def require_verified_run(run, jobs, expected_sha):
    if run["head_sha"] != expected_sha or run["status"] != "completed" or run["conclusion"] != "success":
        raise RuntimeError("The pinned integration run has not passed")
    if len(jobs) != 1 or jobs[0]["conclusion"] != "success":
        raise RuntimeError("Unexpected verification jobs")
    steps = {step["name"]: step["conclusion"] for step in jobs[0]["steps"]}
    if any(steps.get(name) != "success" for name in REQUIRED_STEPS):
        raise RuntimeError("A required proof check is missing, skipped, or unsuccessful")


def pending_checkpoint(log, run, jobs):
    if "POINCARE_BUILD_CHECKPOINT_PENDING" not in log:
        raise RuntimeError("CI failed outside the resumable source-build time slice")
    steps = {step["name"]: step["conclusion"] for step in jobs[0]["steps"]}
    if steps.get("Save this workflow's source-build checkpoint") != "success":
        raise RuntimeError("The incomplete source build has no successfully saved checkpoint")
    entries = re.findall(r"POINCARE_CHECKPOINT (\{[^\n]*\})", log)
    if len(entries) != 1:
        raise RuntimeError("Missing or ambiguous checkpoint provenance")
    data = json.loads(entries[0])
    if (data["commit"] != COMMIT or data["lean_archive_sha256"] != LEAN_SHA256
            or data["clean_source_origin"] is not True or data["source_complete"] is not False
            or data["origin_run"] != str(run["id"])
            or data["origin_attempt"] != str(run["run_attempt"])):
        raise RuntimeError("Unexpected checkpoint origin")
    return data


def publish(state_dir, sha, run, jobs):
    require_verified_run(run, jobs, sha)
    root_runs = api("actions/runs?per_page=100")["workflow_runs"]
    if not any(item["head_sha"] == sha and item["name"] == "Lean verification"
               and item["conclusion"] == "success" for item in root_runs):
        raise RuntimeError("The root-project regression CI has not passed at this revision")
    checkout = state_dir / "publication"
    call(["git", "clone", "--depth=1", "--branch", BRANCH,
          f"https://github.com/{REPOSITORY}.git", str(checkout)])
    if call(["git", "rev-parse", "HEAD"], cwd=checkout).strip() != sha:
        raise RuntimeError("The verification branch moved; refusing to publish a different revision")
    result = dict(status="verified", upstream_commit=COMMIT, integration_commit=sha,
                  workflow_run=run["html_url"], workflow_attempt=run["run_attempt"],
                  verified_at=datetime.now(timezone.utc).isoformat(),
                  lean="leanprover/lean4:v4.33.1", lean_archive_sha256=LEAN_SHA256,
                  allowed_axioms=["propext", "Classical.choice", "Quot.sound"],
                  target="Perelman.poincareConjecture : Perelman.PoincareConjecture",
                  source_build="All pinned original sources; clean origin with our own checkpoints only",
                  kernel_replay_modules=["PoincareConjecture.Proofs.Main", "AuditBridge", "PerelmanFull"],
                  independent_external_checker="Not run")
    (checkout / "full-proof/verification.json").write_text(json.dumps(result, indent=2) + "\n")
    template = (checkout / "docs/README.verified.md.in").read_text()
    (checkout / "README.md").write_text(template.replace("@CI_URL@", run["html_url"])
                                       .replace("@VERIFIED_SHA@", sha))
    (checkout / "full-proof/README.md").write_text(
        "# Full-target integration (verified)\n\n"
        f"The [complete verification run]({run['html_url']}) passed at `{sha}`.\n"
        "The geometric proof is the pinned upstream contribution; see "
        "[provenance](PROVENANCE.md) and [verification scope](verification.json).\n\n"
        "From this directory: `lake exe cache get`, `lake build`, then "
        "`lake env lean -DwarningAsError=true FullAudit.lean`.\n")
    provenance = checkout / "full-proof/PROVENANCE.md"
    provenance.write_text(provenance.read_text().replace(
        "**Verification pending.**", "**Verification passed at the recorded revision.** See [verification.json](verification.json).")
        .replace("All stages must succeed before this pending integration is described as verified.",
                 "All required stages succeeded in the recorded run."))
    (checkout / "ROADMAP.md").write_text(
        "# Proof scope\n\nThe full topological target is proved by the pinned upstream "
        "integration and has passed the recorded source, statement, axiom, kernel-module, "
        "and completeness-gate checks. See [the source map](full-proof/PROVENANCE.md) "
        "and [verification record](full-proof/verification.json).\n\n"
        "The root analytic development remains a separate partial contribution. "
        "It does not identify its supplied real-valued profiles with geometric "
        "invariants, construct Ricci surgery, or supply spherical coverings. "
        "Those root lemmas are not dependencies of the imported full proof.\n\n"
        f"The [historical root roadmap](https://github.com/{REPOSITORY}/blob/{sha}/ROADMAP.md) "
        "records the remaining work for a separate implementation based on those lemmas.\n\n"
        "The recorded kernel replay is per module. Nanoda and a fresh replay of "
        "every imported constant were not run. Dependencies retain their source notices.\n")
    for key, value in [("user.name", "Federico2014"),
                       ("user.email", "8458217+Federico2014@users.noreply.github.com"),
                       ("commit.gpgsign", "false")]:
        call(["git", "config", "--local", key, value], cwd=checkout)
    call(["git", "add", "README.md", "ROADMAP.md", "full-proof/README.md",
          "full-proof/PROVENANCE.md", "full-proof/verification.json"], cwd=checkout)
    call(["git", "-c", "core.hooksPath=/dev/null", "commit", "-m",
          "docs: record verified full-target proof integration [skip ci]"], cwd=checkout)
    # Both pushes must be fast-forwards; concurrent user commits are preserved.
    call(["git", "push", "origin", f"HEAD:{BRANCH}"], cwd=checkout)
    call(["git", "push", "origin", "HEAD:main"], cwd=checkout)
    return call(["git", "rev-parse", "HEAD"], cwd=checkout).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_sha):
        raise RuntimeError("Expected a full immutable integration SHA")
    root = args.state_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "controller.pid").write_text(str(os.getpid()) + "\n")
    state = dict(run_id=args.run_id, expected_sha=args.expected_sha, status="monitoring")
    deadline, previous, last_requested = time.monotonic() + 48 * 3600, 0, 0
    try:
        while time.monotonic() < deadline:
            run = api(f"actions/runs/{args.run_id}")
            if run["head_sha"] != args.expected_sha:
                raise RuntimeError("Workflow revision changed")
            state.update(attempt=run["run_attempt"], ci_status=run["status"], conclusion=run["conclusion"])
            (root / "state.json").write_text(json.dumps(state, indent=2) + "\n")
            if run["status"] != "completed" or run["run_attempt"] <= last_requested:
                time.sleep(20)
                continue
            jobs = api(f"actions/runs/{args.run_id}/attempts/{run['run_attempt']}/jobs")["jobs"]
            for attempt in range(5):
                try:
                    log = call(["gh", "run", "view", str(args.run_id), "--repo", REPOSITORY,
                                "--job", str(jobs[0]["id"]), "--log"])
                    break
                except subprocess.CalledProcessError:
                    if attempt == 4:
                        raise
                    time.sleep(20)
            (root / f"attempt-{run['run_attempt']}.log").write_text(log)
            if run["conclusion"] == "success":
                require_verified_run(run, jobs, args.expected_sha)
                state["status"] = "verified"
                if args.publish:
                    state["published_commit"] = publish(root, args.expected_sha, run, jobs)
                    state["status"] = "published"
                break
            if run["conclusion"] == "cancelled":
                raise RuntimeError("Verification was cancelled; no automatic restart")
            data = pending_checkpoint(log, run, jobs)
            if data["chunks"] >= 8 or data["candidate_modules"] <= previous:
                raise RuntimeError("Source build reached its bounded continuation limit or stopped making progress")
            previous = data["candidate_modules"]
            print(f"Resuming source compilation after {previous} modules; no full proof has passed yet", flush=True)
            call(["gh", "run", "rerun", str(args.run_id), "--repo", REPOSITORY])
            last_requested = run["run_attempt"]
        else:
            raise RuntimeError("The bounded verification monitor expired")
    except Exception as error:
        state.update(status="needs_review", error=str(error))
        if isinstance(error, subprocess.CalledProcessError):
            state["command_stderr"] = (error.stderr or "")[-4000:]
        print(f"Verification stopped: {error}", flush=True)
    (root / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(state), flush=True)
    return 0 if state["status"] in ("verified", "published") else 1


if __name__ == "__main__":
    raise SystemExit(main())

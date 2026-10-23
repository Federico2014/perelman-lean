#!/usr/bin/env python3
"""Run the pinned upstream proof checks in disposable, isolated containers."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


REPO = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/frenzymath/PoincareConjecture.git"
COMMIT = "62db01af9388dc1d9b56b66d6674f4c09b2318a2"
LEAN_SHA256 = "890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235"
LEAN_URL = "https://github.com/leanprover/lean4/releases/download/v4.33.1/lean-4.33.1-linux.tar.zst"
BASE = "ubuntu@sha256:b3cc40b72b93588182b5410f723c7aaf142363311c2aa993d8a453ddcbb3ae15"
VOLUMES = {name: f"perelman-ci-{name}" for name in ("source", "lake", "runtime", "full")}


def check_axioms(output, names):
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    result = {}
    for name in names:
        label = re.escape(name) + r"(?:\.\{[^}]*\})?"
        entries = re.findall(r"'" + label + r"' depends on axioms:\s*\[([^\]]*)\]", output)
        empty = re.findall(r"'" + label + r"' does not depend on any axioms", output)
        if len(entries) + len(empty) != 1:
            raise RuntimeError(f"Missing or ambiguous axiom audit for {name}")
        axioms = [] if empty else [item.strip() for item in entries[0].split(",") if item.strip()]
        normalized = [re.sub(r"\.\{[^}]*\}$", "", item) for item in axioms]
        if any(item not in allowed for item in normalized):
            raise RuntimeError(f"Unapproved axiom dependency in {name}: {axioms}")
        result[name] = axioms
    return result


def run(args, log):
    print("+ " + shlex.join(map(str, args)), flush=True)
    with log.open("w") as output:
        process = subprocess.Popen(
            list(map(str, args)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for line in process.stdout:
            output.write(line)
            output.flush()
            sys.stdout.write(line)
            sys.stdout.flush()
        status = process.wait()
    log.with_suffix(log.suffix + ".status").write_text(str(status) + "\n")
    if status:
        raise RuntimeError(f"Command exited {status}; see {log.name}")


def volume(name, destination, readonly=False):
    return ["--mount", f"type=volume,src={VOLUMES[name]},dst={destination}" + (",readonly" if readonly else "")]


def bind(source, destination, readonly=True):
    return ["--mount", f"type=bind,src={source},dst={destination}" + (",readonly" if readonly else "")]


def container(image, stage, script, log, *, network=False, extra=(), cwd="/work/proof", timeout=14400):
    args = [
        "docker", "run", "--rm", "--name", f"perelman-ci-{stage}",
        "--network", "bridge" if network else "none", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--user=501:501", "--memory=12g",
        "--cpus=4", "--pids-limit=1024", "--ulimit", "nofile=65536:65536",
        "--env", "LEAN_NUM_THREADS=4", "--env", "TMPDIR=/work/runtime/tmp",
        "--workdir", cwd,
    ]
    args += volume("source", "/work/proof", True)
    args += volume("lake", "/work/proof/.lake")
    args += volume("runtime", "/work/runtime") + volume("runtime", "/home/verifier")
    args += bind(REPO / "scripts/upstream_audit", "/audit") + list(extra)
    args += [image, "timeout", f"{timeout}s", "/bin/sh", script]
    run(args, log)


def prepare(workspace):
    source, tools, logs = (workspace / name for name in ("source", "tools", "logs"))
    for path in (source, tools, logs):
        path.mkdir(parents=True, exist_ok=True)
    run(["git", "-C", source, "init", "-q"], logs / "git-init.log")
    run(["git", "-C", source, "remote", "add", "origin", SOURCE], logs / "git-origin.log")
    run(["git", "-C", source, "fetch", "--depth=1", "origin", COMMIT], logs / "git-fetch.log")
    run(["git", "-C", source, "checkout", "--detach", COMMIT], logs / "git-checkout.log")
    actual = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if actual != COMMIT:
        raise RuntimeError("Unexpected source revision")
    archive = tools / "lean.tar.zst"
    run(["curl", "-L", "--fail", "--retry", "2", "-o", archive, LEAN_URL], logs / "toolchain-download.log")
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != LEAN_SHA256:
        raise RuntimeError("Official Lean archive checksum mismatch")
    (tools / "Dockerfile").write_text(f'''FROM {BASE}
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl git zstd build-essential python3 && rm -rf /var/lib/apt/lists/*
COPY lean.tar.zst /tmp/lean.tar.zst
RUN echo "{LEAN_SHA256}  /tmp/lean.tar.zst" | sha256sum -c - && tar --zstd -xf /tmp/lean.tar.zst -C /opt && mv /opt/lean-4.33.1-linux /opt/lean && rm /tmp/lean.tar.zst
RUN groupadd --gid 501 verifier && useradd --uid 501 --gid 501 --create-home verifier
ENV PATH="/opt/lean/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
WORKDIR /work/proof
USER verifier
''')
    run(["docker", "build", "--tag", "perelman-ci-lean:4.33.1", tools], logs / "image-build.log")
    image = subprocess.check_output(
        ["docker", "image", "inspect", "perelman-ci-lean:4.33.1", "--format", "{{.Id}}"], text=True,
    ).strip()
    args = ["docker", "run", "--rm", "--network=none", "--user=0:0", "--memory=2g"]
    args += bind(source, "/input")
    for name in VOLUMES:
        args += volume(name, f"/volume-{name}")
    args += [image, "/bin/sh", "-c",
             "cp -a /input/. /volume-source/ && mkdir -p /volume-runtime/tmp && "
             "chown -R 501:501 /volume-source /volume-lake /volume-runtime /volume-full"]
    run(args, logs / "volume-setup.log")
    state = {"source": SOURCE, "commit": COMMIT, "lean_archive_sha256": LEAN_SHA256, "image": image}
    (workspace / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    container(image, "prepare", "/audit/prepare.sh", logs / "prepare.log", network=True, timeout=3600)


def integration(image, logs):
    (REPO / "full-proof/.lake").mkdir(exist_ok=True)
    extra = bind(REPO / "full-proof", "/integration/full-proof")
    extra += volume("full", "/integration/full-proof/.lake")
    extra += bind(REPO / "Perelman/Statement.lean", "/integration/Perelman/Statement.lean")
    extra += bind(REPO / "CompletionPolicy.lean", "/integration/CompletionPolicy.lean")
    container(image, "integration", "/audit/integration.sh", logs / "integration.log",
              extra=extra, cwd="/integration/full-proof", timeout=1800)
    output = (logs / "integration.log").read_text()
    # The build and explicit source check each print the same axiom declaration.
    source_output = output.rsplit("FullAudit source check begins", 1)[-1]
    evidence = check_axioms(source_output, ["Perelman.poincareConjecture"])
    if "Completeness gate passed for the full Poincare target" not in source_output:
        raise RuntimeError("The full-target completeness gate did not run")
    (logs / "integration-axioms.json").write_text(json.dumps(evidence, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["prepare", "build", "targets", "replay", "integration"])
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    try:
        if args.stage == "prepare":
            prepare(workspace)
            return 0
        state = json.loads((workspace / "state.json").read_text())
        if state["commit"] != COMMIT:
            raise RuntimeError("Verification state has a different source revision")
        logs, image = workspace / "logs", state["image"]
        if args.stage == "integration":
            integration(image, logs)
        else:
            script = {"build": "build.sh", "targets": "check_targets.sh", "replay": "kernel_replay.sh"}[args.stage]
            limit = 14400 if args.stage == "build" else 1800
            container(image, args.stage, f"/audit/{script}", logs / f"{args.stage}.log", timeout=limit)
            if args.stage == "targets":
                evidence = check_axioms((logs / "targets.log").read_text(), [
                    "PoincareConjecture.topologicalPoincareSkeleton",
                    "PoincareConjecture.smoothPoincareSkeleton", "IndependentAudit.intended",
                ])
                (logs / "target-axioms.json").write_text(json.dumps(evidence, indent=2) + "\n")
                print(json.dumps(evidence, indent=2), flush=True)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

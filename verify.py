#!/usr/bin/env python3
"""Re-elaborate the local Lean sources and run the axiom audit.

Dependencies must already be available through Lake. This script does not
download packages or modify their cached source/build directories.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
MODULES = [
    "Perelman.Statement", "Perelman.Extinction", "Perelman.UpperSlope",
    "Perelman.Piecewise", "Perelman.Covering", "Perelman", "Audit", "Completion",
]


def run(args: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False,
    )
    if expect_success and result.returncode:
        print(result.stdout, end="", flush=True)
        raise RuntimeError(f"Command failed (exit {result.returncode}): {args!r}")
    return result


def verify_revisions() -> None:
    manifest = json.loads((ROOT / "lake-manifest.json").read_text())
    for package in manifest["packages"]:
        path = ROOT / ".lake" / "packages" / package["name"]
        if not path.is_dir():
            raise RuntimeError("Dependencies missing: run `lake update` and `lake exe cache get` first")
        actual = run(["git", "-C", str(path), "rev-parse", "HEAD"]).stdout.strip()
        if actual != package["rev"]:
            raise RuntimeError(f"Revision mismatch for {package['name']}: {actual}")
    print("Dependency revisions match lake-manifest.json", flush=True)


def verify() -> None:
    verify_revisions()
    print(run(["lake", "env", "lean", "--version"]).stdout, end="", flush=True)
    for module in MODULES:
        relative = Path(*module.split("."))
        output = ROOT / ".lake" / "build" / "lib" / "lean" / relative.with_suffix(".olean")
        output.parent.mkdir(parents=True, exist_ok=True)
        print(f"Checking {module}", flush=True)
        result = run([
            "lake", "env", "lean", "-DwarningAsError=true", "-o", str(output),
            str(relative.with_suffix(".lean")),
        ])
        print(result.stdout, end="", flush=True)
    print("Local source checks and axiom audit passed. The full Poincare conjecture remains unproved.", flush=True)


def self_test_audit() -> None:
    probes = [
        ("axiom Perelman.auditProbe : False", "Local axiom is forbidden"),
        ("theorem Perelman.auditProbe : False := by sorry", "Unapproved axiom sorryAx"),
        ("def Perelman.auditProbe : False := by sorry", "Unapproved axiom sorryAx"),
    ]
    with tempfile.TemporaryDirectory(prefix="audit-probes-", dir=ROOT / ".lake") as tmp:
        for i, (declaration, expected) in enumerate(probes):
            source = Path(tmp) / f"Probe{i}.lean"
            source.write_text(f"import Audit\n\n{declaration}\n\n#audit_perelman\n")
            result = run(["lake", "env", "lean", str(source)], expect_success=False)
            if not result.returncode or expected not in result.stdout:
                raise RuntimeError(f"Audit failed to reject probe {i}:\n{result.stdout}")
            print(f"Audit rejection probe {i + 1}/{len(probes)} passed", flush=True)

    completion_probes = [
        ("", "full Poincare theorem is missing"),
        (
            "universe u\ntheorem Perelman.poincareConjecture "
            "(h : Perelman.PoincareConjecture.{u}) : Perelman.PoincareConjecture.{u} := h",
            "theorem type does not match the full target",
        ),
    ]
    for i, (declaration, expected) in enumerate(completion_probes):
        result = completion_check(declaration)
        if not result.returncode or expected not in result.stdout:
            raise RuntimeError(f"Completeness gate failed to reject probe {i}:\n{result.stdout}")
        print(f"Completeness rejection probe {i + 1}/{len(completion_probes)} passed", flush=True)


def completion_check(declaration: str = "") -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory(prefix="completion-", dir=ROOT / ".lake") as tmp:
        source = Path(tmp) / "Check.lean"
        source.write_text(f"import Completion\n\n{declaration}\n\n#require_complete_poincare\n")
        return run(["lake", "env", "lean", str(source)], expect_success=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="also test rejection of axioms and incomplete proofs")
    parser.add_argument("--require-complete", action="store_true", help="require a theorem proving the full Poincare target")
    args = parser.parse_args()
    try:
        verify()
        if args.self_test:
            self_test_audit()
        if args.require_complete:
            result = completion_check()
            print(result.stdout, end="", flush=True)
            if result.returncode:
                raise RuntimeError("The full Poincare proof is not complete")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

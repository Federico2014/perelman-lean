"""Fail-closed parsing checks; these fixtures do not verify Lean proofs."""

import unittest
import json
from pathlib import Path
import tempfile
import tarfile

from verify_upstream import check_axioms, checkpoint_metadata, sha256_file, COMMIT, LEAN_SHA256
from upstream_audit.restore_checkpoint import validate_member
from monitor_full_proof import require_verified_run, REQUIRED_STEPS


class AxiomAuditTests(unittest.TestCase):
    def test_standard_foundations_and_universe_suffixes(self):
        output = "'A.target.{u}' depends on axioms: [propext, Classical.choice.{u}, Quot.sound]"
        self.assertEqual(len(check_axioms(output, ["A.target"])["A.target"]), 3)

    def test_missing_target_is_not_an_empty_axiom_set(self):
        with self.assertRaises(RuntimeError):
            check_axioms("error: Unknown constant A.target", ["A.target"])

    def test_duplicate_targets_are_ambiguous(self):
        line = "'A.target' depends on axioms: [propext]"
        with self.assertRaises(RuntimeError):
            check_axioms(line + "\n" + line, ["A.target"])

    def test_incomplete_and_native_proofs_are_rejected(self):
        for axiom in ["sorryAx", "sorryAx.{u}", "Lean.ofReduceBool", "Custom.assumption"]:
            with self.subTest(axiom=axiom), self.assertRaises(RuntimeError):
                check_axioms(f"'A.target' depends on axioms: [{axiom}]", ["A.target"])

    def test_every_requested_target_must_be_present(self):
        with self.assertRaises(RuntimeError):
            check_axioms("'A.target' does not depend on any axioms", ["A.target", "A.other"])


class CheckpointTests(unittest.TestCase):
    def test_pinned_metadata_and_archive_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "build.tar.zst"
            archive.write_bytes(b"fixture; not a Lean proof cache")
            data = dict(commit=COMMIT, lean_archive_sha256=LEAN_SHA256,
                        format=1, clean_source_origin=True, sha256=sha256_file(archive))
            (root / "metadata.json").write_text(json.dumps(data))
            self.assertEqual(checkpoint_metadata(root), data)
            archive.write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "checksum"):
                checkpoint_metadata(root)

    def test_foreign_or_unattested_cache_is_rejected(self):
        for changes in [{"commit": "0" * 40}, {"lean_archive_sha256": "wrong"},
                        {"format": 2}, {"clean_source_origin": "true"}]:
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                data = dict(commit=COMMIT, lean_archive_sha256=LEAN_SHA256,
                            format=1, clean_source_origin=True)
                data.update(changes)
                (root / "metadata.json").write_text(json.dumps(data))
                with self.assertRaises(RuntimeError):
                    checkpoint_metadata(root)

    def test_restore_rejects_path_escape_and_links(self):
        for name in ["/build/evil", "build/../evil", "../build/evil", "packages/evil"]:
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                validate_member(tarfile.TarInfo(name))
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.BLKTYPE]:
            member = tarfile.TarInfo("build/looks-safe")
            member.type = kind
            with self.subTest(kind=kind), self.assertRaises(RuntimeError):
                validate_member(member)
        validate_member(tarfile.TarInfo("build/lib/lean/Actual.olean"))


class PublicationGateTests(unittest.TestCase):
    def test_only_successful_full_checks_at_the_pinned_revision_qualify(self):
        run = dict(head_sha="a" * 40, status="completed", conclusion="success")
        jobs = [dict(conclusion="success", steps=[dict(name=name, conclusion="success")
                                                 for name in REQUIRED_STEPS])]
        require_verified_run(run, jobs, "a" * 40)
        with self.assertRaises(RuntimeError):
            require_verified_run(run, jobs, "b" * 40)
        for step in jobs[0]["steps"]:
            step["conclusion"] = "skipped"
            with self.subTest(step=step["name"]), self.assertRaises(RuntimeError):
                require_verified_run(run, jobs, "a" * 40)
            step["conclusion"] = "success"
        with self.assertRaises(RuntimeError):
            require_verified_run(run, [], "a" * 40)

    def test_cache_only_success_cannot_publish_a_proof(self):
        run = dict(head_sha="a" * 40, status="completed", conclusion="success")
        jobs = [dict(conclusion="success", steps=[dict(name="Save cache", conclusion="success")])]
        with self.assertRaises(RuntimeError):
            require_verified_run(run, jobs, "a" * 40)


if __name__ == "__main__":
    unittest.main()

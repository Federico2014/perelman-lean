"""Fail-closed parsing checks; these fixtures do not verify Lean proofs."""

import unittest

from verify_upstream import check_axioms


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


if __name__ == "__main__":
    unittest.main()

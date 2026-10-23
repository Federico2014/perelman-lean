import Perelman.Statement
import Lean.Util.CollectAxioms
import Lean.Elab.Command
import Lean.Meta.Basic

open Lean Elab Command Meta in
elab "#require_complete_poincare" : command => do
  let proofName := `Perelman.poincareConjecture
  let some decl := (← getEnv).find? proofName
    | throwError "Completeness gate: full Poincare theorem is missing"
  let .thmInfo info := decl
    | throwError "Completeness gate: expected a theorem, not an axiom or definition"
  unless info.levelParams.length == 1 do
    throwError "Completeness gate: expected the full universe-polymorphic target signature"
  let expected := mkConst ``Perelman.PoincareConjecture (info.levelParams.map Level.param)
  liftTermElabM do
    unless ← isDefEq info.type expected do
      throwError "Completeness gate: theorem type does not match the full target (extra hypotheses are not allowed)"
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  for ax in ← collectAxioms proofName do
    unless allowed.contains ax do
      throwError "Completeness gate: unapproved axiom {ax}"
  logInfo "Completeness gate passed for the full Poincare target"

import Perelman
import Lean.Util.CollectAxioms

/-! Kernel dependency audit. No theorem asserting `PoincareConjecture` exists here. -/

#check Perelman.PoincareConjecture
#print axioms Perelman.obstructionTime_pos
#print axioms Perelman.logarithmic_comparison_on
#print axioms Perelman.logarithmic_comparison
#print axioms Perelman.logarithmic_comparison_with_jumps
#print axioms Perelman.no_nonnegative_on_obstruction_interval
#print axioms Perelman.area_rate_bound
#print axioms Perelman.rescaled_rate_bound
#print axioms Perelman.forwardSlopeBound_of_hasDerivWithinAt
#print axioms Perelman.normalized_area_forwardSlopeBound
#print axioms Perelman.no_global_area_profile

open Lean Elab Command in
elab "#audit_perelman" : command => do
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  let mut checked : Nat := 0
  for (name, info) in (← getEnv).constants.toList do
    if (`Perelman).isPrefixOf name then
      match info with
      | .axiomInfo _ => throwError "Local axiom is forbidden: {name}"
      | .thmInfo _ =>
        checked := checked + 1
      | _ => pure ()
      for ax in ← collectAxioms name do
        unless allowed.contains ax do
          throwError "Unapproved axiom {ax} in {name}"
  if checked == 0 then
    throwError "No Perelman theorems were audited"
  logInfo m!"Axiom audit passed for {checked} theorem declarations in namespace Perelman."

#audit_perelman

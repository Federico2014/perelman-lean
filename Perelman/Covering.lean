import Perelman.Statement
import Mathlib.Analysis.Normed.Module.Connected
import Mathlib.Topology.Homotopy.Lifting

/-!
The final covering-space implication, conditional on an actual spherical covering
map. Constructing that covering from Perelman's geometric argument is not done here.
-/

namespace Perelman

/-- A nonempty connected covering of a simply connected, locally path connected
space is a homeomorphism. A section is obtained by lifting the identity, and
uniqueness of lifts proves that the section is a two-sided inverse. -/
noncomputable def coveringHomeomorphOfSimplyConnected
    {E X : Type*} [TopologicalSpace E] [TopologicalSpace X]
    [Nonempty E] [PreconnectedSpace E]
    [SimplyConnectedSpace X] [LocallyPathConnectedSpace X]
    {p : E → X} (hp : IsCoveringMap p) : E ≃ₜ X := by
  classical
  apply Classical.choice
  let e₀ : E := Classical.choice inferInstance
  obtain ⟨s, ⟨hse, hps⟩, _⟩ :=
    hp.existsUnique_continuousMap_lifts (ContinuousMap.id X) (p e₀) e₀ rfl
  have hright : Function.RightInverse s p := fun x => congrFun hps x
  have heq : (fun e => s (p e)) = (fun e => e) :=
    hp.eq_of_comp_eq (s.continuous.comp hp.continuous) continuous_id
      (funext fun e => hright (p e)) e₀ hse
  exact ⟨{
    toFun := p
    invFun := s
    left_inv := fun e => congrFun heq e
    right_inv := hright
    continuous_toFun := hp.continuous
    continuous_invFun := s.continuous
  }⟩

/-- A simply connected, locally path connected space covered by the standard
three-sphere is homeomorphic to that sphere. The covering map is an explicit
hypothesis: this is not the Poincare conjecture. -/
theorem nonempty_homeomorph_threeSphere_of_covering
    {M : Type*} [TopologicalSpace M] [SimplyConnectedSpace M]
    [LocallyPathConnectedSpace M] (p : ThreeSphere → M) (hp : IsCoveringMap p) :
    Nonempty (M ≃ₜ ThreeSphere) := by
  have hdim : (1 : Cardinal) < Module.rank ℝ (EuclideanSpace ℝ (Fin 4)) := by
    rw [← Module.finrank_eq_rank]
    simp
  letI : PathConnectedSpace ThreeSphere :=
    isPathConnected_iff_pathConnectedSpace.mp
      (isPathConnected_sphere hdim (0 : EuclideanSpace ℝ (Fin 4)) (by norm_num : (0 : ℝ) ≤ 1))
  exact ⟨(coveringHomeomorphOfSimplyConnected hp).symm⟩

end Perelman

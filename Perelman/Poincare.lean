import Perelman.Statement
import PoincareConjecture.Proofs.Main

/-!
The full topological target, using the pinned upstream geometric proof.
The upstream contributors supply the Ricci-flow, surgery, extinction and
topological reconstruction development. This module adapts their theorem to
the shared statement without adding a geometric or conjecture hypothesis.
-/

namespace Perelman

universe u

/-- A compact Hausdorff simply connected topological three-manifold without
boundary is homeomorphic to the standard three-sphere. Second countability is
derived from compactness and the Euclidean chart model. -/
theorem nonempty_homeomorph_three_sphere
    (M : Type u) [TopologicalSpace M] [T2Space M]
    [ChartedSpace (EuclideanSpace ℝ (Fin 3)) M]
    [SimplyConnectedSpace M] [CompactSpace M] : Nonempty (M ≃ₜ ThreeSphere) := by
  let : SecondCountableTopology M :=
    ChartedSpace.secondCountable_of_sigmaCompact (EuclideanSpace ℝ (Fin 3)) M
  exact _root_.PoincareConjecture.topologicalPoincareSkeleton M

/-- The complete universe-polymorphic topological Poincaré target. -/
theorem poincareConjecture : PoincareConjecture.{u} := by
  intro M _ _ _ _ _
  exact nonempty_homeomorph_three_sphere M

end Perelman

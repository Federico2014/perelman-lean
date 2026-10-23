import Mathlib.AlgebraicTopology.FundamentalGroupoid.SimplyConnected
import Mathlib.Geometry.Manifold.Instances.Sphere

/-!
The target statement only. No proof of `PoincareConjecture` is supplied.
This uses the same hypotheses as mathlib's corresponding `proof_wanted` statement,
without importing that file or introducing an axiom for the conjecture.
-/

namespace Perelman

universe u

/-- The unit three-sphere in Euclidean four-space. -/
abbrev ThreeSphere := Metric.sphere (0 : EuclideanSpace ℝ (Fin 4)) 1

/-- The topological three-dimensional Poincaré conjecture, as a proposition.
Charts into all of ℝ³ specify manifolds without boundary. Compactness is the
closed-manifold condition; simple connectivity also includes path connectivity.
This is a definition of the goal, not a theorem asserting it. -/
def PoincareConjecture : Prop :=
  ∀ (M : Type u) [TopologicalSpace M] [T2Space M]
    [ChartedSpace (EuclideanSpace ℝ (Fin 3)) M]
    [SimplyConnectedSpace M] [CompactSpace M], Nonempty (M ≃ₜ ThreeSphere)

end Perelman

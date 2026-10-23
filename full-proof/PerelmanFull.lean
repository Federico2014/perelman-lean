import Perelman.Statement
import PoincareConjecture.Proofs.Main

/-!
Integration of the pinned upstream proof. The complete geometric proof belongs
 to the upstream authors. This bridge derives second countability from the
 original compact charted-manifold hypotheses; it adds no geometric assumption.
-/

namespace Perelman
universe u

theorem poincareConjecture : PoincareConjecture.{u} := by
  intro M _ _ _ _ _
  let : SecondCountableTopology M :=
    ChartedSpace.secondCountable_of_sigmaCompact (EuclideanSpace ℝ (Fin 3)) M
  exact _root_.PoincareConjecture.topologicalPoincareSkeleton M

end Perelman

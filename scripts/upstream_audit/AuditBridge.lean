import AuditTarget
import PoincareConjecture.Proofs.Main

namespace IndependentAudit
universe u

theorem intended : IntendedPoincare.{u} := by
  intro M _ _ _ _ _
  let : SecondCountableTopology M :=
    ChartedSpace.secondCountable_of_sigmaCompact (EuclideanSpace ℝ (Fin 3)) M
  exact PoincareConjecture.topologicalPoincareSkeleton M

end IndependentAudit

#check @PoincareConjecture.topologicalPoincareSkeleton
#print PoincareConjecture.topologicalPoincareSkeleton
#print axioms PoincareConjecture.topologicalPoincareSkeleton
#check @PoincareConjecture.smoothPoincareSkeleton
#print PoincareConjecture.smoothPoincareSkeleton
#print axioms PoincareConjecture.smoothPoincareSkeleton
#check @IndependentAudit.intended
#print IndependentAudit.intended
#print axioms IndependentAudit.intended

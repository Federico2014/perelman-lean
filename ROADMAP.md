# Proof implementation and verification scope

The main project implements the full topological target through a fixed upstream
geometric proof. `import Perelman` exposes `Perelman.poincareConjecture`.
The default build imports `Completion`, which requires that theorem to have exactly
`Perelman.PoincareConjecture` as its universe-polymorphic type and permits only
`propext`, `Classical.choice`, and `Quot.sound` in its transitive axiom closure.

| Stage | Implementation | Verification status |
| --- | --- | --- |
| Standard topological target | `Perelman/Statement.lean` | Definition preserved |
| Smoothing, Ricci flow, surgery, finite extinction and reconstruction | FrenzyMath at `62db01af9388dc1d9b56b66d6674f4c09b2318a2` | Complete local source verification pending |
| Second countability and homeomorphism | `Perelman.nonempty_homeomorph_three_sphere` | Local target check pending |
| Closed full target | `Perelman.poincareConjecture` | Full-target axiom and kernel checks pending |
| Default completeness gate | `Completion.lean` using `CompletionPolicy.lean` | Required by the main project |
| Independent statement and source checks | `scripts/upstream_audit/` | Complete run pending |

The upstream authors supply the geometric proof. This repository contributes the
integration, exact shared target and adapter, independent statement checks and
verification harness. See [the source map](full-proof/PROVENANCE.md). An older
verification result applies only to the revision and checking scope it recorded.

## Separate local analytic development

The local analytic modules retain comparison, slope normalization, finite jump-error
bounds and a homeomorphism construction from a supplied spherical covering.
Those modules are not dependencies of the imported geometric proof. Their historical
successful logs do not verify the full target.

A separate geometric proof based on those analytic lemmas would still need actual
Riemannian metrics and flows, geometric area invariants and their evolution/surgery
estimates, finite extinction and reconstruction of the original manifold. These
are obligations for that separate implementation, rather than assumptions added to
`Perelman.poincareConjecture`.

## Acceptance

Preserve the original topological statement and its full quantifier range. Require
a closed theorem without a conjecture or geometric-service hypothesis. Complete a
pinned source build, explicit target checks, transitive axiom audits and the named
kernel replays. Record the exact revision and actual checking scope before describing
the integration as verified. Run new CI after the requested local verification.

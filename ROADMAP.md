# Dependencies and acceptance criteria for a complete formalization

The current contribution is partial real analysis and conditional covering-space topology. It is not a complete proof
of the Poincare conjecture. The stages below require further decomposition and
an audit of reusable foundations in the pinned mathlib revision.

This table describes the root project's locally implemented stages. A separate
`full-proof/` candidate now imports a pinned external proof; it is undergoing its
own source, target, and kernel checks. No external stage is counted as independently
verified by the root project's earlier successful build.

| Stage | Required objects and theorems | Dependencies | Status |
| --- | --- | --- | --- |
| Target statement | Compact, Hausdorff, simply connected topological three-manifolds without boundary are homeomorphic to the standard three-sphere | Manifolds and the fundamental groupoid | Definition only |
| Geometric starting point | Smoothing, orientability, existence of a Riemannian metric, and passage back to a topological conclusion | Three-dimensional topology and differential geometry | Missing |
| Ricci flow | Time-dependent metrics, Ricci tensor, flow equation, short-time existence, continuation | Tensors, connections, curvature, parabolic PDE | Missing |
| Scalar curvature | Evolution equation, maximum principle, `R_min(t) >= -3/(2(t+C))` | Ricci flow | Missing |
| Singularities and surgery | Entropy, reduced volume, noncollapsing, canonical neighborhoods, necks and caps, existence and time control of surgery flows | Ricci flow and geometric analysis | Missing |
| Area invariant | Relative loop-space homotopy classes, existence of a nontrivial class, min-max disk area, positivity | Homotopy theory and minimal surfaces | Missing |
| Geometric area evolution | Area variation, Gauss-Bonnet, curve shortening and regularization, forward upper slope estimates | Area invariant and Ricci flow | Missing |
| Surgery estimates | Distance and area control, tracking homotopy classes, approximation errors and surgery times | Surgery and the area invariant | Missing |
| Analytic normalization | Normalize a forward upper slope estimate without differentiability | Supplied scalar-curvature and area inequalities | Proved |
| Analytic comparison | Logarithmic comparison and explicit obstruction time | Supplied continuous real-valued profiles | Proved |
| Analytic jump errors | Finite-piece comparison with cumulative additive jump errors and an explicit lifespan bound | Supplied finite partition and error budget | Proved |
| Geometric extinction | Apply analytic comparison to actual invariants to exclude surviving components | The preceding geometric and analytic stages | Missing |
| Covering-space conclusion | A supplied connected covering of a simply connected space is a homeomorphism; specialize to a supplied spherical covering | Covering-space lifting theory | Proved |
| Geometric/topological bridge | Reverse surgery topology and construct a spherical covering, or an equivalent classification adequate for the target manifolds | Three-dimensional topology and geometric extinction | Missing |
| Main theorem | Prove `Perelman.PoincareConjecture` without extra geometric assumptions | All stages | Missing |

The opt-in `--require-complete` verification mode currently fails because this
main theorem is absent. Its negative tests also reject a theorem that proves the
target only by assuming that same target. This gate does not fill any mathematical
gap or replace independent review of the statement.

## Boundaries of the current results

`area_rate_bound` takes two numerical inequalities as input. It does not prove
that any geometric flow satisfies either inequality.

`normalized_area_forwardSlopeBound` uses a right derivative. Its extension
`normalized_area_forwardSlopeBound_of_slope` uses only a forward upper slope
estimate. Thus the new analytic normalization step does not require the geometric
area invariant to be differentiable. Constructing that invariant and proving its
upper slope estimate remain separate obligations.

`logarithmic_comparison_on` assumes continuity. The geometric invariant's
continuity on each smooth time interval has not been established here.

`logarithmic_comparison_with_jump_errors` allows finite pieces and a supplied
additive error for each jump. `piecewise_lifespan_lt_obstructionTime` bounds the
terminal time when the terminal value is nonnegative and the cumulative error
has a supplied budget. Neither theorem constructs a finite partition of surgery
times or converts approximate Lipschitz control into a bounded total additive error.
Disappearing components and possible accumulation of surgery times require
additional geometric arguments.

`no_global_area_profile` and `no_global_area_profile_of_slope` exclude global
functions satisfying their hypotheses. They do not prove that a particular flow
becomes extinct. This requires showing that a surviving geometric flow would
produce profiles with all the listed properties.

## Acceptance criteria for a complete proof

1. Preserve the genuine topological statement. Do not redefine a simply connected
   three-manifold to mean a sphere.
2. Provide a main theorem proving the target itself. Do not assume the conjecture
   or package all difficult claims into an uninstantiated hypothesis structure.
3. Prove the geometric stages in Lean and map them to precise references, with
   explicit dimensions, regularity, and boundary conditions.
4. Build in a fresh environment with pinned dependencies, and inspect transitive
   axiom dependencies of the public conclusions.
5. Obtain an independent statement-coverage review and mathematical review. Kernel
   acceptance alone cannot establish that an encoded statement matches the original problem.

Until these criteria are met, this repository remains a partial formalization.

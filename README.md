# Perelman Lean Foundations

**Partial formalization in progress. This repository does not prove the Poincare
conjecture or formally verify Perelman's complete proof.**

This Lean 4 / mathlib project formalizes real-analysis ingredients of Perelman's
finite-extinction argument and a conditional covering-space implication. Its area
functions have not been identified with geometric invariants of an actual Ricci
flow, and no spherical covering has been constructed for the target manifolds.
`PoincareConjecture` defines the target proposition; there is no theorem proving it.

## Formalized results

| File | Content | Status |
| --- | --- | --- |
| [Statement.lean](Perelman/Statement.lean) | A compact, Hausdorff, simply connected topological three-manifold without boundary is homeomorphic to the standard three-sphere | Target definition only |
| [Extinction.lean](Perelman/Extinction.lean) | Logarithmic comparison, an explicit obstruction time, finite downward jumps, and normalization of right-derivative estimates | Proved analytic statements |
| [UpperSlope.lean](Perelman/UpperSlope.lean) | Normalization of forward upper slope estimates, without differentiability assumptions on the area function | Proved analytic statements |
| [Piecewise.lean](Perelman/Piecewise.lean) | Comparison with cumulative jump errors and an explicit lifespan bound | Proved for a supplied finite partition and jump estimates |
| [Covering.lean](Perelman/Covering.lean) | Construct a homeomorphism from a connected covering of a simply connected space; specialize to a supplied three-sphere covering | Proved conditional topology; the covering itself is not constructed |
| [Audit.lean](Audit.lean) | Transitive axiom audit of declarations in namespace `Perelman` | Rejects local axioms and `sorryAx` |
| [Completion.lean](Completion.lean) | Opt-in gate requiring a theorem of the full target type, with no extra hypotheses | Currently rejects a claim of completeness |

## Mathematics and scope

The analytic argument follows [Perelman's third paper, Section 1.3](https://arxiv.org/html/math/0307245v1).
Suppose `C > 0` and a nonnegative function satisfies the **assumed** estimates

\[
A'(t)\le -2\pi-\tfrac12 R(t)A(t),\qquad
R(t)\ge -\frac{3}{2(t+C)}.
\]

The code proves the resulting inequalities

\[
A'(t)\le -2\pi+\frac{3A(t)}{4(t+C)},\qquad
\left(\frac{A(t)}{t+C}\right)'\le -\frac{2\pi}{t+C}.
\]

`UpperSlope.lean` also establishes this normalization directly for forward
upper difference-quotient bounds. It does not assume that `A` has a derivative.
The quotient normalization lemma itself does not require continuity; the subsequent
comparison theorem lists continuity separately.

For a continuous function `f` with forward upper slope bounded by `-k/(t+C)`,

\[
f(T)\le f(0)-k\bigl(\log(T+C)-\log C\bigr).
\]

If `k > 0` and `f(0) >= 0`, the right side is negative at

\[
T=C\left(\exp\left(\frac{f(0)}k+1\right)-1\right)>0.
\]

This excludes a nonnegative terminal value at that time. `ForwardSlopeBound`
expresses an upper bound using eventually bounded forward difference quotients,
without postulating a derivative or an attained extremum.

For finitely many continuous pieces `f_i` with jump errors `e_i`, the code proves

\[
f_n(t_n)\le f_0(t_0)+\sum_{i<n}e_i
-k\bigl(\log(t_n+C)-\log(t_0+C)\bigr).
\]

If `t_0 = 0`, `C > 0`, `k > 0`, the terminal value is nonnegative, the total error
is at most `E`, and `f_0(0)+E >= 0`, then

\[
t_n<C\left(\exp\left(\frac{f_0(0)+E}{k}+1\right)-1\right).
\]

This allows a supplied additive error budget. It does not derive additive errors
from a geometric `(1+xi)` Lipschitz estimate, prove local finiteness of surgeries,
or establish any geometric surgery inequality. A supplied finite partition is
an explicit hypothesis.

`Covering.lean` lifts the identity through a supplied covering map. Uniqueness of
lifts proves that the lift is a two-sided inverse, yielding an actual homeomorphism.
For a simply connected, locally path connected space `M`, a supplied covering map
`ThreeSphere -> M` therefore gives `M ≃ₜ ThreeSphere`. The difficult claim that every
target manifold admits such a covering has not been proved or added as an axiom.

## Reproduce

Pinned environment:

- Lean: `leanprover/lean4:v4.32.0`
- mathlib: `81a5d257c8e410db227a6665ed08f64fea08e997`
- Transitive dependencies: [lake-manifest.json](lake-manifest.json)

Install [elan](https://github.com/leanprover/elan), then run:

```sh
lake exe cache get
python3 verify.py --self-test
```

Fetching dependencies and their precompiled cache requires network access and disk
space. If necessary, run `lake update` first and check that the manifest has not
drifted. The verification script checks dependency revisions, re-elaborates all
local modules with warnings treated as errors, and runs the axiom audit.

`--self-test` additionally checks that the audit rejects a custom axiom, an unfinished
theorem, and an unfinished definition. The temporary probe files live under the
ignored `.lake/` directory and are deleted afterwards.

The self-tests also confirm that the completeness gate rejects a missing main
theorem and a conditional wrapper that merely assumes the target. To require a
complete proof explicitly, use:

```sh
python3 verify.py --require-complete
```

**This command currently exits with failure because the full theorem is missing.**
It expects a universe-polymorphic theorem named `Perelman.poincareConjecture` whose
type is exactly `Perelman.PoincareConjecture`, allowing only the three foundation
axioms listed below. A successful partial build is not a successful completeness
check. The gate checks the encoded target, so independent review of the target's
mathematical meaning is still required.

Standard Lake builds are also supported:

```sh
lake build
```

The initial ten-theorem baseline at commit
`846526f0798e0dcb36d9225bf3066e88ad5d9c7c` has its historical local transcript in
[verification.log](verification.log). Its 31 audited theorem declarations include
Lean-generated auxiliaries. Further modules extend that baseline; the historical
transcript is not evidence for subsequently added results.

Passing these checks verifies the local declarations, not the Poincare conjecture.
The only permitted transitive axioms are `propext`, `Classical.choice`, and
`Quot.sound`. Classical foundations do not substitute for missing geometric theorems.

## Remaining work for a complete proof

[ROADMAP.md](ROADMAP.md) records the dependency boundaries and acceptance criteria.
The missing work includes smooth structures and metrics on the target manifolds;
Ricci flow existence and curvature estimates; noncollapsing and canonical
neighborhoods; surgery construction; loop-space and minimal-disk area invariants;
their geometric evolution and surgery estimates; geometric finite extinction;
and the topological construction of `M ≃ₜ ThreeSphere`.

These gaps are not filled by axioms, unfinished terms, or an uninstantiated structure
that assumes the difficult conclusions. At the pinned mathlib revision, the
corresponding conjecture is still marked `proof_wanted`. No claim is made about
the absence of formalizations elsewhere.

## References and attribution

- Grisha Perelman, [The entropy formula for the Ricci flow and its geometric applications](https://arxiv.org/abs/math/0211159).
- Grisha Perelman, [Ricci flow with surgery on three-manifolds](https://arxiv.org/abs/math/0303109).
- Grisha Perelman, [Finite extinction time for the solutions to the Ricci flow on certain three-manifolds](https://arxiv.org/abs/math/0307245), Sections 1.2-1.4.
- John Morgan and Gang Tian, [Ricci Flow and the Poincare Conjecture](https://arxiv.org/abs/math/0607607), a mathematical exposition, not this project's machine proof.
- Junyan Xu, [mathlib's target statements](https://github.com/leanprover-community/mathlib4/blob/81a5d257c8e410db227a6665ed08f64fea08e997/Mathlib/Geometry/Manifold/PoincareConjecture.lean). This project uses the same hypotheses for the topological three-dimensional statement.

The initial code was written with Codex assistance. Mathematical results retain
their original attribution. This repository does not claim a complete formalization.
Code is licensed under [Apache-2.0](LICENSE); dependencies retain their own licenses
and author attributions.

# Perelman Lean Proof Integration

**Full-target implementation integrated; complete local verification pending.**

The main library now includes `Perelman.poincareConjecture`, whose type is exactly
`Perelman.PoincareConjecture`, for every universe. It applies the fixed FrenzyMath
geometric proof through [Perelman/Poincare.lean](Perelman/Poincare.lean).

Every compact, Hausdorff, simply connected topological three-manifold without
boundary is homeomorphic to the standard unit three-sphere in Euclidean four-space.
The [target definition](Perelman/Statement.lean) uses standard Mathlib types.
The adapter derives second countability from compactness and the Euclidean chart
model; it adds no smoothness, curvature, surgery-flow or conjecture hypothesis.

## Implementation

```lean
import Perelman

#check @Perelman.nonempty_homeomorph_three_sphere
#check @Perelman.poincareConjecture
#print axioms Perelman.poincareConjecture
```

The geometric proof belongs to the upstream contributors. Its source is pinned to
[FrenzyMath/PoincareConjecture at 62db01af](https://github.com/frenzymath/PoincareConjecture/tree/62db01af9388dc1d9b56b66d6674f4c09b2318a2).
The [source map](full-proof/PROVENANCE.md) records the geometric route, revisions,
and attribution. The local analytic modules remain a separate contribution; they
are not dependencies of the imported geometric proof.

| File | Role |
| --- | --- |
| [Perelman/Statement.lean](Perelman/Statement.lean) | Standard topological target definition |
| [Perelman/Poincare.lean](Perelman/Poincare.lean) | Full homeomorphism-existence theorem and closed full target |
| [Perelman.lean](Perelman.lean) | Main import surface, including the full target |
| [Audit.lean](Audit.lean) | Transitive axiom audit of the full target and local analytic results |
| [CompletionPolicy.lean](CompletionPolicy.lean) | Shared exact-type and permitted-axiom policy |
| [Completion.lean](Completion.lean) | Completeness gate required by the default build |
| [full-proof/](full-proof/README.md) | Compatibility project importing the same implementation |

## Local verification

Pinned inputs:

- Lean: `leanprover/lean4:v4.33.1`.
- Mathlib: `0df444a360eaa60ab8c11dca51a86af692955474`.
- Geometric proof: `62db01af9388dc1d9b56b66d6674f4c09b2318a2`.
- All transitive revisions: [lake-manifest.json](lake-manifest.json).

After installing the pinned toolchain and preparing dependencies:

```sh
lake exe cache get
lake build
python3 verify.py --self-test --require-complete
```

The first source build is large and can take many hours. Preserve the committed
dependency revisions when reproducing the project. The default build must check
the complete target, rather than succeed on only the local analytic ingredients.
The verification script explicitly rechecks local sources with warnings treated as
errors, audits the complete target, and tests rejection of custom axioms,
unfinished terms, a missing target and a circular conditional wrapper. The
`--require-complete` option additionally rechecks the full gate and replays the
adapter module with Lean's kernel.

Complete independent verification remains pending. The dedicated
[upstream workflow](.github/workflows/upstream-proof.yml) starts with no precompiled
candidate proof modules, builds the pinned original sources, checks the original
endpoints and an independently stated target, audits their transitive axioms,
replays the named endpoint modules and checks this integration's exact target.
Bounded continuation may reuse only that workflow's own source-build checkpoints.
A checkpoint or partial build is not a successful proof check.

Only `propext`, `Classical.choice`, and `Quot.sound` are permitted. The target gate
requires a theorem of exactly the full universe-polymorphic proposition and rejects
extra geometric or conjecture hypotheses. An imported declaration or an older
upstream verification record does not establish this integration's current status.
Kernel replay is per module; no independent external-checker result is claimed for
this integration before one has actually run.

## Local analytic contribution and history

[Extinction.lean](Perelman/Extinction.lean), [UpperSlope.lean](Perelman/UpperSlope.lean),
[Piecewise.lean](Perelman/Piecewise.lean), and [Covering.lean](Perelman/Covering.lean)
retain logarithmic comparison, slope normalization, finite jump-error bounds,
and a homeomorphism construction from a supplied spherical covering. Those
results assume supplied real-valued profiles or covering data. Implementing
another geometric proof based on those lemmas would be separate work.

The [historical scope and formulas](https://github.com/Federico2014/perelman-lean/blob/5c062780f15b2c2d921efca70fde3abf97377300/README.md)
describe the earlier partial project. [verification.log](verification.log) and
[verification-extension.log](verification-extension.log) concern their recorded
older commits, not the new full target. See [ROADMAP.md](ROADMAP.md) for current
implementation and acceptance boundaries.

The original mathematical argument is due to Hamilton and Perelman. The imported
formal geometric development belongs to its upstream contributors; this repository
adds the shared-target integration and verification harness. The initial local
analytic code was written with Codex assistance. Code is licensed under
[Apache-2.0](LICENSE); dependencies retain their source licenses and notices.

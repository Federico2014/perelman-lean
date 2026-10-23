# Full-target integration (verification pending)

This separate Lean 4.33.1 project integrates the proof in
`frenzymath/PoincareConjecture` at commit
`62db01af9388dc1d9b56b66d6674f4c09b2318a2`.

The upstream geometric proof belongs to its original authors. This project shares
`Perelman/Statement.lean` with the root project and supplies the second-countability
bridge needed to apply the upstream theorem to that exact target.
See the [pinned provenance and proof map](PROVENANCE.md) for the source route,
attribution, and the required verification scope.

This integration has not yet passed our complete independent verification.
The verification branch must pass the original source build, target checks,
axiom audit, kernel replay, and this integration's completeness gate before it
can be described as verified or merged as a completed proof.

From this directory, after installing the pinned toolchain and dependencies:

```sh
lake exe cache get
lake build
lake env lean FullAudit.lean
```

Dependencies retain their upstream licenses and attributions, including the
upstream `NOTICE` and `LICENSES` files. The root project's earlier partial-build
logs do not verify this separate project.

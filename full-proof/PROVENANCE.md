# Upstream provenance and proof map

**Verification pending.** This map records the inspected source interfaces. It
is not evidence that their complete transitive proofs have passed our checks.

The full geometric development is supplied by the upstream contributors. This
repository contributes the shared-target adapter and verification harness; it
does not claim authorship of the imported geometric proof.

## Fixed input

| Input | Revision |
| --- | --- |
| PoincareConjecture | `62db01af9388dc1d9b56b66d6674f4c09b2318a2` |
| Lean | `leanprover/lean4:v4.33.1` |
| mathlib | `0df444a360eaa60ab8c11dca51a86af692955474` |
| lean4export | `15f6055e299ad5b89345e533cc2192f4cc00f659` |
| Comparator | `3927ad383f208ae977c340a91c48ac9b497d2097` |

The complete dependency lock is [lake-manifest.json](lake-manifest.json).
The upstream README describes a Hamilton–Perelman proof following Morgan and
Tian. Its source modification record identifies the imported subject-organized
library and earlier contributions. Dependency source notices remain in the
upstream checkout; this integration does not replace their licensing terms.

- [Upstream README](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/README.md)
- [Source modification record](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/MODIFICATIONS.md)
- [Third-party notices](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/NOTICE)
- [Retained Apache license](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/LICENSES/Apache-2.0.txt)

## Route inspected in the source

| Stage | Pinned source | Interface or role |
| --- | --- | --- |
| Endpoint definitions | [Statement.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareConjecture/Statement.lean) | Standard smooth and topological statements; Euclidean unit three-sphere |
| Initial metric | [Existence.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Geometry/Riemannian/Normalization/Existence.lean) | Normalized metric on the original smooth manifold |
| Local Ricci flow | [ShortTime.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Geometry/RicciFlow/Local/ShortTime.lean) | Short-time flow construction |
| Global surgery flow | [Existence.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Geometry/RicciFlow/Surgery/Global/Existence.lean) | Global flow supplied to the final extinction argument |
| Finite extinction | [Assembly.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Geometry/RicciFlow/Extinction/Global/Assembly.lean) | m71ExtinctionFromCalibratedTheories |
| Reverse surgery topology | [Providers.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Surgery/Reconstruction/Providers.lean) | Reconstruction inputs from the actual flow and its extinction |
| Topological reduction | [Providers.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Surgery/Reduction/Providers.lean) | Reduction used to construct the smooth endpoint input |
| Smooth endpoint input | [Providers.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Poincare/Smooth/Providers.lean) | m75EndpointInputFromExtinction preserves the same flow |
| Compatible smoothing | [Compatible.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Smoothing/Compatible.lean) | m76CompatibleSmoothing for the topological endpoint |
| Concrete suppliers | [Providers.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Poincare/Final/Providers.lean) | m90SmoothEndpointInputs and m90EndpointPackageFromMilestones |
| Final assembly | [Main.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareLib/Topology/Manifold/Poincare/Final/Main.lean) | m90FinalAssemblyFromMilestones |
| Public wrappers | [Main.lean](https://github.com/frenzymath/PoincareConjecture/blob/62db01af9388dc1d9b56b66d6674f4c09b2318a2/PoincareConjecture/Proofs/Main.lean) | PoincareConjecture.topologicalPoincareSkeleton and smoothPoincareSkeleton |

The source supplies intermediate service structures internally in its endpoint
assembly. Merely finding such a structure or an adapter theorem would not prove
Poincare: our acceptance check requires a closed theorem of the complete target
and audits its transitive axiom dependencies.

## Adapter in this repository

[PerelmanFull.lean](PerelmanFull.lean) imports the upstream topological endpoint
and proves the shared `Perelman.PoincareConjecture` proposition. Its target uses
the standard mathlib manifold, simple-connectivity, compactness and homeomorphism
types. The upstream endpoint lists second countability; the adapter derives it
from compactness with `ChartedSpace.secondCountable_of_sigmaCompact`.

The root project's earlier analytic lemmas are a separate partial development.
They are not asserted to be dependencies of the imported complete proof.

## Required evidence

The dedicated workflow builds the original pinned source without author-supplied
proof caches, checks the original endpoints and an independent statement bridge,
audits all those conclusions, replays the named endpoint modules with Lean's
kernel, and builds this integration's complete-target gate. The last replay is
per module; it must not be described as a Nanoda run or a fresh replay of every
imported constant. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed.
All stages must succeed before this pending integration is described as verified.

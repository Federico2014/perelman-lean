import Perelman.Extinction

/-!
Forward upper slope estimates for the normalized area, without differentiability
assumptions. These are real-analysis results; their application to an actual Ricci
flow still requires a geometrically defined invariant and its evolution estimate.
-/

open Set Filter
open scoped Topology

namespace Perelman

/-- Increasing an upper slope bound preserves the bound. -/
theorem ForwardSlopeBound.mono {f : ℝ → ℝ} {t a b : ℝ}
    (h : ForwardSlopeBound f t a) (hab : a ≤ b) : ForwardSlopeBound f t b := by
  intro r hr
  exact h r (lt_of_le_of_lt hab hr)

/-- Division by the positive affine time factor preserves forward upper slope
control with the usual quotient formula. No derivative or continuity of `A` is
assumed: the identity for difference quotients is sufficient. -/
theorem forwardSlopeBound_div_time_shift {A : ℝ → ℝ} {t C bound : ℝ}
    (hpos : 0 < t + C) (hs : ForwardSlopeBound A t bound) :
    ForwardSlopeBound (fun s => A s / (s + C)) t
      ((bound * (t + C) - A t) / (t + C) ^ 2) := by
  intro r hr
  let L := (bound * (t + C) - A t) / (t + C) ^ 2
  let d := (r - L) * (t + C) / 2
  have hL : L < r := hr
  have hd : 0 < d := by dsimp [d]; positivity
  let g : ℝ → ℝ := fun z => ((bound + d) * (t + C) - A t) / ((z + C) * (t + C))
  have hgcont : ContinuousAt g t := by
    exact continuousAt_const.div
      ((continuousAt_id.add continuousAt_const).mul continuousAt_const)
      (mul_ne_zero hpos.ne' hpos.ne')
  have hmid : g t = L + (r - L) / 2 := by
    dsimp [g, d, L]
    field_simp
    ring
  have hgr : g t < r := by rw [hmid]; linarith
  have hg : ∀ᶠ z in 𝓝[>] t, g z < r :=
    (hgcont.tendsto.mono_left nhdsWithin_le_nhds) (Iio_mem_nhds hgr)
  filter_upwards [hs (bound + d) (by linarith), hg, self_mem_nhdsWithin]
    with z hz hgz htz
  have htz' : t < z := htz
  have hzpos : 0 < z + C := by linarith
  have hzt : z - t ≠ 0 := sub_ne_zero.mpr (ne_of_gt htz')
  have hidentity : slope (fun s => A s / (s + C)) t z =
      (slope A t z * (t + C) - A t) / ((z + C) * (t + C)) := by
    simp only [slope_def_field]
    field_simp
    ring
  rw [hidentity]
  apply lt_trans _ hgz
  exact div_lt_div_of_pos_right
    (sub_lt_sub_right (mul_lt_mul_of_pos_right hz hpos) _) (mul_pos hzpos hpos)

/-- The geometric area and scalar-curvature estimates imply the normalized
forward upper slope estimate, even when the area has no right derivative. -/
theorem normalized_area_forwardSlopeBound_of_slope {A : ℝ → ℝ} {t C scalar : ℝ}
    (hpos : 0 < t + C) (harea : 0 ≤ A t)
    (hs : ForwardSlopeBound A t (-2 * Real.pi - scalar * A t / 2))
    (hscalar : -(3 : ℝ) / (2 * (t + C)) ≤ scalar) :
    ForwardSlopeBound (fun s => A s / (s + C)) t (-2 * Real.pi / (t + C)) := by
  apply (forwardSlopeBound_div_time_shift hpos hs).mono
  exact rescaled_rate_bound hpos harea (area_rate_bound hpos harea hscalar le_rfl)

/-- No globally nonnegative continuous area profile can satisfy the specified
curvature and forward upper slope estimates. Differentiability is not required.
The estimates remain explicit hypotheses, not geometric theorems. -/
theorem no_global_area_profile_of_slope (A scalar : ℝ → ℝ) {C : ℝ}
    (hC : 0 < C) (harea : ∀ t ∈ Ici 0, 0 ≤ A t)
    (hcont : ContinuousOn A (Ici 0))
    (hscalar : ∀ t ∈ Ici 0, -(3 : ℝ) / (2 * (t + C)) ≤ scalar t)
    (hslope : ∀ t ∈ Ici 0,
      ForwardSlopeBound A t (-2 * Real.pi - scalar t * A t / 2)) : False := by
  let f : ℝ → ℝ := fun t => A t / (t + C)
  have hf0 : 0 ≤ f 0 := div_nonneg (harea 0 (by simp)) (by simpa using hC.le)
  let T := obstructionTime (f 0) C (2 * Real.pi)
  have hT : 0 < T := obstructionTime_pos hf0 hC (by positivity)
  apply no_nonnegative_on_obstruction_interval (f := f) (k := 2 * Real.pi)
    hC (by positivity) hf0
  · apply (hcont.mono (fun t ht => ht.1)).div
      (continuousOn_id.add continuousOn_const)
    intro t ht
    have : 0 < t + C := by linarith [ht.1]
    exact this.ne'
  · exact div_nonneg (harea T hT.le) (by linarith)
  · intro t ht
    simpa only [f, neg_mul] using
      normalized_area_forwardSlopeBound_of_slope (by linarith [ht.1]) (harea t ht.1)
        (hslope t ht.1) (hscalar t ht.1)

end Perelman

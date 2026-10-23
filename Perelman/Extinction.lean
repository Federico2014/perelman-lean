import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
Real-analysis ingredients of Perelman's finite-extinction argument
(arXiv:math/0307245v1, §1.3).

These results concern real-valued functions. They do NOT construct a Ricci flow,
define the geometric area invariant, establish its evolution estimate, or handle
surgery. In particular they do not prove the Poincaré conjecture.
-/

open Set Filter
open scoped Topology

namespace Perelman

/-- A forward upper slope bound, expressed without assuming differentiability.
For every number strictly above `b`, all sufficiently small forward difference
quotients are below that number. -/
def ForwardSlopeBound (f : ℝ → ℝ) (t b : ℝ) : Prop :=
  ∀ r : ℝ, b < r → ∀ᶠ z in 𝓝[>] t, slope f t z < r

/-- A positive time at which the logarithmic comparison function is negative.
The extra `1` makes the contradiction strict. -/
noncomputable def obstructionTime (initial C k : ℝ) : ℝ :=
  C * (Real.exp (initial / k + 1) - 1)

theorem obstructionTime_pos {initial C k : ℝ}
    (hi : 0 ≤ initial) (hC : 0 < C) (hk : 0 < k) :
    0 < obstructionTime initial C k := by
  apply mul_pos hC
  have h : 0 < initial / k + 1 := by positivity
  have := Real.exp_lt_exp.mpr h
  simpa using sub_pos.mpr (show 1 < Real.exp (initial / k + 1) by simpa using this)

/-- Integrating the forward slope estimate gives a logarithmic upper bound.
Continuity is an explicit hypothesis; discontinuities at surgeries require a
separate argument and are not hidden in this theorem. -/
theorem logarithmic_comparison_on {f : ℝ → ℝ} {a b C k : ℝ}
    (hab : a ≤ b) (hC : 0 < a + C)
    (hcont : ContinuousOn f (Icc a b))
    (hslope : ∀ t ∈ Ico a b, ForwardSlopeBound f t (-k / (t + C))) :
    f b ≤ f a - k * (Real.log (b + C) - Real.log (a + C)) := by
  let B : ℝ → ℝ := fun t => f a - k * (Real.log (t + C) - Real.log (a + C))
  have hBderiv : ∀ t ∈ Icc a b, HasDerivAt B (-k / (t + C)) t := by
    intro t ht
    have hpos : 0 < t + C := by linarith [ht.1]
    convert! (((hasDerivAt_id t).add_const C).log hpos.ne').sub_const (Real.log (a + C))
      |>.const_mul k |>.const_sub (f a) using 1
    simp [div_eq_mul_inv]
  apply image_le_of_liminf_slope_right_le_deriv_boundary hcont
      (B := B) (B' := fun t => -k / (t + C))
  · simp [B]
  · intro t ht
    exact (hBderiv t ht).continuousAt.continuousWithinAt
  · intro t ht
    exact (hBderiv t ⟨ht.1, ht.2.le⟩).hasDerivWithinAt
  · intro t ht r hr
    exact (hslope t ht r hr).frequently
  · exact ⟨hab, le_rfl⟩

/-- The comparison estimate starting at time zero. -/
theorem logarithmic_comparison {f : ℝ → ℝ} {T C k : ℝ}
    (hT : 0 ≤ T) (hC : 0 < C)
    (hcont : ContinuousOn f (Icc 0 T))
    (hslope : ∀ t ∈ Ico 0 T, ForwardSlopeBound f t (-k / (t + C))) :
    f T ≤ f 0 - k * (Real.log (T + C) - Real.log C) := by
  simpa using logarithmic_comparison_on hT (by simpa using hC) hcont hslope

/-- The same estimate survives finitely many downward jumps. The functions
`f i` describe consecutive continuous pieces; the jump inequality is supplied
explicitly. No claim about geometric surgery maps is made here. -/
theorem logarithmic_comparison_with_jumps (f : ℕ → ℝ → ℝ) (time : ℕ → ℝ)
    (C k : ℝ) (n : ℕ)
    (horder : ∀ i < n, time i ≤ time (i + 1))
    (hpos : ∀ i < n, 0 < time i + C)
    (hcont : ∀ i < n, ContinuousOn (f i) (Icc (time i) (time (i + 1))))
    (hslope : ∀ i < n, ∀ t ∈ Ico (time i) (time (i + 1)),
      ForwardSlopeBound (f i) t (-k / (t + C)))
    (hjump : ∀ i < n, f (i + 1) (time (i + 1)) ≤ f i (time (i + 1))) :
    f n (time n) ≤ f 0 (time 0) - k * (Real.log (time n + C) - Real.log (time 0 + C)) := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hp := ih (fun i hi => horder i (Nat.lt_succ_of_lt hi))
      (fun i hi => hpos i (Nat.lt_succ_of_lt hi)) (fun i hi => hcont i (Nat.lt_succ_of_lt hi))
      (fun i hi => hslope i (Nat.lt_succ_of_lt hi)) (fun i hi => hjump i (Nat.lt_succ_of_lt hi))
    have hl := logarithmic_comparison_on (horder n (Nat.lt_succ_self n))
      (hpos n (Nat.lt_succ_self n)) (hcont n (Nat.lt_succ_self n))
      (hslope n (Nat.lt_succ_self n))
    have hj := hjump n (Nat.lt_succ_self n)
    linarith

/-- A nonnegative continuous function cannot satisfy this decay estimate up to
the explicitly given time. This is an analytic obstruction, not a geometric
finite-extinction theorem. -/
theorem no_nonnegative_on_obstruction_interval {f : ℝ → ℝ} {C k : ℝ}
    (hC : 0 < C) (hk : 0 < k) (hi : 0 ≤ f 0)
    (hcont : ContinuousOn f (Icc 0 (obstructionTime (f 0) C k)))
    (hterminal : 0 ≤ f (obstructionTime (f 0) C k))
    (hslope : ∀ t ∈ Ico 0 (obstructionTime (f 0) C k),
      ForwardSlopeBound f t (-k / (t + C))) : False := by
  have hT := obstructionTime_pos hi hC hk
  have hbound := logarithmic_comparison hT.le hC hcont hslope
  have hshift : obstructionTime (f 0) C k + C = C * Real.exp (f 0 / k + 1) := by
    unfold obstructionTime
    ring
  rw [hshift, Real.log_mul hC.ne' (Real.exp_ne_zero _), Real.log_exp] at hbound
  have hcancel : k * (f 0 / k) = f 0 := by field_simp
  nlinarith

/-- Substitute the scalar-curvature lower bound into the area evolution estimate.
The geometric validity of both input inequalities remains a separate obligation. -/
theorem area_rate_bound {area scalar rate time C : ℝ}
    (hpos : 0 < time + C) (harea : 0 ≤ area)
    (hscalar : -(3 : ℝ) / (2 * (time + C)) ≤ scalar)
    (hrate : rate ≤ -2 * Real.pi - scalar * area / 2) :
    rate ≤ -2 * Real.pi + 3 * area / (4 * (time + C)) := by
  have hmul := mul_le_mul_of_nonneg_right hscalar harea
  have heq : (-(3 : ℝ) / (2 * (time + C))) * area / 2 =
      -(3 * area / (4 * (time + C))) := by field_simp; ring
  linarith

/-- Dividing the area by `time + C` yields the required decay estimate. -/
theorem rescaled_rate_bound {area rate time C : ℝ}
    (hpos : 0 < time + C) (harea : 0 ≤ area)
    (hrate : rate ≤ -2 * Real.pi + 3 * area / (4 * (time + C))) :
    (rate * (time + C) - area) / (time + C) ^ 2 ≤ -2 * Real.pi / (time + C) := by
  apply (div_le_iff₀ (sq_pos_of_pos hpos)).2
  have hmul := (mul_le_mul_iff_left₀ hpos).2 hrate
  have hcancel : (3 * area / (4 * (time + C))) * (time + C) = 3 * area / 4 := by
    field_simp
  have hright : (-2 * Real.pi / (time + C)) * (time + C) ^ 2 =
      -2 * Real.pi * (time + C) := by field_simp
  rw [hright]
  nlinarith

/-- A right derivative bounded above gives a forward upper slope bound. -/
theorem forwardSlopeBound_of_hasDerivWithinAt {f : ℝ → ℝ} {t rate bound : ℝ}
    (hd : HasDerivWithinAt f rate (Ici t) t) (hb : rate ≤ bound) :
    ForwardSlopeBound f t bound := by
  intro r hr
  exact hd.Ioi_of_Ici.limsup_slope_le' (lt_irrefl t) (lt_of_le_of_lt hb hr)

/-- Connect the area and curvature estimates to the forward slope estimate for
the normalized area. Only real analysis is proved; the geometric estimates
are hypotheses. -/
theorem normalized_area_forwardSlopeBound {A : ℝ → ℝ} {t C rate scalar : ℝ}
    (hpos : 0 < t + C) (harea : 0 ≤ A t)
    (hd : HasDerivWithinAt A rate (Ici t) t)
    (hscalar : -(3 : ℝ) / (2 * (t + C)) ≤ scalar)
    (hrate : rate ≤ -2 * Real.pi - scalar * A t / 2) :
    ForwardSlopeBound (fun s => A s / (s + C)) t (-2 * Real.pi / (t + C)) := by
  have hdiv : HasDerivWithinAt (fun s => A s / (s + C))
      ((rate * (t + C) - A t) / (t + C) ^ 2) (Ici t) t := by
    convert! hd.div ((hasDerivWithinAt_id t (Ici t)).add_const C) hpos.ne' using 1
    simp
  exact forwardSlopeBound_of_hasDerivWithinAt hdiv
    (rescaled_rate_bound hpos harea (area_rate_bound hpos harea hscalar hrate))

/-- No globally nonnegative continuous area profile can have right derivatives
and curvature satisfying the indicated estimates for all nonnegative times.
This does not identify any such profile with a Ricci flow invariant. -/
theorem no_global_area_profile (A rate scalar : ℝ → ℝ) {C : ℝ}
    (hC : 0 < C) (harea : ∀ t ∈ Ici 0, 0 ≤ A t)
    (hcont : ContinuousOn A (Ici 0))
    (hd : ∀ t ∈ Ici 0, HasDerivWithinAt A (rate t) (Ici t) t)
    (hscalar : ∀ t ∈ Ici 0, -(3 : ℝ) / (2 * (t + C)) ≤ scalar t)
    (hrate : ∀ t ∈ Ici 0, rate t ≤ -2 * Real.pi - scalar t * A t / 2) : False := by
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
      normalized_area_forwardSlopeBound (by linarith [ht.1]) (harea t ht.1)
        (hd t ht.1) (hscalar t ht.1) (hrate t ht.1)

end Perelman

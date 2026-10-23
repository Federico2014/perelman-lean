import Perelman.UpperSlope

/-!
Logarithmic comparison and lifespan bounds for finitely many continuous pieces
with a bounded total jump error. The existence of a finite partition and the
geometric jump estimates are not proved or assumed to hold automatically.
-/

open Set

namespace Perelman

/-- Comparison across finitely many jumps with an explicit cumulative error.
Individual errors need not have a sign; their total appears in the bound. -/
theorem logarithmic_comparison_with_jump_errors (f : ℕ → ℝ → ℝ)
    (time error : ℕ → ℝ) (C k : ℝ) (n : ℕ)
    (horder : ∀ i < n, time i ≤ time (i + 1))
    (hpos : ∀ i < n, 0 < time i + C)
    (hcont : ∀ i < n, ContinuousOn (f i) (Icc (time i) (time (i + 1))))
    (hslope : ∀ i < n, ∀ t ∈ Ico (time i) (time (i + 1)),
      ForwardSlopeBound (f i) t (-k / (t + C)))
    (hjump : ∀ i < n, f (i + 1) (time (i + 1)) ≤ f i (time (i + 1)) + error i) :
    f n (time n) ≤ f 0 (time 0) + ∑ i ∈ Finset.range n, error i -
      k * (Real.log (time n + C) - Real.log (time 0 + C)) := by
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
    rw [Finset.sum_range_succ]
    linarith

/-- A finite piecewise profile with a nonnegative terminal value must stop before
the explicit obstruction time, allowing a bounded total jump error. This is an
analytic lifespan bound, not a theorem constructing or classifying a Ricci flow. -/
theorem piecewise_lifespan_lt_obstructionTime (f : ℕ → ℝ → ℝ)
    (time error : ℕ → ℝ) {C k budget : ℝ} (n : ℕ)
    (hC : 0 < C) (hk : 0 < k)
    (hinitial : 0 ≤ f 0 (time 0) + budget) (hzero : time 0 = 0)
    (horder : ∀ i < n, time i ≤ time (i + 1))
    (hpos : ∀ i < n, 0 < time i + C)
    (hcont : ∀ i < n, ContinuousOn (f i) (Icc (time i) (time (i + 1))))
    (hslope : ∀ i < n, ∀ t ∈ Ico (time i) (time (i + 1)),
      ForwardSlopeBound (f i) t (-k / (t + C)))
    (hjump : ∀ i < n, f (i + 1) (time (i + 1)) ≤ f i (time (i + 1)) + error i)
    (hbudget : ∑ i ∈ Finset.range n, error i ≤ budget)
    (hterminal : 0 ≤ f n (time n)) :
    time n < obstructionTime (f 0 (time 0) + budget) C k := by
  let initial := f 0 (time 0) + budget
  let T := obstructionTime initial C k
  have hT : 0 < T := obstructionTime_pos hinitial hC hk
  by_contra hn
  have hend : T ≤ time n := le_of_not_gt hn
  have hlog := Real.log_le_log (by linarith : 0 < T + C)
    (by linarith : T + C ≤ time n + C)
  have hbound := logarithmic_comparison_with_jump_errors f time error C k n
    horder hpos hcont hslope hjump
  have hstart : Real.log (time 0 + C) = Real.log C := by rw [hzero, zero_add]
  rw [hstart] at hbound
  have hshift : T + C = C * Real.exp (initial / k + 1) := by
    dsimp [T, obstructionTime]
    ring
  rw [hshift, Real.log_mul hC.ne' (Real.exp_ne_zero _), Real.log_exp] at hlog
  have hcancel : k * (initial / k) = initial := by field_simp
  have hmul := mul_le_mul_of_nonneg_left hlog hk.le
  dsimp [initial] at hcancel
  nlinarith

end Perelman

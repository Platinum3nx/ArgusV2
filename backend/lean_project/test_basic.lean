-- Test without Mathlib: verify basic proofs work
-- This tests omega and rfl tactics

def deposit (balance : Int) (amount : Int) : Int :=
  if amount <= 0 then
    balance
  else
    let balance_safe := if balance < 0 then 0 else balance
    balance_safe + amount

theorem deposit_monotonic (balance amount : Int) : 
  deposit balance amount >= balance := by
  unfold deposit
  split_ifs
  case pos h => exact le_refl balance
  case neg h => omega

#check deposit_monotonic

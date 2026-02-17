import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.Linarith

def deposit (balance : Int) (amount : Int) : Int :=
  if amount ≤ 0 then balance
  else
    let balance_safe := if balance < 0 then 0 else balance
    (balance_safe + amount)

def withdraw (balance : Int) (amount : Int) (minimum_balance : Int) : Int :=
  if amount ≤ 0 then balance
  else
    let balance_safe := if balance < 0 then 0 else balance
    let minimum_balance_safe := if minimum_balance < 0 then 0 else minimum_balance
    let available := (balance_safe - minimum_balance_safe)
    let available_safe := if available < 0 then 0 else available
    if amount > available_safe then balance_safe
    else (balance_safe - amount)

theorem verify_safety (balance amount : Int) (h_bal : balance ≥ 0) : 
  deposit balance amount ≥ 0 := by
  unfold deposit
  split_ifs <;> omega

#check verify_safety

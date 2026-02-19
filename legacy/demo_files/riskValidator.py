"""
Risk Validator - Finance Demo.
Test Type: List & Array Validations

This file demonstrates Argus's new Dafny backend verifying logic that
inspects lists for specific conditions (counting, finding maximums).
"""

from typing import List

def count_risky_transactions(amounts: List[int], threshold: int) -> int:
    """
    Count how many transactions exceed the risk threshold.
    
    @requires: threshold >= 0
    @ensures: result >= 0
    
    Demonstrates: array traversal and conditional counting.
    Argus automatically proves that the count never becomes negative.
    """
    risk_count = 0
    for x in amounts:
        if x > threshold:
            risk_count = risk_count + 1
    return risk_count

def find_largest_deposit(transactions: List[int]) -> int:
    """
    Find the single largest deposit in a batch.
    
    @requires: True
    @ensures: result >= 0
    
    Demonstrates: finding a maximum value (reduction).
    Argus proves the result is non-negative, assuming we start at 0.
    """
    max_deposit = 0
    for tx in transactions:
        if tx > max_deposit:
            max_deposit = tx
    return max_deposit

def validate_batch_balance(balances: List[int], min_required: int) -> int:
    """
    Count how many accounts meet the minimum balance requirement.
    
    @requires: min_required >= 0
    @ensures: result >= 0
    
    Demonstrates: checking conditions against external parameters within a loop.
    """
    valid_accounts = 0
    for bal in balances:
        if bal >= min_required:
            valid_accounts = valid_accounts + 1
    return valid_accounts

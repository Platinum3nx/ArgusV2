"""
Currency Operations - Finance Demo.
Test Type: Arithmetic Safety

This file demonstrates Argus verifying currency conversion safety
where we must ensure that converting positive amounts results in
positive totals, preventing integer overflow or negative balances.
"""

from typing import List

def convert_currency_batch(amounts: List[int], rate: int) -> int:
    """
    Convert a batch of transaction amounts using a specific exchange rate.
    
    @requires: rate > 0
    @ensures: result >= 0
    
    Demonstrates: Multiplication safety in loops with preconditions.
    Argus proves that with a positive rate and positive amounts, 
    the total converted value remains non-negative.
    """
    total_converted = 0
    for amount in amounts:
        # Safety: Only convert valid, positive transactions
        if amount > 0:
            converted = amount * rate
            total_converted = total_converted + converted
    return total_converted

def calculate_exchange_fee(amounts: List[int], fee_per_tx: int) -> int:
    """
    Calculate the total exchange fees for a batch of transactions.
    
    @requires: fee_per_tx >= 0
    @ensures: result >= 0
    
    Demonstrates: Accumulation of a constant value based on list filtering.
    """
    total_fee = 0
    for amount in amounts:
        if amount > 0:
            total_fee = total_fee + fee_per_tx
    return total_fee

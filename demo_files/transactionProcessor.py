"""
Transaction Processor - Demo file with loops for Dafny verification.

This file demonstrates Argus's ability to verify loop-based code
using Dafny's formal verification capabilities.
"""

from typing import List


def sum_positive_transactions(transactions: List[int]) -> int:
    """
    Sum all positive transactions (deposits).
    
    @requires: True
    @ensures: result >= 0
    
    This function processes a list of transactions and sums only
    the positive ones (deposits). Negative values (withdrawals)
    are ignored.
    """
    total = 0
    for amount in transactions:
        if amount > 0:
            total = total + amount
    return total


def count_large_transactions(transactions: List[int], threshold: int) -> int:
    """
    Count transactions above a threshold.
    
    @requires: threshold >= 0
    @ensures: result >= 0
    
    This function counts how many transactions exceed a given
    threshold value.
    """
    count = 0
    for amount in transactions:
        if amount > threshold:
            count = count + 1
    return count


def find_max_transaction(transactions: List[int]) -> int:
    """
    Find the maximum transaction value.
    
    @requires: True
    @ensures: True
    
    Returns 0 if the list is empty.
    """
    max_val = 0
    for amount in transactions:
        if amount > max_val:
            max_val = amount
    return max_val


def apply_fee_to_all(transactions: List[int], fee: int) -> int:
    """
    Calculate total after applying a fee to each transaction.
    
    @requires: fee >= 0
    @ensures: result >= 0
    
    Each positive transaction has a fee deducted.
    """
    total = 0
    for amount in transactions:
        if amount > fee:
            total = total + (amount - fee)
    return total

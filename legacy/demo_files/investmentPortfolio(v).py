"""
Investment Portfolio Manager - Finance Demo.
Test Type: Loop-Based Aggregation + List & Array Validations

Simplified version using integer arrays instead of dictionaries
so Argus can verify the safety properties with Dafny.

Model:
- quantities[i] = number of shares for stock i
- prices[i] = current price per share for stock i
- costs[i] = average cost basis for stock i
"""

from typing import List


def calculate_portfolio_value(quantities: List[int], prices: List[int]) -> int:
    """
    Calculate total portfolio value from quantities and prices.
    
    @requires: True
    @ensures: result >= 0
    
    Assumes quantities and prices are parallel arrays of the same length.
    Only counts positive quantities with positive prices.
    """
    total_value = 0
    for i in range(len(quantities)):
        qty = quantities[i]
        price = prices[i]
        # Safety: only add if both are positive
        if qty > 0 and price > 0:
            total_value = total_value + (qty * price)
    return total_value


def calculate_total_gain(quantities: List[int], prices: List[int], costs: List[int]) -> int:
    """
    Calculate total unrealized gain/loss across portfolio.
    
    @requires: True
    @ensures: True
    
    Returns the sum of (current_price - cost_basis) * quantity for all positions.
    Note: Result can be negative (loss), so we don't ensure >= 0.
    """
    total_gain = 0
    for i in range(len(quantities)):
        qty = quantities[i]
        price = prices[i]
        cost = costs[i]
        if qty > 0:
            gain_per_share = price - cost
            total_gain = total_gain + (qty * gain_per_share)
    return total_gain


def count_profitable_positions(quantities: List[int], prices: List[int], costs: List[int]) -> int:
    """
    Count how many positions are currently profitable.
    
    @requires: True
    @ensures: result >= 0
    
    A position is profitable if current price > cost basis.
    """
    profitable_count = 0
    for i in range(len(quantities)):
        qty = quantities[i]
        price = prices[i]
        cost = costs[i]
        if qty > 0 and price > cost:
            profitable_count = profitable_count + 1
    return profitable_count


def sum_position_sizes(quantities: List[int]) -> int:
    """
    Get total number of shares across all positions.
    
    @requires: True
    @ensures: result >= 0
    
    Only counts positive quantities.
    """
    total_shares = 0
    for qty in quantities:
        if qty > 0:
            total_shares = total_shares + qty
    return total_shares


def calculate_dividend_income(quantities: List[int], dividends_per_share: List[int]) -> int:
    """
    Calculate expected dividend income from all positions.
    
    @requires: True
    @ensures: result >= 0
    
    dividends_per_share[i] = annual dividend per share for stock i (in cents).
    """
    total_dividends = 0
    for i in range(len(quantities)):
        qty = quantities[i]
        div = dividends_per_share[i]
        if qty > 0 and div > 0:
            total_dividends = total_dividends + (qty * div)
    return total_dividends

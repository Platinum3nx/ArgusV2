"""
Tax Utilities - Finance Demo.
Test Type: Deduction Logic

This file demonstrates safe tax calculation logic, ensuring that
calculated tax amounts do not violate basic financial invariants
(non-negative).
"""

from typing import List

def calculate_total_tax(incomes: List[int], tax_rate_percent: int) -> int:
    """
    Calculate the total tax for a list of incomes based on a flat rate.
    
    @requires: tax_rate_percent >= 0
    @requires: tax_rate_percent <= 100
    @ensures: result >= 0
    
    Demonstrates: Percentage calculations and bounds checking.
    Argus validates that the tax calculation (multiplication and division) 
    maintains non-negativity given positive inputs.
    """
    total_tax = 0
    for income in incomes:
        if income > 0:
            # Calculate tax: (income * rate) / 100
            tax = (income * tax_rate_percent) // 100
            total_tax = total_tax + tax
    return total_tax

def estimate_retained_income(incomes: List[int], fixed_tax: int) -> int:
    """
    Estimate total retained income after a fixed tax deduction per entry.
    
    @requires: fixed_tax >= 0
    @ensures: result >= 0
    
    Demonstrates: Subtraction with safety checks.
    """
    total_retained = 0
    for income in incomes:
        if income > fixed_tax:
            retained = income - fixed_tax
            total_retained = total_retained + retained
    return total_retained

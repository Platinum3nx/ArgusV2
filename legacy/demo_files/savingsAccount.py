"""
Savings Account Manager - Interest-Bearing Account Operations

This module handles savings account operations including deposits,
withdrawals, and interest calculations with proper validation.

SAFETY INVARIANTS:
1. Balance must always be >= 0
2. Withdrawals cannot exceed current balance
3. All amounts must be positive for valid transactions
4. Interest calculations must be non-negative
"""


def deposit(balance: int, amount: int) -> int:
    """
    Deposit money into the savings account.
    
    SAFETY INVARIANT: Amount must be positive. Balance cannot decrease.
    
    Args:
        balance: Current account balance in cents
        amount: Amount to deposit in cents
        
    Returns:
        New balance after deposit, or original balance if invalid
        
    Example:
        >>> deposit(1000, 500)
        1500
        >>> deposit(1000, -100)
        1000  # Rejected - negative amount
    """
    if amount <= 0:
        return balance  # Reject non-positive deposits
    if balance < 0:
        balance = 0  # Sanitize invalid state
    
    return balance + amount


def withdraw(balance: int, amount: int, minimum_balance: int) -> int:
    """
    Withdraw money from the savings account.
    
    SAFETY INVARIANT: Cannot withdraw more than available balance minus
    the minimum balance requirement. Amount must be positive.
    
    Args:
        balance: Current account balance in cents
        amount: Amount to withdraw in cents
        minimum_balance: Minimum balance that must be maintained
        
    Returns:
        New balance after withdrawal, or original balance if invalid
        
    Example:
        >>> withdraw(1000, 200, 100)
        800
        >>> withdraw(1000, 950, 100)
        1000  # Rejected - would go below minimum
    """
    if amount <= 0:
        return balance  # Reject non-positive withdrawals
    if balance < 0:
        balance = 0
    if minimum_balance < 0:
        minimum_balance = 0
    
    available = balance - minimum_balance
    if available < 0:
        available = 0
    
    if amount > available:
        return balance  # Reject - would violate minimum balance
    
    return balance - amount


def calculate_monthly_interest(balance: int, annual_rate_bps: int) -> int:
    """
    Calculate monthly interest earned on the balance.
    
    SAFETY INVARIANT: Interest must be non-negative.
    
    Args:
        balance: Current account balance in cents
        annual_rate_bps: Annual interest rate in basis points (100 = 1%)
        
    Returns:
        Interest earned for the month in cents
        
    Example:
        >>> calculate_monthly_interest(10000, 500)  # $100 at 5% APY
        41  # ~$0.41 monthly interest
    """
    if balance <= 0:
        return 0
    if annual_rate_bps <= 0:
        return 0
    
    # Monthly rate = annual rate / 12
    # Interest = balance * monthly_rate / 10000 (for basis points)
    monthly_interest = (balance * annual_rate_bps) // (12 * 10000)
    
    return monthly_interest


def apply_interest(balance: int, interest: int) -> int:
    """
    Apply earned interest to the account balance.
    
    SAFETY INVARIANT: Interest must be non-negative. Balance can only increase.
    
    Args:
        balance: Current account balance in cents
        interest: Interest amount to add in cents
        
    Returns:
        New balance with interest applied
    """
    if balance < 0:
        balance = 0
    if interest <= 0:
        return balance  # No interest to apply
    
    return balance + interest


def check_balance(balance: int) -> int:
    """
    Return the current balance, ensuring non-negative.
    
    Args:
        balance: Account balance value
        
    Returns:
        Balance if valid, 0 if negative
    """
    if balance < 0:
        return 0
    return balance


def can_withdraw(balance: int, amount: int, minimum_balance: int) -> bool:
    """
    Check if a withdrawal is allowed without actually performing it.
    
    Args:
        balance: Current account balance in cents
        amount: Proposed withdrawal amount in cents
        minimum_balance: Minimum balance requirement in cents
        
    Returns:
        True if withdrawal is permitted, False otherwise
    """
    if amount <= 0:
        return False
    if balance < 0:
        return False
    if minimum_balance < 0:
        minimum_balance = 0
    
    available = balance - minimum_balance
    return amount <= available

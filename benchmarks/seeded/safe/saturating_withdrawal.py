def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        return balance
    return balance - amount

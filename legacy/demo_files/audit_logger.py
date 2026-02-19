"""
Audit Logger - Finance Demo.
Test Type: Event Validation & Counting

This file demonstrates Argus verifying event logging logic, ensuring
that counts of specific security events are always non-negative.
"""

from typing import List

def count_high_value_events(events: List[int], threshold: int) -> int:
    """
    Count the number of events that exceed a certain value threshold.
    
    @requires: threshold >= 0
    @ensures: result >= 0
    
    Demonstrates: Conditional counting logic.
    Argus automatically proves that the counter starts at 0 and only increments,
    ensuring a non-negative result.
    """
    count = 0
    for value in events:
        if value > threshold:
            count = count + 1
    return count

def validate_event_sequence(events: List[int]) -> int:
    """
    Check that all events in a sequence are non-negative. 
    Returns 1 if valid, 0 otherwise.
    
    @requires: True
    @ensures: result == 0 or result == 1
    
    Demonstrates: Boolean-like validation logic using integers.
    """
    is_valid = 1
    for event in events:
        if event < 0:
            is_valid = 0
    return is_valid

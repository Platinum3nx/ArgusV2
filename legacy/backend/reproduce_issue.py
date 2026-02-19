
import re
import sys

def extract_counterexample(lean_output: str) -> dict:
    """
    Extract counterexample values from Lean proof comments.
    (Copied from backend/ci_runner.py)
    """
    counterexample = {}
    
    # Match lines like: -- Counterexample: var1 = val1, var2 = val2
    pattern = r'--\s*Counterexample[:\s]+(.+)'
    match = re.search(pattern, lean_output, re.IGNORECASE)
    
    if match:
        pairs_str = match.group(1)
        # Parse individual var = value pairs
        pair_pattern = r'(\w+)\s*=\s*([^\s,]+)'
        for var_match in re.finditer(pair_pattern, pairs_str):
            var_name = var_match.group(1)
            var_value = var_match.group(2)
            # Try to convert to int/float
            try:
                counterexample[var_name] = int(var_value)
            except ValueError:
                try:
                    counterexample[var_name] = float(var_value)
                except ValueError:
                    counterexample[var_name] = var_value
    
    return counterexample

def test_extraction(name, input_str, expected):
    result = extract_counterexample(input_str)
    if result == expected:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"  Input: {input_str}")
        print(f"  Got: {result}")
        print(f"  Exp: {expected}")

test_cases = [
    (
        "Simple Integers",
        "-- Counterexample: x = 1, y = 2",
        {"x": 1, "y": 2}
    ),
    (
        "Negative Integers",
        "-- Counterexample: x = -1, y = -100",
        {"x": -1, "y": -100}
    ),
    (
        "Floats",
        "-- Counterexample: temp = 98.6",
        {"temp": 98.6}
    ),
    (
        "With Text",
        "Some error here\n-- Counterexample: balance = 50\nMore text",
        {"balance": 50}
    ),
    (
         "Complex Value (fails with current regex)",
         "-- Counterexample: p = (1 : Nat)",
         {"p": "(1 : Nat)"} 
    ),
     (
         "Broken spacing",
         "--Counterexample: x=10,y=20",
         {"x": 10, "y": 20}
    )
]

for name, inp, exp in test_cases:
    test_extraction(name, inp, exp)

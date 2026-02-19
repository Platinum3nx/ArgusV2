from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# --- CONFIGURATION ---
MODEL_NAME = "gemini-3-pro-preview"

# --- PROMPTS ---

# 1. THEOREM GENERATOR PROMPT (Hybrid Approach)
# Functions are translated by AST parser (100% reliable).
# Gemini only generates the verification theorem.
THEOREM_PROMPT = """
You are given Lean 4 function definitions that were translated from Python.

Your task: Generate a theorem `verify_safety` that proves the main function's result is >= 0, assuming the starting balance is >= 0.

Rules:
1. Only assume starting balance is valid: `(h_bal : balance ≥ 0)`
2. Do NOT add extra hypotheses (like `amount <= balance`) - let the proof fail if the code is buggy
3. Use this tactic pattern: `unfold <function_name>; split_ifs <;> omega`

Example output:
```lean
theorem verify_safety (balance amount : Int) (h_bal : balance ≥ 0) : 
  withdraw balance amount ≥ 0 := by
  unfold withdraw
  split_ifs <;> omega
```

Output ONLY the theorem statement and proof. No markdown fences, no explanations.
"""

# 2. THE "NUCLEAR OPTION" PROMPT (Universal Solver)
# This script works for ANY logic that involves integers or control flow.
# It is not specific to wallets.
FIXER_PROMPT = """
Role: You are an automated proof generator. Output this exact Auto-Tactic script for every theorem.

Instructions:
1. Do NOT try to be clever.
2. Do NOT use `first`, `match`, or complex branching.
3. Just output the script below verbatim.

The Universal Script:
  unfold func_name
  split_ifs <;> omega

Alternative (if split_ifs fails):
  simp only [func_name]
  split_ifs
  all_goals omega

Goal: This script unfolds the function, splits all if-then-else branches with split_ifs, and solves linear arithmetic with omega.
Output: Return ONLY the fixed Lean code block with the corrected proof.
"""

TRIAGE_PROMPT = """Role: Senior Security Architect. Task: Identify the top 3 high-risk files. Output Format: Return ONLY the 3 filenames as a JSON list of strings."""

EXPLAIN_PROMPT = """You are a senior software engineer explaining a bug to a developer.

A formal verification tool (Lean 4) found a bug in this Python code. Your job is to explain:
1. What the bug is (in plain English)
2. Why it's dangerous
3. How to fix it

Be concise and practical. Use bullet points. Don't mention "Lean" or "theorem" - just explain the bug.

## Python Code
{python_code}

## Verification Error
{lean_error}

## Your Explanation
"""

# --- HELPER FUNCTIONS ---

def clean_response(text: str) -> str:
    """
    Removes Markdown code fences from the LLM response.
    """
    text = re.sub(r"^```[a-zA-Z]*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$", "", text, flags=re.MULTILINE)
    return text.strip()

def call_gemini(prompt_template: str, content: str) -> str:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "-- ARGUS_ERROR: GEMINI_API_KEY not found."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        
        user_content = f"{prompt_template}\n\nUser Input:\n{content}"
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }

        response = model.generate_content(user_content, safety_settings=safety_settings)

        if response.parts:
            return clean_response(response.text)
        else:
            return "-- ARGUS_ERROR: Empty response."

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return f"-- ARGUS_ERROR: {e}"

def triage_files(file_list: list[str]) -> list[str]:
    import json
    content = f"Files: {json.dumps(file_list)}\n\nIdentify top 3 high-risk files."
    response_text = call_gemini(TRIAGE_PROMPT, content)
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Error parsing triage: {response_text}")
        return []

def explain_error(python_code: str, lean_error: str) -> str:
    """
    Generate a plain English explanation for a Lean verification error.
    """
    try:
        content = f"Python Code:\n{python_code}\n\nVerification Error:\n{lean_error}"
        # We pass empty string as template because EXPLAIN_PROMPT already has placeholders
        # and we want to format it ourselves, but call_gemini appends content.
        # Let's adjust slightly:
        
        # Actually call_gemini does: f"{prompt_template}\n\nUser Input:\n{content}"
        # So we can just use a simple system prompt as template
        
        system_prompt = "You are a helpful code review assistant. Explain the bug concisely."
        user_input = EXPLAIN_PROMPT.format(python_code=python_code, lean_error=lean_error)
        
        return call_gemini(system_prompt, user_input)
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Could not generate explanation."

# --- MAIN AUDIT LOGIC ---

from . import lean_driver
from . import python_to_lean
from . import advanced_translator

# Import Dafny modules (may not be available in all environments)
try:
    from . import dafny_driver
    from . import python_to_dafny
    DAFNY_AVAILABLE = dafny_driver.check_dafny_available()
except ImportError:
    DAFNY_AVAILABLE = False
    dafny_driver = None
    python_to_dafny = None


def _has_loops(code: str) -> bool:
    """
    Detect if Python code contains loops (for/while).
    
    Code with loops should be verified with Dafny (better loop invariant support)
    rather than Lean (which requires induction proofs).
    """
    # Strip docstrings and comments
    code_stripped = re.sub(r'"""[\s\S]*?"""', '', code)
    code_stripped = re.sub(r"'''[\s\S]*?'''", '', code_stripped)
    code_stripped = re.sub(r'#.*$', '', code_stripped, flags=re.MULTILINE)
    
    loop_patterns = [
        r'\bfor\s+\w+\s+in\s+',      # for x in ...
        r'\bwhile\s+',                 # while ...
    ]
    
    for pattern in loop_patterns:
        if re.search(pattern, code_stripped):
            return True
    
    return False

def _is_complex_code(code: str) -> bool:
    """
    Detect if Python code requires the advanced (LLM-based) translator.
    
    Returns True if code contains ACTUAL code patterns (not just text in comments):
    - List type hints or operations
    - Set operations
    - Complex data structures
    - List comprehensions
    """
    # Step 1: Strip docstrings and comments to avoid false positives from prose
    # Remove triple-quoted strings (docstrings)
    code_stripped = re.sub(r'"""[\s\S]*?"""', '', code)
    code_stripped = re.sub(r"'''[\s\S]*?'''", '', code_stripped)
    # Remove single-line comments
    code_stripped = re.sub(r'#.*$', '', code_stripped, flags=re.MULTILINE)
    
    # Patterns that REQUIRE LLM translation (actual code constructs, not prose)
    # These are precise patterns that indicate complex data structures
    complex_patterns = [
        r'\bList\[',           # Type hints: List[int], List[str]
        r'\bSet\[',            # Set type hints
        r'\bDict\[',           # Dictionary type hints
        r'\bOptional\[',       # Optional type hints
        r'\bTuple\[',          # Tuple type hints
        r'\.append\s*\(',      # List append
        r'\.extend\s*\(',      # List extend
        r'\.remove\s*\(',      # List/set remove
        r'\.add\s*\(',         # Set add (method call, not math)
        r'\bfor\s+\w+\s+in\s+',  # For loops: "for x in items"
        r'\[\s*\w+\s+for\s+',    # List comprehensions: [x for x in ...]
        r'\bif\s+\w+\s+in\s+\w+',  # Membership: "if x in items" (not "in cents")
        r'\bsorted\s*\(',      # Sorted operations
        r'\bfilter\s*\(',      # Filter operations
        r'\bmap\s*\(',         # Map operations
    ]
    
    for pattern in complex_patterns:
        if re.search(pattern, code_stripped):
            return True
    
    return False


def audit_file(filename: str, code: str) -> dict:
    """
    Audits a single file using the appropriate verifier:
    
    1. Code with loops → Dafny (better loop invariant support)
    2. Code without loops → Lean (better for arithmetic)
    3. Complex code (lists, sets, no Dafny) → Gemini-powered Lean translator
    
    The neuro-symbolic approach ensures AI translations are mathematically verified.
    
    Returns a dictionary with the final status and details.
    """
    original_code = code
    logs = []
    
    # Check if code has loops and Dafny is available
    has_loops = _has_loops(code)
    
    if has_loops and DAFNY_AVAILABLE:
        # Route to Dafny for loop verification
        print(f"[{filename}] Detected loops - using Dafny verifier...")
        return audit_file_dafny(filename, code)
    
    # Otherwise, use Lean-based verification
    # Determine which Lean translator to use
    use_advanced = _is_complex_code(code)
    
    if use_advanced:
        # Use advanced Gemini-powered translator for complex code
        print(f"[{filename}] Step 1: Advanced translation (Complex Python → Lean)...")
        print(f"[{filename}] Detected: Lists, membership, or complex operations")
        lean_code = advanced_translator.translate_advanced(code)
        logs.append("Advanced (LLM-based) translation for complex code")
    else:
        # Use simple deterministic translator for basic arithmetic
        print(f"[{filename}] Step 1: Deterministic translation (Python → Lean)...")
        lean_code = python_to_lean.translate_with_theorem(code)
        logs.append("Deterministic translation completed (functions + theorem)")
    
    # Check for translation errors
    if lean_code.startswith("-- PARSE_ERROR") or lean_code.startswith("-- ERROR"):
        print(f"[{filename}] Translation error. Flagging as VULNERABLE.")
        return {
            "filename": filename,
            "status": "VULNERABLE",
            "verified": False,
            "proof": lean_code,
            "original_code": original_code,
            "fixed_code": None,
            "logs": ["Code could not be translated to Lean."]
        }
    
    # Step 2: Verification
    print(f"[{filename}] Step 2: Running Lean verification...")
    result = lean_driver.run_verification(lean_code)
    
    initial_verified = result["verified"]
    has_sorry = result.get("has_sorry", False)
    
    # If failed due to sorry, try tactic substitution
    if not initial_verified and has_sorry:
        print(f"[{filename}] Step 2b: Attempting tactic substitution (removing sorry)...")
        logs.append("Initial proof contained 'sorry', attempting tactic substitution")
        
        # Try common tactic replacements for sorry
        tactic_substitutions = [
            ("sorry", "decide"),
            ("sorry", "native_decide"),
            ("sorry", "trivial"),
            ("sorry", "rfl"),
            ("sorry", "simp"),
        ]
        
        for old_tactic, new_tactic in tactic_substitutions:
            modified_code = lean_code.replace(old_tactic, new_tactic)
            if modified_code != lean_code:
                print(f"[{filename}] Trying: {old_tactic} → {new_tactic}")
                retry_result = lean_driver.run_verification(modified_code)
                if retry_result["verified"]:
                    print(f"[{filename}] ✅ Tactic substitution succeeded: {new_tactic}")
                    logs.append(f"Tactic substitution succeeded: {old_tactic} → {new_tactic}")
                    result = retry_result
                    lean_code = modified_code
                    initial_verified = True
                    break
    
    logs.append(f"Verification: {'PASSED' if initial_verified else 'FAILED'}")
    
    if not initial_verified and result.get("error_message"):
        logs.append(f"Error: {result['error_message'][:100]}...")
    
    # Simple decision: proof passes = SECURE, proof fails = VULNERABLE
    # NO FIXER, NO RETRIES - this ensures buggy code stays VULNERABLE
    ui_status = "SECURE" if initial_verified else "VULNERABLE"
    
    print(f"[{filename}] Final status: {ui_status}")
    
    return {
        "filename": filename,
        "status": ui_status,
        "verified": initial_verified,
        "proof": lean_code,
        "error_message": result.get("error_message", ""),
        "original_code": original_code,
        "logs": logs
    }


def audit_file_dafny(filename: str, code: str) -> dict:
    """
    Audits a file using Dafny verification.
    
    Used for code with loops/arrays where Dafny's built-in
    loop invariant support is superior to Lean.
    
    Returns same structure as audit_file() for compatibility.
    """
    original_code = code
    logs = ["Using Dafny verifier (loop-based code detected)"]
    
    # Step 1: Translate Python to Dafny
    print(f"[{filename}] Step 1: Translating Python → Dafny...")
    dafny_code = python_to_dafny.translate_to_dafny(code)
    
    if dafny_code.startswith("// PARSE_ERROR"):
        print(f"[{filename}] Translation error. Flagging as VULNERABLE.")
        return {
            "filename": filename,
            "status": "VULNERABLE",
            "verified": False,
            "proof": dafny_code,
            "original_code": original_code,
            "fixed_code": None,
            "logs": ["Code could not be translated to Dafny."],
            "verifier": "dafny"
        }
    
    logs.append("Dafny translation completed")
    
    # Step 2: Run Dafny verification
    print(f"[{filename}] Step 2: Running Dafny verification...")
    result = dafny_driver.run_verification(dafny_code)
    
    verified = result["verified"]
    logs.append(f"Dafny verification: {'PASSED' if verified else 'FAILED'}")
    
    if not verified and result.get("error_message"):
        logs.append(f"Error: {result['error_message'][:200]}")
    
    ui_status = "SECURE" if verified else "VULNERABLE"
    
    print(f"[{filename}] Final status: {ui_status}")
    
    return {
        "filename": filename,
        "status": ui_status,
        "verified": verified,
        "proof": dafny_code,
        "error_message": result.get("error_message", ""),
        "original_code": original_code,
        "logs": logs,
        "verifier": "dafny"
    }
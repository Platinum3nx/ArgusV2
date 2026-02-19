"""
Lean 4 Verification Driver

This module handles running Lean 4 proofs for formal verification.
It creates temporary Lean files and runs them through the Lean compiler.

For CI (Docker): Uses the pre-configured Lean environment with Mathlib.
For Local Dev: Creates a standalone Lean file (no external dependencies needed for basic proofs).
"""

import subprocess
import os
import uuid
import tempfile
import re
from typing import Dict, Any


def _contains_sorry(lean_code: str) -> bool:
    """
    Check if the Lean code contains 'sorry' - an incomplete proof marker.
    
    In Lean 4, 'sorry' is a tactic that allows a proof to compile without
    actually proving anything. It's a "cheat code" that should
    NEVER appear in verified production code.
    
    Args:
        lean_code: The Lean 4 source code
        
    Returns:
        True if the code contains sorry in a proof context
    """
    # Remove single-line comments (-- ...)
    code_no_comments = re.sub(r'--.*$', '', lean_code, flags=re.MULTILINE)
    
    # Remove block comments (/- ... -/)
    code_no_comments = re.sub(r'/\-.*?\-/', '', code_no_comments, flags=re.DOTALL)
    
    # Remove string literals
    code_no_strings = re.sub(r'"[^"]*"', '', code_no_comments)
    
    # Check for 'sorry' as a word (not part of another word)
    if re.search(r'\bsorry\b', code_no_strings):
        return True
    
    return False


def _get_lean_project_path() -> str:
    """
    Get the path to the Lean project directory.
    
    In Docker (CI): Uses /app/lean_project (pre-configured with Mathlib)
    Locally: Uses backend/lean_project in the repo
    """
    # Check if we're in Docker (CI environment)
    docker_lean_path = "/app/lean_project"
    if os.path.exists(docker_lean_path) and os.path.isdir(docker_lean_path):
        return docker_lean_path
    
    # Check for local Lean project in backend folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_lean_path = os.path.join(base_dir, "backend", "lean_project")
    if os.path.exists(local_lean_path) and os.path.isdir(local_lean_path):
        return local_lean_path
    
    # Fallback: use temp directory (basic proofs only, no Mathlib)
    return tempfile.gettempdir()



def run_verification(lean_code: str) -> Dict[str, Any]:
    """
    Run Lean 4 verification on the provided code.
    
    Writes the code to a temporary .lean file, runs the Lean compiler,
    and returns the verification result.
    
    Args:
        lean_code: Complete Lean 4 source code to verify
        
    Returns:
        Dict with keys:
        - verified: bool - True if code compiles AND contains no 'sorry'
        - error_message: str - Full compiler output
        - distinct_errors: list - Parsed error messages
        - has_sorry: bool - Whether code contains 'sorry'
        - compiled: bool - Whether code compiled successfully
    """
    
    # Get the Lean project path
    lean_project_path = _get_lean_project_path()
    is_temp_dir = lean_project_path == tempfile.gettempdir()
    
    # Generate a unique filename
    file_id = str(uuid.uuid4())
    filename = f"verify_{file_id}.lean"
    file_path = os.path.join(lean_project_path, filename)

    try:
        # 1. Write the code to a temporary .lean file
        with open(file_path, "w") as f:
            f.write(lean_code)

        # 2. Run Lean compiler
        if is_temp_dir:
            # Standalone mode: run lean directly (no lake, no Mathlib)
            # This works for basic proofs that don't need Mathlib tactics
            cmd = ["lean", file_path]
            cwd = None
        else:
            # Project mode: use lake env to get Mathlib in scope
            cmd = ["lake", "env", "lean", filename]
            cwd = lean_project_path
        
        print(f"[Lean Driver] Running: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        stdout = process.stdout
        stderr = process.stderr
        return_code = process.returncode

        # 3. Process results
        compiled = (return_code == 0)
        
        # Log detailed output for debugging
        if not compiled:
            print(f"[Lean Driver] ❌ Compilation FAILED (exit code {return_code})")
            if stdout.strip():
                print(f"[Lean Driver] STDOUT:\n{stdout[:1000]}")  # Limit output
            if stderr.strip():
                print(f"[Lean Driver] STDERR:\n{stderr[:1000]}")
        else:
            print(f"[Lean Driver] ✅ Compilation succeeded")
        
        # CRITICAL: Check for 'sorry' - this skips proofs
        has_sorry = _contains_sorry(lean_code)
        
        if has_sorry:
            print("[Lean Driver] WARNING: Proof contains 'sorry' - marking as VULNERABLE")
        
        # Only SECURE if: compiles AND no sorry
        verified = compiled and not has_sorry
        
        full_output = (stdout + "\n" + stderr).strip()
        
        # Add sorry warning to error message if applicable
        if has_sorry and compiled:

            full_output = "WARNING: Proof uses 'sorry' (incomplete proof)\n\n" + full_output
        
        distinct_errors = []
        if not verified:
            if has_sorry:
                distinct_errors.append("Proof contains 'sorry' - incomplete proof detected")
            # Parse error lines
            error_lines = [line for line in full_output.splitlines() if line.strip() and "error:" in line.lower()]
            distinct_errors.extend(error_lines)
            if not distinct_errors:
                # Fallback if no explicit "error:" found but failed
                distinct_errors = [line for line in full_output.splitlines() if line.strip()][:5]

        return {
            "verified": verified,
            "error_message": full_output,
            "distinct_errors": distinct_errors,
            "has_sorry": has_sorry,
            "compiled": compiled
        }

    except subprocess.TimeoutExpired:
        return {
            "verified": False,
            "error_message": "Lean verification timed out after 60 seconds",
            "distinct_errors": ["Timeout: verification took too long"],
            "has_sorry": False,
            "compiled": False
        }
    except FileNotFoundError:
        return {
            "verified": False,
            "error_message": "Lean compiler not found. Install Lean 4 or run in Docker.",
            "distinct_errors": ["Lean not installed"],
            "has_sorry": False,
            "compiled": False
        }
    except Exception as e:
        return {
            "verified": False,
            "error_message": str(e),
            "distinct_errors": [str(e)],
            "has_sorry": False,
            "compiled": False
        }
    finally:
        # Cleanup: remove the temporary file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

"""
Dafny Verification Driver

This module handles running Dafny verification on translated code.
Similar interface to lean_driver.py for consistency.
"""

import subprocess
import os
import tempfile
import uuid
from typing import Optional


import shutil

def get_dafny_path() -> str:
    """
    Get the path to the Dafny executable.
    
    Checks PATH first, then common locations.
    """
    # 1. Check PATH (best for robust installs)
    if shutil.which("dafny"):
        return "dafny"

    # 2. Check common paths (fallback)
    paths_to_check = [
        "/opt/dafny/dafny",
        "/usr/local/bin/dafny",
    ]
    
    for path in paths_to_check:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
            
    return "dafny"  # Fallback


def run_verification(dafny_code: str, timeout: int = 120) -> dict:
    """
    Run Dafny verification on the provided code.
    
    Args:
        dafny_code: Complete Dafny program as a string
        timeout: Maximum time to wait for verification (seconds)
        
    Returns:
        dict with:
        - verified: bool - True if all assertions verified
        - error_message: str - Error details if verification failed
        - stdout: str - Raw Dafny output
        - dafny_file: str - Path to the temp file (for debugging)
    """
    # Create a unique temp file for this verification
    temp_dir = tempfile.gettempdir()
    file_id = str(uuid.uuid4())[:8]
    dafny_file = os.path.join(temp_dir, f"verify_{file_id}.dfy")
    
    try:
        # Write the Dafny code to temp file
        with open(dafny_file, "w") as f:
            f.write(dafny_code)
        
        dafny_path = get_dafny_path()
        
        # Run Dafny verification
        # --verify: Run the verifier
        # --allow-warnings: Don't fail on warnings
        cmd = [
            dafny_path,
            "verify",
            "--allow-warnings",
            dafny_file
        ]
        
        print(f"[Dafny Driver] Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=temp_dir
        )
        
        stdout = result.stdout
        stderr = result.stderr
        
        # Parse Dafny output
        # Success: "Dafny program verifier finished with X verified, 0 errors"
        # Failure: Contains "Error" or non-zero errors count
        
        verified = False
        error_message = ""
        
        if result.returncode == 0:
            # Check for verification success
            if "verified, 0 errors" in stdout or "0 errors" in stdout:
                verified = True
                print(f"[Dafny Driver] ✅ Verification succeeded")
            else:
                # Dafny returned 0 but might have verification failures
                error_message = stdout
                print(f"[Dafny Driver] ⚠️ Verification completed with issues")
        else:
            # Parse error from output
            error_message = stdout if stdout else stderr
            print(f"[Dafny Driver] ❌ Verification FAILED (exit code {result.returncode})")
        
        # Look for specific error patterns
        if "Error:" in stdout or "Error:" in stderr:
            verified = False
            # Extract error lines
            all_output = stdout + "\n" + stderr
            error_lines = [line for line in all_output.split("\n") if "Error" in line or "error" in line.lower()]
            error_message = "\n".join(error_lines[:5])  # First 5 error lines
        
        if stdout:
            print(f"[Dafny Driver] STDOUT:\n{stdout[:500]}")
        
        return {
            "verified": verified,
            "error_message": error_message,
            "stdout": stdout,
            "stderr": stderr,
            "dafny_file": dafny_file,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"[Dafny Driver] ❌ Verification TIMEOUT after {timeout}s")
        return {
            "verified": False,
            "error_message": f"Verification timed out after {timeout} seconds",
            "stdout": "",
            "stderr": "",
            "dafny_file": dafny_file,
            "exit_code": -1
        }
    except Exception as e:
        print(f"[Dafny Driver] ❌ Error: {e}")
        return {
            "verified": False,
            "error_message": str(e),
            "stdout": "",
            "stderr": "",
            "dafny_file": dafny_file,
            "exit_code": -1
        }
    finally:
        # Optionally clean up temp file
        # For now, keep it for debugging
        pass


def check_dafny_available() -> bool:
    """Check if Dafny is installed and available."""
    try:
        dafny_path = get_dafny_path()
        result = subprocess.run(
            [dafny_path, "--version"],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()
            print(f"[Dafny Driver] Dafny available: {version}")
            return True
    except Exception as e:
        print(f"[Dafny Driver] Dafny not available: {e}")
    return False


# Simple test
if __name__ == "__main__":
    # Test with a simple Dafny program
    test_code = """
method Deposit(balance: int, amount: int) returns (result: int)
  requires balance >= 0
  requires amount >= 0
  ensures result >= 0
{
  result := balance + amount;
}
"""
    
    if check_dafny_available():
        result = run_verification(test_code)
        print(f"Verified: {result['verified']}")
        if not result['verified']:
            print(f"Error: {result['error_message']}")
    else:
        print("Dafny not installed - skipping test")

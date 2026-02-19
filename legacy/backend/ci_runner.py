#!/usr/bin/env python3
"""
Argus CI Runner - Main orchestrator for the audit workflow.

Integrates the Neuro-Symbolic Repair Loop:
1. Audit files using deterministic translation + Lean verification
2. If VULNERABLE, attempt AI-powered repair using Gemini
3. Verify the fix to ensure it actually passes
4. Generate comprehensive report
5. Create auto-remediation PR with verified fixes
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from backend import repo_manager
from backend import agents
from backend.ai_repair import generate_fix
from backend.github_service import GitHubService
from backend.secrets_scanner import scan_repo, format_findings_for_report
from backend.sarif_generator import generate_sarif


def extract_counterexample(lean_output: str) -> dict:
    """
    Extract counterexample values from Lean proof comments.
    
    Looks for patterns like:
    -- Counterexample: current_balance = 900, charge_amount = 200, credit_limit = 1000
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


def extract_error_explanation(lean_output: str, error_message: str = "", ai_explanation: str = "") -> str:
    """
    Extract the human-readable error explanation.
    
    Priority:
    1. AI-generated explanation (if available)
    2. Lean compiler error messages (sanitized)
    3. Lines starting with '--' comments
    """
    # 1. Prefer AI explanation if available
    if ai_explanation and len(ai_explanation) > 10:
        return ai_explanation

    # 2. Extract meaningful error from compiler output & sanitize
    if error_message:
        # Clean up temporary filenames (verify_UUID.lean)
        cleaned_msg = re.sub(r'verify_[a-f0-9-]+\.lean:\d+:\d+:', '', error_message)
        
        error_lines = []
        for line in cleaned_msg.split('\n'):
            stripped = line.strip()
            if 'error:' in stripped.lower():
                parts = stripped.split('error:', 1)
                if len(parts) > 1:
                    error_lines.append(parts[1].strip())
                else:
                    error_lines.append(stripped)
            elif 'unsolved goals' in stripped.lower():
                error_lines.append("Proof failed: safety invariant could not be proven")
            elif 'omega' in stripped.lower() and 'could not prove' in stripped.lower():
                error_lines.append("Arithmetic check failed (possible overflow/underflow)")
        
        if error_lines:
            return ' | '.join(error_lines[:3])
    
    # 3. Fallback: look for comment explanations
    explanations = []
    for line in lean_output.split('\n'):
        if line.strip().startswith('--') and 'counterexample' not in line.lower():
            explanation = line.strip()[2:].strip()
            if len(explanation) > 10:
                explanations.append(explanation)
    
    if explanations:
        return ' '.join(explanations)
    
    return "Formal verification failed - safety conditions not met."


def generate_json_report(results: list, secrets_findings: list, repo_name: str = None, unaudited_files: list = None) -> dict:
    """
    Generate a rich JSON report for the frontend dashboard.
    
    This is MORE detailed than SARIF and designed for our custom UI.
    """
    summary = {
        "audited": len(results),
        "secure": sum(1 for r in results if r["status"] == "SECURE"),
        "vulnerable": sum(1 for r in results if r["status"] == "VULNERABLE"),
        "patched": sum(1 for r in results if r["status"] == "AUTO_PATCHED"),
        "secrets": len(secrets_findings) if secrets_findings else 0,
        "unaudited": len(unaudited_files) if unaudited_files else 0
    }
    
    files = []
    for r in results:
        lean_proof = r.get("proof", "")
        
        file_entry = {
            "filename": r["filename"],
            "status": r["status"],
            "original_code": r.get("original_code", ""),
            "lean_proof": lean_proof,
            "error_explanation": extract_error_explanation(lean_proof, r.get("error_message", ""), r.get("ai_explanation", "")) if r["status"] == "VULNERABLE" else None,
            "counterexample": extract_counterexample(lean_proof) if r["status"] == "VULNERABLE" else None,
            "suggested_fix": r.get("suggested_fix") or r.get("fixed_code"),
            "fix_verified": r["status"] == "AUTO_PATCHED"
        }
        files.append(file_entry)
    
    # Add secrets as file entries too
    if secrets_findings:
        for secret in secrets_findings:
            files.append({
                "filename": secret.file_path,
                "status": "SECRET_DETECTED",
                "secret_type": secret.secret_type,
                "line_number": secret.line_number,
                "severity": secret.severity,
                "description": secret.description
            })
    
    # Add unaudited files
    if unaudited_files:
        for filename in unaudited_files:
            files.append({
                "filename": filename,
                "status": "UNAUDITED",
                "reason": "File unchanged in this commit"
            })
    
    report = {
        "tool": "Argus",
        "version": "1.0.0",
        "repo": repo_name or os.getenv("GITHUB_REPOSITORY", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "files": files
    }
    
    return report


def attempt_repair(filename: str, original_code: str, lean_error: str, repo_path: str) -> dict:
    """
    Attempt to repair vulnerable code using Gemini with retries.
    
    The LLM may generate fixes that don't verify on the first attempt,
    but retrying increases success rate since different attempts may
    use different fix strategies.
    
    Args:
        filename: Original filename
        original_code: The vulnerable Python code
        lean_error: The Lean error message explaining why verification failed
        repo_path: Path to the repository
        
    Returns:
        Dictionary with repair results
    """
    MAX_REPAIR_ATTEMPTS = 5
    
    print(f"[{filename}] Attempting AI-powered repair (max {MAX_REPAIR_ATTEMPTS} attempts)...")
    
    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        print(f"[{filename}] Repair attempt {attempt}/{MAX_REPAIR_ATTEMPTS}...")
        
        try:
            # Generate fix using Gemini
            fixed_code = generate_fix(original_code, lean_error)
            
            if not fixed_code or len(fixed_code.strip()) < 10:
                print(f"[{filename}] Attempt {attempt}: AI returned empty or invalid fix")
                continue  # Try again
            
            # Save the fixed code to a new file
            base_name = os.path.splitext(filename)[0]
            fixed_filename = f"{base_name}_fixed.py"
            fixed_path = os.path.join(repo_path, fixed_filename)
            
            with open(fixed_path, "w") as f:
                f.write(fixed_code)
            print(f"[{filename}] Attempt {attempt}: Fixed code saved to {fixed_filename}")
            
            # Verify the fix
            print(f"[{filename}] Attempt {attempt}: Verifying the AI-generated fix...")
            fix_result = agents.audit_file(fixed_filename, fixed_code)
            
            if fix_result["verified"]:
                print(f"[{filename}] ✅ AI fix PASSED verification on attempt {attempt}!")
                return {
                    "attempted": True,
                    "success": True,
                    "attempts": attempt,
                    "reason": f"AI-generated fix passed formal verification (attempt {attempt})",
                    "fixed_code": fixed_code,
                    "fixed_filename": fixed_filename,
                    "fixed_proof": fix_result.get("proof")
                }
            else:
                print(f"[{filename}] Attempt {attempt}: Fix failed verification, trying again...")
                # Store the last failed fix in case all attempts fail
                last_failed_fix = fixed_code
                last_failed_proof = fix_result.get("proof")
                
        except Exception as e:
            print(f"[{filename}] Attempt {attempt} error: {e}")
            continue  # Try again
    
    # All attempts failed
    print(f"[{filename}] ❌ AI fix FAILED verification after {MAX_REPAIR_ATTEMPTS} attempts")
    return {
        "attempted": True,
        "success": False,
        "attempts": MAX_REPAIR_ATTEMPTS,
        "reason": f"AI-generated fix failed formal verification after {MAX_REPAIR_ATTEMPTS} attempts",
        "fixed_code": last_failed_fix if 'last_failed_fix' in dir() else None,
        "fixed_filename": fixed_filename if 'fixed_filename' in dir() else None,
        "fixed_proof": last_failed_proof if 'last_failed_proof' in dir() else None
    }


def generate_report(results: list, secrets_findings: list = None, unaudited_files: list = None) -> int:
    """
    Generates a Markdown report and writes it to Argus_Audit_Report.md
    and GITHUB_STEP_SUMMARY if available.
    Returns 1 if any file failed verification (and repair) or secrets found, 0 otherwise.
    """
    report_lines = ["# Argus AI Audit Report", "", "## Summary"]
    
    audited_count = len(results)
    secure = sum(1 for r in results if r["status"] == "SECURE")
    patched = sum(1 for r in results if r["status"] == "AUTO_PATCHED")
    vulnerable = sum(1 for r in results if r["status"] == "VULNERABLE")
    unaudited_count = len(unaudited_files) if unaudited_files else 0
    
    report_lines.append(f"- **Files Audited:** {audited_count} (changed in this commit)")
    report_lines.append(f"- **✅ Secure:** {secure}")
    report_lines.append(f"- **🔧 Auto-Patched:** {patched}")
    report_lines.append(f"- **❌ Vulnerable:** {vulnerable}")
    report_lines.append(f"- **⏭️ Unaudited (unchanged):** {unaudited_count}")
    report_lines.append("")
    
    # Only fail if there are truly unfixed vulnerabilities or HIGH severity secrets
    high_secrets = [f for f in (secrets_findings or []) if f.severity == "HIGH"]
    has_failure = vulnerable > 0 or len(high_secrets) > 0
    
    # Add secrets summary if any found
    if secrets_findings:
        report_lines.append(f"- **🔐 Secrets Detected:** {len(secrets_findings)}")
    
    report_lines.append("")
    
    # Add secrets section first if any found
    if secrets_findings:
        report_lines.append(format_findings_for_report(secrets_findings))
    
    report_lines.append("## Code Verification Details")
    
    for r in results:
        icon = "✅"
        if r["status"] == "AUTO_PATCHED":
            icon = "🔧"
        elif r["status"] == "VULNERABLE":
            icon = "❌"
            
        report_lines.append(f"### {icon} {r['filename']}")
        report_lines.append(f"**Status:** {r['status']}")
        
        # Show original issue for AUTO_PATCHED files (what was wrong before the fix)
        if r["status"] == "AUTO_PATCHED" and r.get("original_issue"):
            original = r["original_issue"]
            report_lines.append("\n#### 🔍 Original Issue (Fixed)")
            report_lines.append(f"> {original.get('error_summary', 'Verification failed')}")
            
            if original.get("counterexample"):
                report_lines.append("\n**Counterexample (before fix):**")
                report_lines.append("| Variable | Value |")
                report_lines.append("|----------|-------|")
                for var, val in original["counterexample"].items():
                    report_lines.append(f"| `{var}` | {val} |")
                report_lines.append("")
        
        # Show "Why is this Vulnerable?" for files that remain unfixed
        if r["status"] == "VULNERABLE":
            proof = r.get("proof", "")
            error_msg = r.get("error_message", "")
            ai_expl = r.get("ai_explanation", "")
            explanation = extract_error_explanation(proof, error_msg, ai_expl)
            counterexample = extract_counterexample(proof)
            
            report_lines.append("\n#### ⚠️ Why is this Vulnerable?")
            report_lines.append(f"> {explanation}")
            
            # Show counterexample as a table if available
            if counterexample:
                report_lines.append("\n**Counterexample Found:**")
                report_lines.append("| Variable | Value |")
                report_lines.append("|----------|-------|")
                for var, val in counterexample.items():
                    report_lines.append(f"| `{var}` | {val} |")
                report_lines.append("")
        
        # Show repair attempt info
        if r.get("repair_attempt"):
            repair = r["repair_attempt"]
            if repair.get("attempted"):
                if repair.get("success"):
                    report_lines.append(f"\n**🔧 Repair Attempt:** SUCCESS")
                    report_lines.append(f"- Fixed file: `{repair.get('fixed_filename')}`")
                else:
                    report_lines.append(f"\n**🔧 Repair Attempt:** FAILED")
                    report_lines.append(f"- Reason: {repair.get('reason')}")
        
        # Show fixed code for auto-patched files
        if r["status"] == "AUTO_PATCHED" and r.get("fixed_code"):
            report_lines.append("\n<details><summary>View Fix</summary>\n")
            report_lines.append("```python")
            report_lines.append(r["fixed_code"])
            report_lines.append("```\n</details>\n")

        # Show the formal proof
        if r.get("proof"):
            report_lines.append("\n<details><summary>View Formal Proof (Lean 4)</summary>\n")
            report_lines.append("```lean")
            report_lines.append(r["proof"])
            report_lines.append("```\n</details>\n")
        
        # Show suggested fix for failed repairs (for human review)
        if r["status"] == "VULNERABLE" and r.get("suggested_fix"):
            report_lines.append("\n**⚠️ Suggested Fix (Unverified):**")
            report_lines.append("*This fix was generated by AI but could not be formally verified. Manual review recommended.*")
            report_lines.append("\n<details><summary>View Suggested Fix</summary>\n")
            report_lines.append("```python")
            report_lines.append(r["suggested_fix"])
            report_lines.append("```\n</details>\n")
             
        report_lines.append("---")

    # Add unaudited files section
    if unaudited_files:
        report_lines.append("")
        report_lines.append("## ⏭️ Unaudited Files (Unchanged)")
        report_lines.append("> These files were not modified in this commit and were skipped.")
        report_lines.append("> Argus only audits files that change.")
        report_lines.append("")
        report_lines.append(f"<details><summary>{len(unaudited_files)} files not audited</summary>\n")
        for filename in sorted(unaudited_files):
            report_lines.append(f"- `{filename}`")
        report_lines.append("\n</details>")
        report_lines.append("")


    report_content = "\n".join(report_lines)
    
    # Write to local file
    try:
        with open("Argus_Audit_Report.md", "w") as f:
            f.write(report_content)
        print("Report written to Argus_Audit_Report.md")
    except Exception as e:
        print(f"Error writing report file: {e}")

    # Write to GitHub Step Summary
    step_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary_path:
        try:
            with open(step_summary_path, "a") as f:
                f.write(report_content)
            print("Report appended to GITHUB_STEP_SUMMARY")
        except Exception as e:
            print(f"Error writing to GITHUB_STEP_SUMMARY: {e}")
            
    return 1 if has_failure else 0


def create_remediation_pr(all_fixed_content: dict, all_proofs: dict) -> str:
    """
    Create an auto-remediation PR with all verified fixes.
    
    Args:
        all_fixed_content: Dict mapping filenames to fixed code
        all_proofs: Dict mapping filenames to Lean proofs
        
    Returns:
        URL of the created PR, or None if failed
    """
    # Get GitHub environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    branch_name = os.getenv("GITHUB_REF_NAME")
    
    if not github_token:
        print("[PR Creation] GITHUB_TOKEN not set, skipping PR creation")
        return None
    
    if not repo_name:
        print("[PR Creation] GITHUB_REPOSITORY not set, skipping PR creation")
        return None
    
    if not branch_name:
        print("[PR Creation] GITHUB_REF_NAME not set, using 'main' as default")
        branch_name = "main"
    
    try:
        print(f"\n{'='*50}")
        print("Creating Auto-Remediation Pull Request...")
        print(f"{'='*50}")
        print(f"  Repository: {repo_name}")
        print(f"  Base branch: {branch_name}")
        print(f"  Files to fix: {list(all_fixed_content.keys())}")
        
        github_service = GitHubService(token=github_token)
        pr_url = github_service.create_fix_pr(
            repo_name=repo_name,
            original_branch=branch_name,
            fixes=all_fixed_content,
            proofs=all_proofs
        )
        
        return pr_url
        
    except Exception as e:
        print(f"[PR Creation] Error: {e}")
        return None


def main():
    repo_path = os.environ.get("REPO_PATH", ".")
    print(f"Scanning repository at: {repo_path}")
    
    # Get all Python files for tracking unaudited files
    all_files = repo_manager.get_all_python_files(repo_path)
    
    # 1. Get changed files (Smart Scan)
    try:
        critical_files = repo_manager.get_changed_files(repo_path)
    except Exception as e:
        print(f"Error getting changed files: {e}")
        critical_files = []
    
    # Calculate unaudited files (unchanged files that were skipped)
    unaudited_files = [f for f in all_files if f not in critical_files]
        
    if not critical_files:
        print("No Python files changed. Skipping audit.")
        sys.exit(0)
        
    print(f"Auditing {len(critical_files)} files: {critical_files}")
    print(f"Skipping {len(unaudited_files)} unchanged files")
    
    # 1b. Run secrets scan on entire repo
    print(f"\n{'='*50}")
    print("Running Secrets Scan...")
    print(f"{'='*50}")
    secrets_findings = scan_repo(repo_path)
    
    if secrets_findings:
        print(f"⚠️  Found {len(secrets_findings)} potential secret(s)!")
    else:
        print("✅ No secrets detected")
    
    results = []
    
    # Data collection for PR creation
    all_fixed_content = {}
    all_proofs = {}
    
    # 2. Audit loop with repair
    for filename in critical_files:
        print(f"\n{'='*50}")
        print(f"--- Auditing {filename} ---")
        print(f"{'='*50}")
        
        try:
            full_path = os.path.join(repo_path, filename)
            
            # Check if file still exists
            if not os.path.exists(full_path):
                print(f"File {filename} does not exist (deleted?). Skipping.")
                continue
                
            with open(full_path, "r") as f:
                content = f.read()
                
            # Initial audit
            result = agents.audit_file(filename, content)
            result["original_code"] = content  # Store for JSON report
            
            # If VULNERABLE, attempt repair
            if result["status"] == "VULNERABLE":
                print(f"\n[{filename}] ❌ VULNERABLE - Initiating repair loop...")
                
                # Get the Lean error message for the AI
                lean_error = result.get("error_message", "") or "Verification failed"
                
                # 2.5: Generate AI Explanation
                print(f"[{filename}] Generating AI explanation for the vulnerability...")
                try:
                    ai_explanation = agents.explain_error(content, lean_error)
                    result["ai_explanation"] = ai_explanation
                except Exception as e:
                    print(f"[{filename}] Failed to generate explanation: {e}")
                    ai_explanation = ""
                
                # Capture original issue info BEFORE repair (for display even if fix succeeds)
                result["original_issue"] = {
                    "error_summary": extract_error_explanation(result.get("proof", ""), lean_error, ai_explanation),
                    "counterexample": extract_counterexample(result.get("proof", "")),
                    "original_proof": result.get("proof", "")
                }
                
                # Attempt AI-powered repair
                repair_result = attempt_repair(
                    filename=filename,
                    original_code=content,
                    lean_error=lean_error,
                    repo_path=repo_path
                )
                
                result["repair_attempt"] = repair_result
                
                # If repair succeeded, update status to AUTO_PATCHED
                if repair_result.get("success"):
                    result["status"] = "AUTO_PATCHED"
                    result["fixed_code"] = repair_result.get("fixed_code")
                    result["fixed_filename"] = repair_result.get("fixed_filename")
                    print(f"[{filename}] Status updated to AUTO_PATCHED")
                    
                    # Capture fix for PR creation
                    # Store the fixed content using the ORIGINAL filename (so PR updates the original file)
                    all_fixed_content[filename] = repair_result.get("fixed_code")
                    all_proofs[filename] = repair_result.get("fixed_proof", "Proof verified successfully")
                else:
                    # Even if repair failed verification, capture the suggestion
                    # for human review (graceful degradation)
                    if repair_result.get("fixed_code"):
                        result["suggested_fix"] = repair_result.get("fixed_code")
                        # Note: We intentionally don't add to all_fixed_content since it's not verified
                        # The PR will only contain verified fixes
            
            results.append(result)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            results.append({
                "filename": filename,
                "status": "VULNERABLE",
                "logs": [f"System Error: {str(e)}"],
                "repair_attempt": {"attempted": False, "reason": str(e)}
            })

    # 3. Report
    print(f"\n{'='*50}")
    print("Generating report...")
    print(f"{'='*50}")
    
    exit_code = generate_report(results, secrets_findings, unaudited_files)
    
    # 3b. Generate SARIF output
    print("Generating SARIF output...")
    try:
        sarif_data = generate_sarif(results, secrets_findings, repo_path)
        sarif_file = os.path.join(repo_path, "argus_results.sarif")
        with open(sarif_file, "w") as f:
            json.dump(sarif_data, f, indent=2)
        print(f"SARIF report written to: {sarif_file}")
    except Exception as e:
        print(f"Error generating SARIF report: {e}")
    
    # 3c. Generate rich JSON report for dashboard
    print("Generating JSON report for dashboard...")
    try:
        json_report = generate_json_report(results, secrets_findings, unaudited_files=unaudited_files)
        json_file = os.path.join(repo_path, "argus_report.json")
        with open(json_file, "w") as f:
            json.dump(json_report, f, indent=2)
        print(f"JSON report written to: {json_file}")
    except Exception as e:
        print(f"Error generating JSON report: {e}")
    
    # 4. Create PR if there are fixes
    if all_fixed_content:
        pr_url = create_remediation_pr(all_fixed_content, all_proofs)
        if pr_url:
            print(f"\n🚀 Argus Auto-Remediation PR Created: {pr_url}")
        else:
            print("\n⚠️ Could not create auto-remediation PR")
    else:
        print("\n📝 No fixes to submit (all files secure or unfixable)")
    
    # 5. Final status
    if exit_code == 0:
        print("\n✅ Audit PASSED")
    else:
        print("\n❌ Audit FAILED - Some vulnerabilities could not be fixed")
        
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

import os
import shutil
import tempfile
import git
import subprocess
from typing import List
from . import agents
import pathspec

def clone_repo(repo_url: str) -> str:
    """
    Clones a repo to a temporary directory and returns the path.
    Caller is responsible for cleaning up using shutil.rmtree().
    """
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning {repo_url} into {temp_dir}...")
    try:
        git.Repo.clone_from(repo_url, temp_dir, depth=1)
        return temp_dir
    except Exception as e:
        # If clone fails, clean up immediately and re-raise
        shutil.rmtree(temp_dir)
        raise e

def load_argusignore(repo_path: str) -> pathspec.PathSpec:
    """
    Loads .argusignore from the repo root and returns a PathSpec object.
    Returns an empty PathSpec if the file doesn't exist.
    """
    ignore_path = os.path.join(repo_path, '.argusignore')
    if os.path.exists(ignore_path):
        try:
            with open(ignore_path, 'r') as f:
                return pathspec.PathSpec.from_lines('gitwildmatch', f)
        except Exception as e:
            print(f"Error loading .argusignore: {e}")
            
    return pathspec.PathSpec.from_lines('gitwildmatch', [])

def get_all_python_files(repo_path: str) -> List[str]:
    """
    Walks the directory and returns a list of .py files, ignoring standard ignored dirs AND .argusignore patterns.
    """
    py_files = []
    # Hardcoded critical ignores - these are always skipped for performance/safety
    ignore_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules', 'tests', 'test', 'docs'}
    
    # Load user-defined ignores
    spec = load_argusignore(repo_path)
    
    for root, dirs, files in os.walk(repo_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # Store relative path for cleaner agent consumption
                rel_path = os.path.relpath(full_path, start=repo_path)
                
                # Check against .argusignore
                if not spec.match_file(rel_path):
                    py_files.append(rel_path)
                
    return py_files

def get_changed_files(repo_path: str) -> List[str]:
    """
    Identifies changed Python files in the current commit/PR.
    
    Uses multiple strategies in order of preference:
    1. GitHub Actions push event: uses GITHUB_EVENT_BEFORE..GITHUB_SHA
    2. GitHub Actions PR event: uses origin/GITHUB_BASE_REF..HEAD  
    3. Local development: uses HEAD^..HEAD
    4. Fallback: scans all files (first commit or shallow clone without event data)
    
    Returns list of changed .py files.
    """
    import json
    
    print("Checking for changed files...")
    spec = load_argusignore(repo_path)
    
    # Strategy 1: GitHub push event (has before SHA in event payload)
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, 'r') as f:
                event_data = json.load(f)
            
            before_sha = event_data.get("before")
            after_sha = event_data.get("after") or os.environ.get("GITHUB_SHA", "HEAD")
            
            # Check if before_sha is valid (not all zeros, which means first push)
            if before_sha and before_sha != "0000000000000000000000000000000000000000":
                print(f"Using GitHub event: {before_sha[:7]}..{after_sha[:7]}")
                
                # Fetch the 'before' commit (shallow clones don't have it)
                print(f"Fetching parent commit {before_sha[:7]} for comparison...")
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin", before_sha, "--depth=1"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if fetch_result.returncode != 0:
                    print(f"Warning: Could not fetch parent commit: {fetch_result.stderr.strip()}")
                
                # Now run the diff
                result = subprocess.run(
                    ["git", "diff", "--name-only", before_sha, after_sha],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                changed_files = result.stdout.strip().splitlines()
                valid_files = _filter_python_files(changed_files, repo_path, spec)
                print(f"GitHub event scan identified {len(valid_files)} changed Python files.")
                return valid_files
        except Exception as e:
            print(f"GitHub event parsing failed: {e}")

    
    # Strategy 2: GitHub PR event (compare with base branch)
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        try:
            print(f"Using GitHub PR base ref: origin/{base_ref}..HEAD")
            result = subprocess.run(
                ["git", "diff", "--name-only", f"origin/{base_ref}", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = result.stdout.strip().splitlines()
            valid_files = _filter_python_files(changed_files, repo_path, spec)
            print(f"PR comparison identified {len(valid_files)} changed Python files.")
            return valid_files
        except subprocess.CalledProcessError as e:
            print(f"PR base comparison failed: {e}")
    
    # Strategy 3: Local development - use HEAD^ (requires at least 2 commits)
    try:
        print("Using local git: HEAD^..HEAD")
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = result.stdout.strip().splitlines()
        valid_files = _filter_python_files(changed_files, repo_path, spec)
        print(f"Local scan identified {len(valid_files)} changed Python files.")
        return valid_files
        
    except subprocess.CalledProcessError:
        print("WARNING: Could not determine changed files (shallow clone or first commit).")
        print("Falling back to full scan - all files will be audited.")
        return get_all_python_files(repo_path)
    except Exception as e:
        print(f"Error during git diff: {e}. Falling back to full scan.")
        return get_all_python_files(repo_path)


def _filter_python_files(changed_files: List[str], repo_path: str, spec: pathspec.PathSpec) -> List[str]:
    """Filter a list of changed files to only include existing .py files not in .argusignore."""
    valid_files = []
    for f in changed_files:
        if f.endswith('.py') and os.path.exists(os.path.join(repo_path, f)):
            if not spec.match_file(f):
                valid_files.append(f)
    return valid_files

def get_critical_files(repo_path: str) -> List[str]:
    """
    Identifies the top 3 critical files in the repo using the Triage Agent.
    """
    print("Analyzing file structure...")
    file_list = get_all_python_files(repo_path)
    
    if not file_list:
        print("No Python files found in repository.")
        return []
        
    print(f"Found {len(file_list)} Python files. Sending to Agent for triage...")
    high_risk_files = agents.triage_files(file_list)
    
    print("Triage complete. High risk files:")
    for f in high_risk_files:
        print(f" - {f}")
        
    return high_risk_files

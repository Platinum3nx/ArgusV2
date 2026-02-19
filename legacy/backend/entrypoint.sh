#!/bin/sh
set -e

# Map the GitHub Action input to the variable Argus expects
if [ -n "$INPUT_GEMINI_API_KEY" ]; then
    export GEMINI_API_KEY="$INPUT_GEMINI_API_KEY"
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

echo "Starting Argus AI Auditor..."
export REPO_PATH="/github/workspace"

# Fix git safe.directory issue in Docker (container user differs from file owner)
git config --global --add safe.directory /github/workspace

# Run the module
python3 -m backend.ci_runner

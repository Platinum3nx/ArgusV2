# ArgusV2 Deployment Guide

## Prerequisites
- GitLab project with CI enabled
- Python 3.11+
- Docker (for containerized flow)
- API key for selected provider (`ANTHROPIC_API_KEY` or `GEMINI_API_KEY`)
- `GITLAB_TOKEN` (api scope) for MR comments/labels

## Option A: GitLab CI (recommended)
1. Fork/import repository.
2. Add CI variables (masked/protected as appropriate):
   - `ANTHROPIC_API_KEY` (or `GEMINI_API_KEY`)
   - `GITLAB_TOKEN`
3. Open/update MR.
4. Verify `argus-verify` runs and artifacts are produced.

## Option B: Docker standalone
```bash
docker build -t argusv2:local .
docker run --rm -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -v "$PWD":/workspace -w /workspace argusv2:local \
  python -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic
```

## Option C: Local CLI
```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic
```

## Environment variables
| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes for Anthropic mode | Provider auth |
| `GEMINI_API_KEY` | Yes for Gemini mode | Provider auth |
| `GITLAB_TOKEN` | Optional local / required for MR publish | MR comments + labels |
| `LLM_PROVIDER` | Optional | Default provider override |
| `ARGUS_ALLOW_LOCAL_VERIFY` | Optional | Allows local verifier path when set `true` |
| `CI_SERVER_URL` | CI-provided | GitLab base URL for MR publishing |
| `CI_PROJECT_ID` | CI-provided | Project identifier for MR publishing |
| `CI_MERGE_REQUEST_IID` | CI-provided | MR-triggered behavior |
| `CI_COMMIT_SHA` | CI-provided | Included in MR comment metadata |

## CLI options (release surface)
- `--file`, `--repo-path`, `--mode`, `--provider`, `--model`, `--allow-local-verify`, `--output-html`, `--skip-gitlab-publish`

## Runner sizing
- Minimum: 2 vCPU / 4GB RAM
- Recommended: 4 vCPU / 8GB RAM

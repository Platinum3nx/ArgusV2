# ArgusV2 Deployment Guide

## Prerequisites
- GitLab project with CI enabled
- Python 3.11+
- Docker (for containerized flow)
- `ARGUS_PROXY_TOKEN` for hosted LLM access
- `GITLAB_TOKEN` (api scope) for MR comments/labels

## Option A: GitLab CI (recommended)
1. Fork/import repository.
2. Add CI variables (masked/protected as appropriate):
   - `ARGUS_PROXY_TOKEN`
   - `GITLAB_TOKEN`
3. Open/update MR.
4. Verify `argus-verify` runs and artifacts are produced.

## Option B: Docker standalone
```bash
docker build -t argusv2:local .
docker run --rm -e ARGUS_PROXY_TOKEN=$ARGUS_PROXY_TOKEN -v "$PWD":/workspace -w /workspace argusv2:local \
  python -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic
```

## Option C: Local CLI
```bash
python3 -m pip install -r requirements.txt
export ARGUS_PROXY_TOKEN=<your-token>
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic
```

## Environment variables
| Variable | Required | Purpose |
|---|---|---|
| `ARGUS_PROXY_TOKEN` | Yes | Hosted proxy authentication |
| `ARGUS_PROXY_URL` | Optional | Hosted proxy base URL override |
| `GITLAB_TOKEN` | Optional local / required for MR publish | MR comments + labels |
| `LLM_PROVIDER` | Optional | Keep default `anthropic` |
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

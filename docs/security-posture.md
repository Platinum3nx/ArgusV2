# ArgusV2 Security Posture

## Trust model
Argus uses a **prove-before-trust** model:
- LLMs (Anthropic/Gemini) are advisors for discovery, proof hints, and repair suggestions.
- Lean/Dafny verifiers are the authority for safety claims.
- Verdicts are fail-closed: verifier/runtime errors cannot produce VERIFIED.

## Secret handling
- `ARGUS_PROXY_TOKEN` and `GITLAB_TOKEN` must be provided via CI/CD masked variables.
- Secrets are never committed to the repo and are excluded from generated artifacts.
- Tokens can be rotated without data migration.
- Docker image contains no baked credentials.

## Access model
- Developer: sees MR comments, labels, and artifacts.
- Platform/DevOps: configures runners and CI variables.
- Security lead: configures merge policy and interprets findings.
- Project admin: controls project visibility and token provisioning.

## Fail-closed guarantees
- Missing/invalid provider config -> startup `ConfigurationError`.
- LLM empty/malformed output -> VULNERABLE/ERROR, never VERIFIED.
- Verifier crash/translation failure -> ERROR, never VERIFIED.
- Network/provider failures -> pipeline exits non-zero in CI path.

## Supply-chain posture
- Dependencies pinned in `requirements.txt`.
- Containerized runtime via `Dockerfile`.
- No runtime plugin download path in normal CI flow.

## Known limitations
- Source code is sent to configured LLM provider for enabled AI stages.
- Trace artifacts may contain generated code/proof snippets; set retention accordingly.
- Artifact-at-rest encryption depends on host/platform controls.

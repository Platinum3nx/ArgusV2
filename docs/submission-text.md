# Devpost Submission Snippet

## Custom Public Agent / Flow
ArgusV2 includes a custom public GitLab Duo agent (**Argus Verified Repair**) and a public event-driven flow for merge requests.

- Agent definition: `config.yml`
- Agent runtime config: `.gitlab/duo/agent-config.yml`
- Public flow definition: `.gitlab/duo/flows/argus_verify.yml`

On every merge request, Argus autonomously:
1. Discovers formal security obligations from Python changes
2. Translates obligations into Lean 4 / Dafny artifacts
3. Runs formal verification and semantic guard checks
4. Attempts constrained proof search and repair when proofs fail
5. Publishes structured verdict outputs (MR comments/labels when configured)
6. Enforces fail-closed merge behavior via CI exit contract

This is not chat-only behavior. It is trigger-based autonomous execution tied to GitLab merge request events.

## Anthropic Impact Track

ArgusV2 uses **Anthropic Claude** as its primary LLM reasoning engine across all four reasoning stages:

| Stage | Role | LLM call |
|:---|:---|:---|
| Invariant Discovery | Extract security obligations and assumption candidates from Python code | `claude-sonnet-4-6` |
| Lean Translation | Translate obligations into Lean 4 formal verification artifacts | `claude-sonnet-4-6` |
| Proof Search | Generate repaired Lean proof candidates (constrained — no `sorry`/`admit`) | `claude-sonnet-4-6` |
| Code Repair | Produce candidate Python fixes that re-satisfy failed obligations | `claude-sonnet-4-6` |

**Key design principle**: Claude is the reasoning advisor; the formal verifier (Lean 4 / Dafny) is the authority. Every Claude-generated artifact passes through deterministic gates before any verdict is issued. False positives are impossible by construction — the verifier must independently confirm every claim.

**Provenance**: Every trace artifact (`manifest.json`, per-file `result.json`) records `provider` and `model` fields so the reasoning chain is fully auditable.

**Fail-closed**: Missing `ANTHROPIC_API_KEY` raises a `ConfigurationError` at pipeline startup — the pipeline never silently degrades to a weaker reasoning mode.

**Model selection**: Default is `claude-sonnet-4-6`. Override with `--model claude-opus-4-6` for maximum reasoning depth, or `--provider gemini` for Gemini fallback.

## Judge FAQ (ready answers)
**Q: Is this just a CI pipeline?**
A: It is an autonomous agent+flow packaged for GitLab MR events, with declared tools/capabilities, formal verification logic, and autonomous MR actions beyond test execution.

**Q: Where is the custom public agent?**
A: `config.yml` and `.gitlab/duo/agent-config.yml` define the agent; `.gitlab/duo/flows/argus_verify.yml` defines the public flow.

**Q: Does it require chat interaction?**
A: No. The flow is event-triggered on merge requests and runs autonomously.

**Q: What does Anthropic Claude actually do?**
A: Claude reasons over Python source code to produce formal artifacts (obligations, Lean theorems, proof candidates, repaired code). The formal verifier independently checks every artifact — Claude's output is never trusted on its own.

**Q: What if Claude makes a mistake?**
A: The formal verifier catches it. The system is designed so Claude's errors produce UNVERIFIED/VULNERABLE verdicts, never false VERIFIED verdicts. Fail-closed by design.

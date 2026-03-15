# Devpost Submission Snippet (Phase 2)

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

## Judge FAQ (ready answers)
**Q: Is this just a CI pipeline?**
A: It is an autonomous agent+flow packaged for GitLab MR events, with declared tools/capabilities, formal verification logic, and autonomous MR actions beyond test execution.

**Q: Where is the custom public agent?**
A: `config.yml` and `.gitlab/duo/agent-config.yml` define the agent; `.gitlab/duo/flows/argus_verify.yml` defines the public flow.

**Q: Does it require chat interaction?**
A: No. The flow is event-triggered on merge requests and runs autonomously.

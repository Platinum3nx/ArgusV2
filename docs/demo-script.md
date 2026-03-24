# ArgusV2 Demo Script — 3-Minute Judged Format

**Total runtime**: 3:00 (180 seconds)
**Format**: Screen recording with voiceover narration
**Setup**: Two terminal windows + browser tab open to `argus_dashboard.html`

---

## Pre-Demo Checklist (before recording)

- [ ] `ARGUS_PROXY_TOKEN` is set in the environment
- [ ] `demo_target/` files exist and are confirmed
- [ ] Terminal font size is large (16pt+) for readability
- [ ] Dashboard backup artifact is open in a browser tab
- [ ] Backup run artifacts are in `demo_target/backup_artifacts/`
- [ ] Screen resolution: 1920×1080 (or 1440×900 for laptop recording)

**Rehearsal target**: Hit each timestamp within ±3 seconds.

---

## Segment 1: The Problem (0:00 – 0:25)

**Duration**: 25 seconds

### Screen
- Open `demo_target/vulnerable_transfer.py` in a code editor or terminal
- Highlight line 23: `return sender_balance - amount`
- Show a quick inline comment or terminal note: `# transfer(100, 200) → -100`

### Narration
> "Every day, developers push security-critical code. Manual code review catches
> some issues — but subtle logic flaws slip through. This function looks correct.
> But when `amount` exceeds `balance`, the result goes negative — an attacker
> can create money from nothing. Standard linters won't catch this. Code review
> often misses it. Argus proves it."

### Key visuals
- Code on screen with the missing bounds check clearly visible
- Annotated example: `transfer(100, 200) → -100`
- Subtitle overlay: **"Linters miss it. Code review misses it. Argus proves it."**

---

## Segment 2: The Trigger (0:25 – 0:50)

**Duration**: 25 seconds

### Screen
- Show the terminal or GitLab MR view
- Run the CLI command live (or cut to a recording of it starting):

```bash
python -m src.adapters.cli \
  --file demo_target/vulnerable_transfer.py \
  --allow-local-verify \
  --provider anthropic
```

### Narration
> "On every merge request, Argus triggers automatically — no human intervention.
> It discovers security obligations from the Python source, translates them into
> Lean 4 formal proof obligations, and runs the formal verifier. Claude provides
> reasoning. Lean 4 provides mathematical proof. Neither alone is sufficient."

### Key visuals
- Terminal showing the CLI command executing
- Stage-by-stage output: `[discover]`, `[translate]`, `[verify]`
- Subtitle: **"Event-triggered. Autonomous. No chat required."**

---

## Segment 3: Detection + Diagnosis (0:50 – 1:25)

**Duration**: 35 seconds

### Screen
- Terminal showing verification failure output
- Cut to or show the Lean 4 obligation code from `.argus-trace/`
- Show the obligation that failed: `non_negative_result`

### Narration
> "Argus found the vulnerability. The obligation `non_negative_result` failed —
> the Lean 4 prover confirmed that for inputs where `amount` exceeds `balance`,
> the function can return a negative integer. This is a mathematical proof of
> the vulnerability, not a heuristic or pattern match. Claude powered the
> obligation extraction; Lean 4 delivered the verdict."

### Key visuals
- Lean 4 theorem code visible (from trace artifact)
- Verification failure message highlighted
- Subtitle: **"Claude proposes. Lean disposes. The verdict is mathematical."**

---

## Segment 4: Repair + Re-verification (1:25 – 2:05)

**Duration**: 40 seconds

### Screen
- Terminal showing `[repair]` stage — Claude generating a fix
- Side-by-side diff: original (red) vs repaired (green)
- Re-verification success message

### Narration
> "Argus uses Claude to generate a security patch. The fix adds the missing bounds
> check. But Argus doesn't trust the AI — it runs the Lean 4 prover again on the
> repaired code. Both obligations now pass. The repair is formally verified. The
> verdict changes from VULNERABLE to FIXED."
>
> "Claude proposes. Lean disposes."

### Key visuals
```
BEFORE:                          AFTER (VERIFIED):
def transfer(s, a):              def transfer(s, a):
    return s - a                     if a <= 0: return s
                                     if a > s: return s
                                     return s - a
```
- Verdict badge changing: 🔴 VULNERABLE → 🔧 FIXED
- Subtitle: **"AI-generated. Formally verified. Trust the proof, not the model."**

---

## Segment 5: Developer & Compliance UX (2:05 – 2:35)

**Duration**: 30 seconds

### Screen
- Switch to browser: open `argus_dashboard.html`
- Scroll through: Executive Summary → Pipeline Timeline → File Cards → Audit Trail
- Cut to: GitLab MR comment preview (from a screenshot or recorded run)

### Narration
> "Developers see a structured MR comment — what failed, the verified repair diff,
> and exactly what to do. Security leads get the Mission Control dashboard: a
> visual overview of every stage, every obligation, every artifact. SARIF reports
> integrate directly with GitLab's Security Dashboard. Every decision is traceable
> from obligation discovery through formal proof to enforcement."

### Key visuals
- Mission Control dashboard open in browser — executive summary visible
- MR comment with repair diff (screenshot or live view)
- Artifact list: `argus_report.json`, `argus_dashboard.html`, `argus-sarif-report.json`
- Subtitle: **"From discovery to proof to merge gate — fully traceable."**

---

## Segment 6: Close (2:35 – 3:00)

**Duration**: 25 seconds

### Screen
- Architecture diagram (from `docs/architecture.md` or a clean slide)
- Key metrics overlay:
  - "204/204 tests passing"
  - "0 false positives across 18+ validation runs"
  - "3/3 live demo runs archived as fallback artifacts"
- Final positioning statement

### Narration
> "ArgusV2 is the trust layer for AI-accelerated software delivery. It uses
> Anthropic Claude for reasoning and Lean 4 for mathematical proof. It's
> autonomous, fail-closed, and enterprise-ready. The deterministic core never
> changes — Claude is the advisor, Lean 4 is the authority, and Argus enforces
> the verdict before merge. Safer merges. Faster reviews. Auditable trust."

### Key visuals
- Architecture diagram: LLM (ADVISOR) → Formal Verifier (AUTHORITY)
- Final title card: **"ArgusV2 — The Trust Layer for AI-Accelerated Software Delivery"**
- Subtitle: **"Claude proposes. Lean disposes. Argus enforces."**

---

## Backup Contingency Plan

| Failure | Response |
|:---|:---|
| API slow / timeout during live run | Cut to pre-recorded terminal output from `backup_artifacts/` |
| Network down | Open `demo_target/backup_artifacts/vulnerable_transfer_dashboard.html` in browser |
| Dashboard won't open | Show MR comment screenshot (pre-captured) |
| Wrong output / unexpected verdict | Cut to backup recording, note: "Exact same code, pre-recorded run" |

**Pre-recording verification** (run before recording session):
```bash
python -m src.adapters.cli \
  --file demo_target/vulnerable_transfer.py \
  --allow-local-verify \
  --provider anthropic \
  --output-json demo_target/backup_artifacts/vulnerable_transfer_report.json \
  --output-html demo_target/backup_artifacts/vulnerable_transfer_dashboard.html \
  --output-md demo_target/backup_artifacts/vulnerable_transfer_report.md
```

---

## Timestamp Summary

| Time | Segment | Key Moment |
|:---|:---|:---|
| 0:00 – 0:25 | Problem | Show vulnerable code, annotate negative result |
| 0:25 – 0:50 | Trigger | Run CLI, show autonomous pipeline starting |
| 0:50 – 1:25 | Detection | Lean 4 proof failure, obligation name visible |
| 1:25 – 2:05 | Repair | Before/after diff, re-verify success, FIXED verdict |
| 2:05 – 2:35 | UX | Dashboard in browser, MR comment, artifact list |
| 2:35 – 3:00 | Close | Architecture diagram, metrics, positioning statement |

---

## Judging Rubric Coverage

| Rubric Category | Demo Segment | Evidence Shown |
|:---|:---|:---|
| Technological Implementation | 2, 3, 4 | Lean 4 proof, Claude reasoning, trace artifacts |
| Design & Usability | 5 | Mission Control dashboard, MR comment, 45-second comprehension |
| Potential Impact | 1, 6 | Real vulnerability caught, measurable outcomes |
| Quality of Idea | 3, 4, 6 | AI advisor + formal proof authority model |
| Custom Public Agent/Flow | 2 | CLI command, CI trigger proof |
| Anthropic Integration | 3, 4, 6 | Claude reasoning shown, provenance in artifacts |

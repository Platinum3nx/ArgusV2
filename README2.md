# Argus V2 — Autonomous Formal Verification Agent for GitLab

> **"We are moving software from 'It looks like it works' (Testing) to 'It is mathematically impossible for it to fail' (Verification)."**

Argus is an autonomous, zero-config DevSecOps agent that mathematically proves critical Python bugs are impossible — before code is ever merged. It integrates natively into GitLab as a **Duo Custom Flow**, operating as an invisible safety net that requires no developer configuration, no manual invocation, and no formal methods expertise.

When a developer pushes a merge request, Argus automatically:
1. **Discovers** what safety properties the code needs (invariants)
2. **Translates** the Python logic into formal proof language (Lean 4 / Dafny)
3. **Verifies** the proofs using mathematical compilers
4. **Repairs** any failing code using AI-guided fix generation
5. **Reports** directly on the MR with verified fixes and proof artifacts

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Soundness Envelope](#soundness-envelope)
- [Verdict Contract (Fail Closed)](#verdict-contract-fail-closed)
- [How Argus Works](#how-argus-works)
- [Architecture](#architecture)
- [Implementation Hardening Changes (Module-Level)](#implementation-hardening-changes-module-level)
- [Trust Model](#trust-model)
- [Neuro-Symbolic Repair Loop](#neuro-symbolic-repair-loop)
- [GitLab Duo Integration](#gitlab-duo-integration)
- [Invariant Discovery (Key Innovation)](#invariant-discovery-key-innovation)
- [Translation Engine](#translation-engine)
- [Verification Engine](#verification-engine)
- [AI Repair Engine](#ai-repair-engine)
- [Observability & Traceability](#observability--traceability)
- [CI Integrity Gates & Acceptance Criteria](#ci-integrity-gates--acceptance-criteria)
- [Data Handling & Privacy](#data-handling--privacy)
- [Reporting & MR Integration](#reporting--mr-integration)
- [Directory Structure](#directory-structure)
- [Tech Stack](#tech-stack)
- [Supported Python Constructs](#supported-python-constructs)
- [Configuration](#configuration)
- [Demo Scenarios](#demo-scenarios)
- [Hackathon Submission](#hackathon-submission)
- [Startup Vision](#startup-vision)
- [Development Roadmap](#development-roadmap)

---

## Problem Statement

### The $10 Billion Bug Problem

Unit tests check that code works for the inputs you *thought of*. Formal verification proves code works for **every possible input within the verified subset** — including the edge cases no one imagined.

**Real-world examples of bugs that testing missed:**
- **Ariane 5 rocket explosion** (1996): Integer overflow in a type conversion. $370 million lost.
- **Knight Capital** (2012): A race condition in trading logic. $440 million lost in 45 minutes.
- **Heartbleed** (2014): Buffer over-read in OpenSSL. Affected 17% of all web servers.
- **Therac-25** (1985–1987): Race condition in radiation therapy machine. 3 patients died.

Bugs in each of these categories (integer overflow, arithmetic bounds, buffer access, state transitions) fall within the class of properties formal verification can prove impossible. But formal verification has historically been:
- **Too expensive**: Requires PhD-level expertise in proof assistants
- **Too slow**: Manual proof engineering takes weeks per function
- **Too narrow**: Only available at NASA/DARPA-funded organizations

### Argus's Mission

Argus eliminates all three barriers by combining:
1. **AI reasoning** (Gemini) to automate the parts that need creativity
2. **Mathematical compilers** (Lean 4 / Dafny) to provide the parts that need certainty
3. **DevOps integration** (GitLab Duo) to deliver it with zero developer friction

The result: Any team, on any GitLab project, gets automated formal verification for the Python constructs and property classes Argus supports — with mathematical certainty, not statistical confidence.

---

## Soundness Envelope

> **Argus's guarantees are absolute within its supported scope, and explicitly bounded outside it.**

Argus does **not** claim to verify all possible properties of all possible Python code. It operates within a defined **soundness envelope** — and it is precise about what falls inside and outside.

### What Argus Guarantees (Inside the Envelope)

When Argus reports `VERIFIED ✅`, it means:
- The specific safety properties (invariants) **are mathematically proven** for the translated code
- The Lean 4 or Dafny compiler accepted the proof — this is not a heuristic
- The proof was checked for `sorry` (incomplete proof marker) and rejected if found

This guarantee holds for:
- Functions using [supported Python constructs](#supported-python-constructs)
- Properties in [supported invariant categories](#invariant-categories)
- Code where the translation faithfully preserves the Python semantics

### What Argus Does NOT Guarantee (Outside the Envelope)

| Limitation | Explanation |
|:---|:---|
| **Concurrency** | Argus does not verify race conditions, deadlocks, or thread safety |
| **I/O and side effects** | File operations, network calls, database queries are not modeled |
| **OOP patterns** | Class hierarchies, inheritance, method dispatch are not translated |
| **Dynamic typing** | Code without type annotations cannot be meaningfully verified |
| **Translation fidelity** | The translation from Python to Lean/Dafny is a model — semantic drift is possible for complex constructs |
| **Completeness & soundness bounds** | Argus may fail to prove a true property (report VULNERABLE for safe code). False `VERIFIED` is driven toward zero **inside the envelope** using deterministic obligations, assumption evidence checks, and fail-closed verdicting; residual risk exists if translation fidelity is violated. |

### The Assumption Firewall (Critical Design Rule)

> **⚠️ The LLM is never allowed to invent assumptions that weaken proof obligations.**

This is Argus's most important soundness rule. Discovered invariants are classified into two strict categories:

| Category | Who decides | Role in proof | Example |
|:---|:---|:---|:---|
| **Obligations** | Argus (must prove) | The goal the proof must establish — from code alone, with no gifted assumptions | `withdraw(balance, amount) ≥ 0` |
| **Assumed inputs** | User/team policy (trusted) | Preconditions about the calling context, documented and auditable | `balance ≥ 0` (evidence: DB constraint or validated API contract) |

**Rules:**
1. **Obligations come from deterministic policy code** (`src/core/obligation_policy.py`) — Gemini may suggest candidates, but only policy-approved obligations become pass criteria
2. **Assumed inputs require evidence** (`src/core/assumption_evidence.py`) — every assumption must include machine-checkable provenance (validator, DB constraint, API schema, or approved policy ID)
3. **The LLM cannot mutate pass criteria** — if a proof fails, the repair engine can change Python code only, never obligations/assumptions
4. **Every assumption appears in the MR report** — developers can audit what Argus assumed vs. what it proved
5. **Missing evidence or unsupported semantics fail closed** — Argus emits `UNVERIFIED`, never `VERIFIED`

### Verdict Contract (Fail Closed)

Argus uses strict verdict semantics:

| Verdict | Meaning | Merge Gate |
|:---|:---|:---|
| `VERIFIED` | All canonical obligations proven; assumptions are evidenced; no unsupported constructs encountered | Pass |
| `FIXED` | Originally vulnerable, repaired, then meets all `VERIFIED` criteria | Pass (with fix review) |
| `VULNERABLE` | At least one obligation failed after allowed repair attempts | Block |
| `UNVERIFIED` | Unsupported construct, missing assumption evidence, or translation guard failure | Block |
| `ERROR` | Tooling/runtime failure (timeouts, infra failures) | Block |

---

## How Argus Works

When a merge request is opened or updated on GitLab, Argus runs as a Duo Custom Flow:

```
Developer pushes MR
       │
       ▼
┌──────────────────┐
│  GitLab Duo Flow │  ← Triggered by MR event or @mention
│  (argus_verify)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                    ARGUS PIPELINE                         │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │  1. Discover │───▶│ 2. Translate │───▶│  3. Verify  │ │
│  │  Invariants  │    │  to Proof    │    │  Formally   │ │
│  │  (Gemini)    │    │  (AST+LLM)  │    │  (Lean/Daf) │ │
│  └─────────────┘    └──────────────┘    └──────┬──────┘ │
│                                                │        │
│                                         Pass? ─┤        │
│                                                │        │
│                              ┌─────────────────┴──────┐ │
│                              │ YES              NO     │ │
│                              ▼                  ▼      │ │
│                        ┌──────────┐      ┌──────────┐  │ │
│                        │ VERIFIED │      │ 4. Repair │  │ │
│                        │    ✅    │      │  (Gemini) │  │ │
│                        └──────────┘      └─────┬────┘  │ │
│                                                │       │ │
│                                          Re-verify     │ │
│                                          (loop ≤3x)    │ │
│                                                │       │ │
│                                          ┌─────▼────┐  │ │
│                                          │ 5.Report │  │ │
│                                          │ on MR    │  │ │
│                                          └──────────┘  │ │
└──────────────────────────────────────────────────────────┘
```

### End-to-End Example

**Input**: Developer pushes this Python function in an MR:

```python
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
```

**Step 1 — Invariant Discovery** (Gemini):
> **Obligations** (must prove from code alone):
> 1. `withdraw(balance, amount) ≥ 0` — balance must never go negative after withdrawal
>
> **Assumed inputs** (caller contract — surfaced in report):
> 1. `balance ≥ 0` — source: database constraint (`accounts.balance CHECK >= 0`)
> 2. `amount > 0` — source: API schema (`WithdrawRequest.amount` minimum is `1`)

**Step 2 — Translation** (AST Translator):
```lean
def withdraw (balance : Int) (amount : Int) : Int :=
  balance - amount

-- Assumed inputs are explicit hypotheses (auditable in MR report)
-- Obligation is the proof goal — Argus must prove this, not assume it
theorem balance_non_negative (balance amount : Int)
  (h_bal : balance ≥ 0)   -- ASSUMED INPUT: caller contract
  (h_amt : amount ≥ 0) :  -- ASSUMED INPUT: caller contract
  withdraw balance amount ≥ 0 := by  -- OBLIGATION: must prove
  unfold withdraw
  omega
```

**Step 3 — Verification** (Lean 4 Compiler):
```
❌ FAILED: omega could not prove the goal
   balance amount : Int
   h_bal : balance ≥ 0
   ⊢ balance - amount ≥ 0
```

**Step 4 — Repair** (Gemini):
```python
def withdraw(balance: int, amount: int) -> int:
    if amount <= 0 or amount > balance:
        return balance
    return balance - amount
```

Re-translated, re-verified: **✅ PROOF PASSES**

**Step 5 — MR Comment**:

> ### 🛡️ Argus Formal Verification Report
>
> | File | Status | Finding |
> |:---|:---|:---|
> | `withdraw.py` | ⚠️ VULNERABLE → ✅ FIXED | Balance can go negative without guard |
>
> **Auto-fix available**: The function lacked bounds checking. Argus generated a verified fix that ensures `balance >= 0` for all inputs that satisfy documented assumptions.
>
> <details><summary>View Lean 4 Proof</summary>
>
> ```lean
> theorem balance_non_negative ...
> ```
> </details>
>
> **Suggested fix commit**: [View diff →]()

---

## Architecture

### Core Design Principles

| Principle | Description |
|:---|:---|
| **Platform-agnostic core** | All verification logic lives in `src/core/` with zero platform dependencies. Can run as GitLab Flow, GitHub Action, CLI, or API. |
| **Dual verification engines** | Lean 4 (primary, for arithmetic/conditionals/data structures) + Dafny (secondary, for loops/iteration). Canonical property normalization ensures both engines verify the same properties. |
| **Obligation/assumption separation** | Gemini discovers safety properties, but obligations (must-prove) and assumptions (trusted input policy) are strictly separated. The LLM cannot weaken proofs. |
| **Externalized prompts** | All LLM prompts are versioned files in `src/prompts/`, not inline strings. Testable, swappable, improvable independently. |
| **Hybrid translation** | Deterministic AST-based translation for simple code (fast, reliable). Gemini-powered translation for complex constructs (flexible). |
| **Autonomous with observability** | No UI, no dashboard, no manual invocation — but full per-stage traceability via structured artifacts for debugging and audit. |

### Component Map

```
┌─────────────────────────────────────────────────────────────┐
│                      ADAPTERS (thin)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ GitLab Duo   │  │ GitHub       │  │ CLI               │ │
│  │ Flow Adapter │  │ Adapter      │  │ (local dev/test)  │ │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬─────────┘ │
│         │                 │                     │           │
│         └─────────────────┼─────────────────────┘           │
│                           │                                 │
│                     ┌─────▼──────┐                          │
│                     │  Pipeline  │  ← Orchestrates all      │
│                     │  (core)    │     stages below          │
│                     └─────┬──────┘                          │
│                           │                                 │
│         ┌─────────────────┼─────────────────────────┐       │
│         │                 │                         │       │
│   ┌─────▼─────┐   ┌──────▼──────┐   ┌─────────────▼─┐     │
│   │ Invariant │   │ Translation │   │   Verification │     │
│   │ Discovery │   │   Engine    │   │     Engine     │     │
│   │ (Gemini)  │   │  AST + LLM │   │  Lean + Dafny  │     │
│   └───────────┘   └─────────────┘   └────────────────┘     │
│                                                             │
│   ┌───────────┐   ┌─────────────┐   ┌────────────────┐     │
│   │  Repair   │   │  Reporter   │   │   Secrets      │     │
│   │  Engine   │   │  (SARIF/MD) │   │   Scanner      │     │
│   │ (Gemini)  │   │             │   │   (regex)      │     │
│   └───────────┘   └─────────────┘   └────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Hardening Changes (Module-Level)

To minimize false verification risk, Argus V2 adds explicit trust-boundary modules:

| Module | Responsibility | Trusted for `VERIFIED`? |
|:---|:---|:---|
| `src/core/obligation_policy.py` | Deterministically generate canonical obligations from AST patterns + rule packs | Yes |
| `src/core/assumption_evidence.py` | Validate that each assumption has evidence and provenance | Yes |
| `src/core/semantic_guard.py` | Run translation sanity checks and fail on drift-risk patterns | Yes |
| `src/core/verdict.py` | Enforce fail-closed verdict contract (`VERIFIED/FIXED/VULNERABLE/UNVERIFIED/ERROR`) | Yes |
| `src/core/invariant_discovery.py` | LLM-assisted candidate generation and ranking | No (advisory) |
| `src/core/repair.py` | LLM-assisted code repair proposals | No (advisory) |
| `src/core/translator/llm_translator.py` | LLM translation for unsupported deterministic patterns | Conditionally (only after semantic guards pass) |

### Trust Model

The trusted computing base for a `VERIFIED` result is:
1. Canonical obligation policy
2. Assumption evidence validator
3. Translation/semantic guards
4. Lean/Dafny verifier result parser
5. Verdict contract enforcement

Everything else (candidate discovery, repair generation, explanation text) is untrusted and must pass through these gates.

---

## Neuro-Symbolic Repair Loop

The term **"neuro-symbolic"** describes Argus's core innovation: combining neural AI (Gemini) with symbolic reasoning (Lean 4 / Dafny compilers).

| Component | Type | Role |
|:---|:---|:---|
| Invariant Discovery | **Neural** | Gemini reads Python code and *reasons* about what safety properties matter |
| LLM Translation | **Neural** | Gemini translates complex Python constructs to Lean 4 syntax |
| AST Translation | **Symbolic** | Deterministic AST parser converts simple Python to Lean 4 (no AI) |
| Lean 4 Compiler | **Symbolic** | Mathematical compiler — either the proof is valid or it isn't. No ambiguity. |
| Dafny Compiler | **Symbolic** | SMT-solver-backed verification for loops with invariants |
| AI Repair | **Neural** | Gemini reads the Lean error message and reasons about how to fix the Python code |
| Re-verification | **Symbolic** | The fix is re-verified mathematically — the AI's fix is not trusted blindly |

**The key insight**: The AI is used where creativity is needed (understanding code intent, generating fixes). The compiler is used where certainty is needed (mathematical proof). Neither alone is sufficient. Together, they form a closed loop.

### Repair Loop Logic

```python
MAX_REPAIR_ATTEMPTS = 3

for attempt in range(MAX_REPAIR_ATTEMPTS):
    # 1. Translate Python → Lean/Dafny
    proof_code = translate(python_code, invariants)

    # 2. Verify with mathematical compiler
    result = verify(proof_code)

    if result.verified:
        return VERIFIED  # Bug is mathematically impossible ✅

    # 3. Ask Gemini to fix the Python code based on the proof error
    python_code = repair(python_code, result.error_message)

# All attempts exhausted — report as VULNERABLE
return VULNERABLE  # with error details + partial analysis
```

---

## GitLab Duo Integration

Argus runs as a **GitLab Duo Custom Flow** — a natively integrated AI workflow within the GitLab platform.

### How It's Triggered

Argus can be triggered in multiple ways:

1. **@mention in MR comment**: A developer or reviewer types `@argus-verify` in an MR discussion
2. **Reviewer assignment**: Assigning the Argus service account as a reviewer triggers the flow
3. **CI pipeline**: Argus can run as a CI job in `.gitlab-ci.yml` for automatic triggering on every MR

### GitLab Duo Flow Definition

The flow is defined in the GitLab Duo platform and registered via the AI Catalog:

**Flow Configuration (`config.yml`):**
```yaml
display_name: "Argus Formal Verification"
description: "Autonomous formal verification agent that mathematically proves Python code is bug-free using Lean 4 and Gemini AI."
version: "2.0.0"
```

**Agent Configuration (`.gitlab/duo/agent-config.yml`):**
```yaml
image: argus-v2:2.0.0  # Pinned Docker image with Python 3.11 + Lean 4.16.0 + Dafny 4.9.1
setup_script:
  - pip install -r requirements.txt
cache:
  paths:
    - lean_project/.lake/
    - .argus-cache/
```

### CI Pipeline Integration

For teams that prefer CI-based triggering, Argus also runs as a pipeline job:

**`.gitlab-ci.yml`:**
```yaml
argus-verify:
  stage: test
  image: argus-v2:2.0.0
  script:
    - python -m src.adapters.cli --repo-path . --mode ci
  artifacts:
    reports:
      sast: gl-sast-report.json     # GitLab's expected SAST schema filename
    paths:
      - Argus_Audit_Report.md
      - argus-sarif-report.json      # Raw SARIF 2.1.0 attached separately
      - .argus-trace/                # Per-stage traceability artifacts
  rules:
    - if: $CI_MERGE_REQUEST_IID
```

> **Note on SARIF compatibility**: Argus generates a native `gl-sast-report.json` conforming to GitLab's [Security Report Schema](https://gitlab.com/gitlab-org/security-products/security-report-schemas) for the target GitLab version, ensuring findings appear in the Security Dashboard. The raw SARIF 2.1.0 report is attached separately as an additional artifact for tooling interoperability.

### MR Interaction

When Argus completes verification, it posts structured findings directly on the MR:

- **Thread comments** with per-file verification results
- **Inline suggestions** with verified fixes (using GitLab's suggestion syntax)
- **Labels** applied to the MR (`argus:verified`, `argus:vulnerable`, `argus:fixed`)
- **SARIF report** uploaded as a security artifact (appears in GitLab's Security Dashboard)

---

## Invariant Discovery (Key Innovation)

This is the **single biggest improvement** over Argus V1. Instead of hardcoding a single theorem template (`result >= 0`), Argus V2 uses a deterministic obligation policy plus Gemini candidate discovery to identify what safety properties the code actually needs.

### What Are Invariants?

An invariant is a property that must **always be true** about a piece of code:
- "The account balance is never negative"
- "The list has no duplicate entries"
- "The loop index stays within array bounds"
- "The total of all transfers is conserved (no money created or destroyed)"

### How Discovery Works

Argus discovery is a **two-stage pipeline**, not pure LLM output:

1. **Deterministic baseline (`src/core/obligation_policy.py`)**  
   AST + rule packs generate non-negotiable obligations for recognized patterns (bounds, non-negativity, uniqueness, conservation templates).

2. **LLM candidate augmentation (`src/core/invariant_discovery.py`)**  
   Gemini proposes additional candidates and rankings. Candidates are policy-validated before admission.

3. **Assumption evidence validation (`src/core/assumption_evidence.py`)**  
   Any assumption must carry evidence metadata (`source_type`, `source_ref`, `evidence_id`) and pass schema checks.

4. **Canonicalization**  
   Final obligations/assumptions are normalized into a canonical set used by all translators/verifiers.

**Prompt** (`src/prompts/discover_invariants.md`) is advisory only. It cannot directly alter pass criteria.

**Output format** (structured JSON):

```json
{
  "function": "transfer_funds",
  "obligations": [
    {
      "property": "sender_balance >= 0",
      "description": "Sender balance must never go negative after transfer",
      "severity": "critical",
      "category": "postcondition"
    },
    {
      "property": "sender_balance + receiver_balance == old_sender + old_receiver",
      "description": "Total money in the system must be conserved",
      "severity": "critical",
      "category": "conservation"
    }
  ],
  "assumed_inputs": [
    {
      "property": "amount > 0",
      "description": "Transfer amount must be positive",
      "justification": "API contract: validated at HTTP handler before reaching this function",
      "source_type": "api_schema",
      "source_ref": "schemas/WithdrawRequest.amount",
      "evidence_id": "api-schema-withdraw-v3",
      "severity": "high"
    },
    {
      "property": "sender_balance >= 0",
      "description": "Sender starts with non-negative balance",
      "justification": "Database constraint enforces non-negative balances",
      "source_type": "db_constraint",
      "source_ref": "accounts.balance_check_nonnegative",
      "evidence_id": "db-check-accounts-balance",
      "severity": "high"
    }
  ],
  "loop_invariants": []
}
```

**Critical rule**: Obligations become proof **goals**. Assumed inputs become proof **hypotheses** only after evidence validation. The LLM prompt explicitly forbids moving properties between categories to make proofs easier, and policy validation enforces this mechanically.

### Invariant Categories

| Category | Description | Example |
|:---|:---|:---|
| **Non-negativity** | Numeric values stay above zero | `balance >= 0` after withdrawal |
| **Bounds checking** | Array/list indices stay in range | `0 <= index < len(array)` |
| **Uniqueness** | No duplicates in collections | `list.Nodup` after insertion |
| **Conservation** | Quantities are preserved | `sum_before == sum_after` |
| **Monotonicity** | Values only grow/shrink | `counter` only increases |
| **State transitions** | Only valid state changes occur | `PENDING → APPROVED` but never `APPROVED → PENDING` |
| **Type safety** | Values match expected types/ranges | `port ∈ [1, 65535]` |

---

## Translation Engine

Argus uses a **hybrid translation** approach: deterministic AST-based translation for simple code, and Gemini-powered translation for complex constructs.

### Layer 1: AST Translator (Deterministic)

The AST translator parses Python source code using Python's `ast` module and generates Lean 4 code via tree walking. **No LLM is involved** — this is 100% deterministic and reproducible.

**Supported constructs:**
- Function definitions with type annotations
- If/else/elif chains → Lean `if ... then ... else ...`
- Binary operations (`+`, `-`, `*`, `/`, `%`, `>`, `<`, `>=`, `<=`, `==`, `!=`)
- Boolean operations (`and`, `or`, `not`)
- Return statements
- Integer, float, bool, string literals
- Variable references
- Tuple returns → Lean product types (`A × B`)
- Guard patterns (sequential `if: return` → nested `if-then-else`)
- Reassignment patterns → Lean `let` bindings

**When to use**: Simple functions with basic arithmetic, conditionals, and no loops.

### Layer 2: LLM Translator (Gemini-Powered)

For constructs the AST translator can't handle, Gemini translates the Python to Lean 4 using a carefully crafted prompt with:
- Type mapping tables (Python types → Lean types)
- Operation mapping tables (Python operations → Lean equivalents)
- Anti-patterns ("NEVER translate it this way...")
- Import requirements (Mathlib tactics)
- Tactic strategies for proofs

**Supported constructs (beyond AST):**
- Lists (`List Int`, `List String`)
- Membership checks (`x in list` → `x ∈ list`)
- List operations (append, concatenation, slicing)
- Set operations
- Dict-like patterns
- Complex data transformations
- Comprehensions

**When to use**: Code with lists, sets, membership guards, or patterns the AST translator hasn't been programmed for.

### Layer 3: Dafny Translator (Loop Specialist)

For code with `for` or `while` loops, the Dafny translator converts Python loops into Dafny `while` loops with auto-generated `invariant` and `decreases` clauses.

**Why Dafny for loops:**
- Dafny has **first-class loop invariant syntax**: `while (i < n) invariant i >= 0 decreases n - i { ... }`
- Dafny uses the **Z3 SMT solver** to automatically discharge proof obligations
- Lean 4 requires modeling loops as recursive functions + induction proofs, which is harder to auto-generate

**Supported loop patterns:**
- `for x in range(n)` → Dafny `while (x < n)` with bounds invariants
- `for x in items` → Dafny indexed iteration with sequence length invariants
- `while condition` → Dafny `while` (requires `decreases` hint)
- Accumulator detection: `total += x` inside loops → automatic `invariant total >= 0`

### Translation Router

```python
def select_translator(code: str, invariants: list) -> Translator:
    if has_loops(code):
        return DafnyTranslator()  # Loops → Dafny (better invariant support)
    elif is_complex(code):
        return LLMTranslator()    # Complex constructs → Gemini
    else:
        return ASTTranslator()   # Simple code → deterministic
```

**Translator fallback (pre-verification only)**: If the AST translator cannot encode a construct, Argus may try LLM translation. If loops are present, Dafny translation is selected. This fallback happens **before** verification starts.

> **⚠️ Property normalization rule**: Regardless of which translator is selected, the **same canonical set of obligations and assumed inputs** is used. The translator converts the obligation into the target proof language (Lean theorem or Dafny postcondition), but the *property itself* does not change. This prevents "engine shopping" where a weaker encoding passes.

---

## Verification Engine

### Lean 4 Verifier

Lean 4 is a **dependently-typed programming language and interactive theorem prover**. When the Lean compiler accepts a proof, it is mathematically certain — not statistically likely, not "probably correct", but **proven**.

**How it works:**
1. Argus writes the translated Lean code to a temporary `.lean` file
2. Runs `lake env lean <filename>` within the Lean project (includes Mathlib)
3. Parses the compiler output:
   - **Exit code 0 + no `sorry`** → VERIFIED ✅
   - **Exit code ≠ 0** → VULNERABLE (with error message for repair)
   - **Contains `sorry`** → VULNERABLE (incomplete proof detected)

**Key tactics used:**
| Tactic | Purpose |
|:---|:---|
| `omega` | Solves linear arithmetic goals (e.g., `a + b >= 0`) |
| `split_ifs` | Breaks if-then-else into separate proof cases |
| `simp` | Simplification using known lemmas |
| `linarith` | Linear arithmetic reasoning (more powerful than omega) |
| `decide` | Decides decidable propositions |
| `unfold` | Expands function definitions |

### Dafny Verifier

Dafny is a **verification-aware programming language** backed by the Z3 SMT solver. It's purpose-built for proving program correctness, especially for imperative code with loops.

**How it works:**
1. Argus writes the translated Dafny code to a temporary `.dfy` file
2. Runs `dafny verify <filename>`
3. Parses the output:
   - All assertions verified → VERIFIED ✅
   - Verification errors → VULNERABLE (with error details for repair)

### Verification Router

The router selects the best engine for the code pattern but **never switches engines to avoid a failure**. Engine selection happens *before* verification based on code structure, not after a failure:

```python
def verify(code: str, obligations: list, engine: str = "auto") -> VerificationResult:
    # Engine is selected ONCE based on code structure, not switched on failure
    if engine == "auto":
        engine = "dafny" if has_loops(original_python) else "lean"

    if engine == "lean":
        result = lean_verifier.run(lean_code, obligations)
    elif engine == "dafny":
        result = dafny_verifier.run(dafny_code, obligations)

    # ALL obligations must pass — no partial pass
    result.all_passed = all(o.verified for o in result.obligation_results)
    return result
```

> **No fallback on failure**: If Lean fails to verify an obligation, Argus does **not** retry with Dafny (or vice versa). The engine is chosen based on code structure (loops → Dafny, everything else → Lean). A failure goes to the repair loop, not to a different engine. This prevents false confidence from weaker encodings.

### The `sorry` Problem

In Lean 4, `sorry` is a tactic that lets you skip a proof. It compiles but proves nothing. Argus treats any proof containing `sorry` as **VULNERABLE** — this prevents the LLM from "cheating" by inserting `sorry` to make proofs compile.

---

## AI Repair Engine

> **Soundness note**: The repair engine modifies the *Python code* to make the proof pass — it never modifies the proof obligations or assumptions. The repaired code is re-verified from scratch through the same translation and verification pipeline.

When verification fails, Argus uses Gemini to generate a fixed version of the Python code.

### Repair Prompt Strategy

The repair prompt (`src/prompts/repair_code.md`) provides Gemini with:

1. **The original Python code** that failed verification
2. **The Lean/Dafny error message** explaining *why* the proof failed
3. **The invariant that was violated** (from the discovery step)
4. **Common fix patterns** organized by category:
   - Financial: bounds checking, non-negative enforcement
   - Lists: membership checks before insertion, bounds before indexing
   - Loops: safe iteration limits, explicit bounds guards
   - State machines: valid transition enforcement

### Repair Loop

```
Attempt 1: Gemini generates fix → Translate → Verify
   If fail:
Attempt 2: Gemini sees previous error + its failed fix → New fix → Translate → Verify
   If fail:
Attempt 3: Final attempt with stronger constraints → Translate → Verify
   If fail:
Report as VULNERABLE with AI analysis of the issue
```

Each retry gives Gemini more context about what went wrong, increasing the success rate.

### Repair Output

The repair engine returns:
- **Fixed Python code** (raw, no markdown, directly saveable)
- **The Lean/Dafny proof** that verified the fix
- **Plain English explanation** of what the bug was and how it was fixed

---

## Observability & Traceability

Argus has no UI, but every run produces a structured **trace directory** (`.argus-trace/`) that persists all intermediate artifacts for debugging, audit, and reproducibility.

### Trace Directory Structure

Each pipeline run writes to `.argus-trace/<run-id>/`:

```text
.argus-trace/
└── 2026-02-17T13-10-44/
    ├── manifest.json              # Run metadata: git SHA, timestamps, config snapshot
    ├── files/
    │   └── withdraw.py/
    │       ├── 01_discovery.json   # Discovered obligations + assumed_inputs + prompt hash
    │       ├── 02_translation.lean # Generated Lean proof code
    │       ├── 03_verify_stdout.txt# Raw Lean/Dafny compiler output
    │       ├── 04_repair_0.py     # Repair attempt 0 (if needed)
    │       ├── 04_repair_0.lean   # Re-translation of repair attempt
    │       ├── 04_repair_0_verify.txt
    │       └── result.json        # Final verdict + timing + model version
    └── summary.json               # Aggregate results for all files
```

### What's Captured Per Stage

| Stage | Artifacts | Why |
|:---|:---|:---|
| **Discovery** | Prompt hash, model version, raw LLM response, parsed obligations/assumptions | Reproduce invariant discovery; detect prompt regressions |
| **Translation** | Generated Lean/Dafny code, translator type used (AST/LLM/Dafny) | Debug translation errors; compare AST vs LLM output |
| **Verification** | Raw compiler stdout/stderr, exit code, time elapsed | Diagnose proof failures; measure performance |
| **Repair** | Each attempt's Python fix + re-translated proof + verify output | Understand repair strategy; detect repair loops |
| **Decision** | Engine selection rationale, property normalization log | Audit why Lean vs Dafny was chosen |

### Cost & Time Budgets

Each `result.json` includes:

```json
{
  "file": "withdraw.py",
  "verdict": "FIXED",
  "timing": {
    "discovery_ms": 1200,
    "translation_ms": 50,
    "verification_ms": 3400,
    "repair_attempts": 1,
    "total_ms": 5800
  },
  "model": {
    "name": "gemini-2.5-pro",
    "prompt_tokens": 1420,
    "completion_tokens": 380
  },
  "toolchain": {
    "lean": "4.16.0",
    "mathlib": "2025-02-01",
    "dafny": "4.9.1"
  }
}
```

---

## CI Integrity Gates & Acceptance Criteria

Argus `VERIFIED` status is only emitted when all integrity gates pass in CI.

### Required Gates

| Gate | Check | Fail Condition |
|:---|:---|:---|
| `unsupported-construct-gate` | Detect unsupported Python constructs in changed files | Any unsupported construct in targeted code path |
| `obligation-policy-gate` | Canonical obligations generated deterministically from AST + policy pack | Nondeterministic obligation set across repeated runs |
| `assumption-evidence-gate` | Every assumption has valid `source_type`, `source_ref`, and `evidence_id` | Missing/invalid evidence metadata |
| `semantic-guard-gate` | Translation sanity checks pass (no known drift-risk transformations) | Guard violations on translated artifact |
| `proof-gate` | All canonical obligations prove with chosen engine | Any failed obligation |
| `verdict-contract-gate` | Verdict computed from strict contract logic | Contract mismatch or partial-pass leakage |
| `traceability-gate` | `.argus-trace/<run-id>/` contains required stage artifacts | Missing required trace artifacts |
| `reproducibility-gate` | Two CI reruns on same commit produce same canonical obligations and hashes | Hash mismatch |
| `mutation-gate` | Seeded mutation suite verifies expected failures on perturbed code | Kill rate below threshold |

### Minimum Acceptance Thresholds

| Metric | Threshold (V2.0) |
|:---|:---|
| Obligation determinism | 100% identical canonical obligation hashes across reruns |
| Assumption evidence coverage | 100% (no unevidenced assumptions) |
| Trace artifact completeness | 100% required files present |
| Mutation kill rate on critical rules | ≥95% |
| False-`VERIFIED` on seeded benchmark corpus | 0 known cases |
| Toolchain pinning drift | 0 unpinned core toolchain dependencies |

### Seeded Benchmark Requirement

CI includes a maintained corpus of:
1. Known vulnerable snippets expected to fail until repaired
2. Safe snippets expected to pass
3. Drift probes designed to catch translation mismatches

A release candidate cannot be tagged if benchmark expectations regress.

---

## Data Handling & Privacy

Argus sends Python source code to external LLM APIs (Gemini) for invariant discovery, translation, and repair. This creates data handling obligations, especially for regulated industries.

### Data Flow

| Data | Sent To | Purpose | Retention |
|:---|:---|:---|:---|
| Python source code (changed files only) | Gemini API | Invariant discovery, LLM translation, repair | Per Google AI API data retention policy (not used for training by default with API key) |
| Lean/Dafny proofs | Local only | Verification runs locally via subprocess | Ephemeral (temp files deleted after run) |
| MR metadata (file paths, branch names) | GitLab API | Posting comments, labels | Per GitLab data retention |

### Privacy Controls

| Control | Description | Config |
|:---|:---|:---|
| **File filtering** | Only changed Python files in the MR diff are analyzed — not the entire repo | Automatic |
| **`.argusignore`** | Exclude sensitive files/directories from analysis entirely | User-configured |
| **Redaction mode** | Strip string literals, comments, and docstrings before sending to LLM | `ARGUS_REDACT=true` |
| **Self-hosted inference** | Route LLM calls to a self-hosted Gemini endpoint (Vertex AI on GCP, or local model) | `ARGUS_LLM_ENDPOINT=<url>` |
| **Audit log** | All LLM interactions are logged in `.argus-trace/` with prompt hashes | Always on |

### Enterprise Path

For organizations that cannot send code to external APIs:
1. **Vertex AI**: Use Gemini on your own GCP project with data residency controls
2. **Air-gapped mode**: Use the AST translator only (no LLM calls) — limited to simple constructs but fully local
3. **On-prem deployment**: Run Argus in your own infrastructure with self-hosted models

---

## Reporting & MR Integration

### Report Types

| Format | Purpose | Destination |
|:---|:---|:---|
| **MR Comment** | Human-readable summary with inline suggestions | GitLab MR thread |
| **SARIF** | Machine-readable security findings | GitLab Security Dashboard |
| **Markdown** | Detailed audit report with proofs | Pipeline artifact |
| **JSON** | Structured data for programmatic consumption | Pipeline artifact |

### MR Comment Structure

```markdown
## 🛡️ Argus Formal Verification Report

**Commit**: `abc1234` | **Files Audited**: 5 | **Time**: 42s

### Results

| File | Status | Invariants Checked | Finding |
|:---|:---|:---|:---|
| `ledger.py` | ✅ VERIFIED | 3/3 | All safety properties proven |
| `withdraw.py` | ⚠️ → ✅ FIXED | 2/2 | Missing bounds check (auto-fixed) |
| `auth.py` | ❌ VULNERABLE | 1/3 | Unauthorized state transition possible |

### 🔐 Secrets Scan
No hardcoded secrets detected.

---

<details>
<summary>📐 View Mathematical Proofs</summary>

#### withdraw.py — balance_non_negative
```lean
theorem balance_non_negative (balance amount : Int)
  (h_bal : balance ≥ 0) (h_amt : amount ≥ 0) :
  withdraw balance amount ≥ 0 := by
  unfold withdraw; split_ifs <;> omega
```
**Proof status**: ✅ Verified by Lean 4 compiler
</details>
```

### Labels

Argus applies GitLab labels to the MR based on results:
- `argus:verified` — All files pass verification
- `argus:vulnerable` — One or more files have unresolvable vulnerabilities
- `argus:fixed` — Vulnerabilities found and auto-fixed

---

## Directory Structure

```text
ArgusV2/
├── src/
│   ├── core/                          # Platform-agnostic verification engine
│   │   ├── __init__.py
│   │   ├── pipeline.py                # Orchestrates: discover → translate → verify → repair
│   │   ├── obligation_policy.py       # Deterministic canonical obligation generation
│   │   ├── assumption_evidence.py     # Assumption provenance validation
│   │   ├── invariant_discovery.py     # Gemini: analyze code → discover safety properties
│   │   ├── semantic_guard.py          # Translation drift-risk checks
│   │   ├── verdict.py                 # Fail-closed verdict contract enforcement
│   │   ├── translator/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Abstract translator interface
│   │   │   ├── ast_translator.py      # Deterministic Python→Lean (AST-based, no LLM)
│   │   │   ├── llm_translator.py      # Gemini-powered Python→Lean (complex constructs)
│   │   │   └── dafny_translator.py    # Python→Dafny (loops/iteration specialist)
│   │   ├── verifier/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Abstract verifier interface
│   │   │   ├── lean_verifier.py       # Lean 4 subprocess driver
│   │   │   ├── dafny_verifier.py      # Dafny subprocess driver
│   │   │   └── router.py             # Smart engine selection logic
│   │   ├── repair.py                  # Gemini-powered fix generation + re-verify loop
│   │   └── reporter.py               # SARIF, JSON, Markdown, MR comment generation
│   │
│   ├── prompts/                       # All LLM prompts as versioned files
│   │   ├── discover_invariants.md     # "What safety properties does this code need?"
│   │   ├── translate_lean.md          # "Convert this Python to Lean 4"
│   │   ├── translate_lean_advanced.md # "Convert complex Python (lists, sets) to Lean 4"
│   │   ├── translate_dafny.md         # "Convert Python loops to Dafny" (if LLM-assisted)
│   │   ├── repair_code.md            # "Fix this Python based on verification error"
│   │   └── explain_vulnerability.md   # "Explain this bug in plain English"
│   │
│   ├── adapters/                      # Platform integrations (thin layers)
│   │   ├── __init__.py
│   │   ├── gitlab_adapter.py          # GitLab MR comments, labels, SARIF upload
│   │   ├── github_adapter.py          # GitHub PR comments, Actions integration (future)
│   │   └── cli.py                     # CLI entry point for local dev/testing/CI
│   │
│   └── utils/
│       ├── __init__.py
│       ├── git_ops.py                 # Repo clone, diff detection, file filtering
│       ├── secrets_scanner.py         # Regex-based secret detection
│       └── file_router.py            # .argusignore support, Python file discovery
│
├── lean_project/                      # Lean 4 project environment
│   ├── lakefile.lean                  # Lake build file (includes Mathlib dependency)
│   ├── lean-toolchain                 # Lean version pinning
│   └── LeanProject.lean              # Root file
│
├── demo_target/                       # Vulnerable demo code for testing/video
│   ├── fintech_ledger.py             # Financial bugs: negative balance, overflow
│   ├── auth_state.py                 # State machine bugs: invalid transitions
│   └── inventory.py                  # List bugs: duplicates, bounds
│
├── tests/
│   ├── test_pipeline.py              # End-to-end pipeline tests
│   ├── test_obligation_policy.py     # Deterministic obligation generation tests
│   ├── test_assumption_evidence.py   # Assumption evidence validator tests
│   ├── test_invariant_discovery.py   # Invariant extraction tests
│   ├── test_ast_translator.py        # AST translation unit tests
│   ├── test_llm_translator.py        # LLM translation tests (mocked)
│   ├── test_semantic_guard.py        # Translation guard tests
│   ├── test_lean_verifier.py         # Lean verification tests
│   ├── test_dafny_verifier.py        # Dafny verification tests
│   ├── test_repair.py               # Repair loop tests
│   ├── test_verdict_contract.py      # Fail-closed verdict tests
│   ├── test_mutation_gate.py         # Mutation benchmark gate tests
│   ├── test_reproducibility.py       # Same-commit determinism tests
│   └── test_reporter.py              # Report generation tests
│
├── .gitlab/
│   └── duo/
│       └── agent-config.yml          # Duo Flow Docker image + setup
│
├── legacy/                            # V1 code preserved for reference
│   └── ...
│
├── Dockerfile                         # Python + Lean 4 + Dafny runtime
├── requirements.txt                   # Python dependencies
├── .argusignore.example               # Example ignore file for users
└── README.md
```

---

## Tech Stack

| Component | Technology | Version | Purpose |
|:---|:---|:---|:---|
| **Runtime** | Python | 3.11 (pinned in Dockerfile) | Core orchestration language |
| **AI Engine** | Google Gemini | gemini-2.5-pro / gemini-2.5-flash | Invariant discovery, translation, repair |
| **AI SDK** | `google-genai` | ≥1.0.0 | Current Gemini SDK (replaces deprecated `google-generativeai`) |
| **Proof Engine (Primary)** | Lean 4 | 4.16.0 (pinned in `lean-toolchain`) | Mathematical formal verification |
| **Proof Library** | Mathlib4 | Pinned commit in `lakefile.lean` | Tactics and lemmas for Lean proofs |
| **Proof Engine (Secondary)** | Dafny | 4.9.1 (pinned in Dockerfile) | Loop verification with Z3 SMT solver |
| **Platform** | GitLab Duo Agent Platform | 18.8+ | Custom Flow hosting and MR integration |
| **Container** | Docker | - | Reproducible environment with all toolchains |
| **Report Format** | SARIF 2.1.0 + GitLab SAST schema | - | Security Dashboard integration |
| **Secret Scanning** | Regex patterns | - | Hardcoded API keys, tokens, passwords |

### Reproducibility Manifest

All toolchain versions are pinned to ensure deterministic builds:

| File | Pins |
|:---|:---|
| `lean-toolchain` | Exact Lean 4 version (e.g., `leanprover/lean4:v4.16.0`) |
| `lakefile.lean` | Mathlib commit hash |
| `Dockerfile` | Python version, Dafny version, elan version |
| `requirements.txt` | All Python dependencies with `==` pins |
| `src/prompts/*.md` | Prompts are versioned files; changes tracked in git history |

### Python Dependencies

```
google-genai==1.0.0       # Gemini API client (current SDK)
python-gitlab==4.4.0      # GitLab API client
python-dotenv==1.0.1      # Environment variable management
pathspec==0.12.1          # .argusignore gitignore-style matching
gitpython==3.1.43         # Git operations
pydantic==2.10.0          # Data validation for pipeline stages
pytest==8.3.0             # Testing framework
```

---

## Supported Python Constructs

### Fully Supported (AST Translator)

| Construct | Example | Lean 4 Translation |
|:---|:---|:---|
| Functions | `def foo(x: int) -> int:` | `def foo (x : Int) : Int :=` |
| If/else | `if x > 0: return x` | `if x > 0 then x else ...` |
| Arithmetic | `a + b - c * d` | `a + b - c * d` |
| Comparisons | `x >= 0 and y < 10` | `x ≥ 0 ∧ y < 10` |
| Guard patterns | sequential `if: return` | nested `if-then-else` |
| Type annotations | `int`, `float`, `bool`, `str` | `Int`, `Float`, `Bool`, `String` |
| Tuple returns | `return x, y` | `(x, y) : Int × Int` |

### Supported via LLM (Gemini Translator)

| Construct | Example | Lean 4 Translation |
|:---|:---|:---|
| Lists | `List[int]` | `List Int` |
| Membership | `x in my_list` | `x ∈ my_list` |
| List append | `list + [item]` | `list ++ [item]` |
| Set operations | `set()`, `x not in s` | `Finset`, `x ∉ s` |
| List comprehensions | `[x for x in items if x > 0]` | `items.filter (· > 0)` |
| Complex logic | Multi-step data transformations | Context-dependent |

### Supported via Dafny (Loop Translator)

| Construct | Example | Dafny Translation |
|:---|:---|:---|
| Range loops | `for i in range(n):` | `while (i < n) invariant ... { ... }` |
| Sequence iteration | `for x in items:` | `while (idx < |items|) { var x := items[idx]; ... }` |
| Accumulation | `total += x` | Auto-generates `invariant total >= 0` |
| While loops | `while condition:` | `while (condition) { ... }` |

### Not Supported (Out of Scope)

- Classes and object-oriented patterns
- `async` / `await`
- External library calls (NumPy, Pandas, etc.)
- Dynamic typing without annotations
- Metaclasses, decorators, generators

---

## Configuration

### For Users (Target Repositories)

Users add an `.argusignore` file to their repo root (gitignore syntax):

```gitignore
# Don't audit test files
tests/
test_*.py

# Skip generated code
*_pb2.py
migrations/

# Skip specific files
config.py
```

### Environment Variables

| Variable | Required | Description |
|:---|:---|:---|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key for Gemini |
| `GITLAB_TOKEN` | Yes (for GitLab) | GitLab API token for MR comments/labels |
| `GITHUB_TOKEN` | Yes (for GitHub) | GitHub API token for PR comments |
| `ARGUS_MAX_REPAIR_ATTEMPTS` | No (default: 3) | Max repair loop iterations |
| `ARGUS_VERIFICATION_TIMEOUT` | No (default: 60s) | Lean/Dafny compiler timeout |
| `ARGUS_MODEL` | No (default: gemini-2.5-pro) | Gemini model to use |

---

## Demo Scenarios

### Scenario 1: The Billion-Dollar Bug (Financial)

**File**: `fintech_ledger.py`

```python
def withdraw(balance: int, amount: int) -> int:
    """Process a withdrawal from an account."""
    return balance - amount  # BUG: No bounds check!
```

**Argus finds**: Balance can go negative. **Argus fixes**: Adds `if amount > balance: return balance` guard.

### Scenario 2: The State Machine Breach (Security)

**File**: `auth_state.py`

```python
def update_access(current_level: int, requested_level: int) -> int:
    """Update user access level."""
    return requested_level  # BUG: No authorization check!
```

**Argus finds**: Unrestricted privilege escalation. **Argus fixes**: Adds `if requested_level > current_level + 1: return current_level` guard (level can only increase by 1).

### Scenario 3: The Duplicate Data Bug (Data Integrity)

**File**: `inventory.py`

```python
def add_product_id(existing_ids: list, new_id: int) -> list:
    """Add a new product ID to the inventory list."""
    return existing_ids + [new_id]  # BUG: No duplicate check!
```

**Argus finds**: List can contain duplicates. **Argus fixes**: Adds `if new_id in existing_ids: return existing_ids` guard.

---

## Hackathon Submission

### GitLab AI Hackathon Details

| Item | Detail |
|:---|:---|
| **Category** | GitLab Duo Custom Agents & Flows |
| **Deadline** | March 25, 2026, 2:00 PM EDT |
| **Requirements** | Public source code (open-source), description, 3-min demo video |
| **Judging Criteria** | Tech implementation (tools, triggers, code quality), Design & UX (ease of install/config), Potential Impact, Idea Quality |

### Submission Deliverables

1. **Public GitLab project** with source code under open-source license
2. **Functional Duo Custom Flow** that can be installed on any GitLab project
3. **Demo video** (≤3 min) showing:
   - Pushing vulnerable code to an MR
   - Argus automatically detecting the bug
   - Argus posting the fix with mathematical proof
   - The fix being verified
4. **README** with installation instructions

---

## Startup Vision

### Beyond the Hackathon

Argus V2 is designed from day one as a **startup product**, not a hackathon demo.

**Target customers**: Enterprises in regulated industries where software bugs have catastrophic consequences:
- **FinTech**: Trading algorithms, payment processing, ledger systems
- **Healthcare**: Medical device software, drug dosing algorithms
- **Aerospace/Defense**: Flight control systems, autonomous vehicles
- **Critical Infrastructure**: Power grid control, water treatment systems

**Competitive moat**:
1. **Network effects on prompts**: Every bug Argus finds improves the invariant discovery and repair prompts for all future users
2. **Proof library**: Accumulated verified proofs become a searchable knowledge base of proven patterns
3. **Platform integration**: Native GitLab/GitHub integration means zero-friction adoption
4. **Mathematical certainty within scope**: Within the [soundness envelope](#soundness-envelope), a Lean proof is either valid or it isn't — unlike static analyzers (Snyk, SonarQube) that rely on heuristics and produce false positives. Outside the envelope, Argus clearly reports what was and wasn't verified.

**Pricing model** (future):
- **Free tier**: 5 files per MR, 50 verifications/month
- **Pro tier**: Unlimited files, priority verification, custom invariant rules
- **Enterprise**: On-prem deployment, SOC2/HIPAA compliance reporting, dedicated support

### Scaling Roadmap

| Phase | Scope | Timeline |
|:---|:---|:---|
| **V2.0** | GitLab Duo Flow, Lean 4 + Dafny, invariant discovery | March 2026 |
| **V2.1** | GitHub Actions support, expanded Python construct coverage | April 2026 |
| **V2.2** | Multi-language support (TypeScript/JavaScript) | Summer 2026 |
| **V3.0** | Custom invariant rules for enterprises, proof library marketplace | Fall 2026 |

---

## Development Roadmap

### Phase 1: Core Engine (Weeks 1-2)
- [ ] Set up project structure (`src/core/`, `src/prompts/`, `src/adapters/`)
- [ ] Build deterministic obligation policy engine (`src/core/obligation_policy.py`)
- [ ] Build assumption evidence validator (`src/core/assumption_evidence.py`)
- [ ] Port and refactor AST translator from V1 → `src/core/translator/ast_translator.py`
- [ ] Port and refactor Lean verifier from V1 → `src/core/verifier/lean_verifier.py`
- [ ] Port and refactor Dafny translator + verifier from V1
- [ ] Build the verification router (`src/core/verifier/router.py`)
- [ ] Build the invariant discovery module (`src/core/invariant_discovery.py`)
- [ ] Build semantic guard module for translation sanity checks (`src/core/semantic_guard.py`)
- [ ] Build verdict contract module (`src/core/verdict.py`)
- [ ] Externalize all prompts to `src/prompts/`

### Phase 2: Pipeline & Repair (Weeks 2-3)
- [ ] Build the orchestration pipeline (`src/core/pipeline.py`)
- [ ] Port and refactor repair engine from V1 → `src/core/repair.py`
- [ ] Build the reporter module (SARIF, Markdown, JSON)
- [ ] Add assumption/evidence rendering to MR reports (what was assumed vs proven)
- [ ] Add `.argus-trace/` artifact writer for all stages
- [ ] Build CLI adapter for local testing (`src/adapters/cli.py`)
- [ ] Create demo target files
- [ ] Write unit tests for all core modules

### Phase 3: GitLab Integration (Weeks 3-4)
- [ ] Build GitLab adapter (`src/adapters/gitlab_adapter.py`)
- [ ] Create Duo Custom Flow configuration
- [ ] Build Dockerfile with Lean 4 + Dafny + Python
- [ ] Create `.gitlab-ci.yml` for CI-based triggering
- [ ] Implement CI integrity gates (unsupported construct, obligation determinism, evidence coverage, semantic guard, reproducibility)
- [ ] Add seeded benchmark corpus and mutation gate in CI
- [ ] Test end-to-end on a real GitLab MR
- [ ] Deploy to GitLab AI Catalog

### Phase 4: Polish & Submit (Week 5)
- [ ] End-to-end integration tests
- [ ] Verify acceptance thresholds from `CI Integrity Gates & Acceptance Criteria`
- [ ] Demo video recording (3 min)
- [ ] Final README with installation instructions
- [ ] Open-source license
- [ ] Submit to GitLab AI Hackathon



# ArgusV2 — Product Requirements Document (PRD)

## Overview

**Product Name:** ArgusV2  
**Category:** AI DevSecOps Agent with Formal Verification  
**Primary Platform:** GitLab (compatible with GitHub-style workflows conceptually)

### Core Idea
ArgusV2 is an autonomous DevOps security agent that integrates **formal verification with AI-driven code repair** to ensure that critical security invariants are preserved after every commit.

When developers push code, ArgusV2:

1. Identifies security-critical functions
2. Extracts formal specifications or invariants
3. Runs formal verification (Lean/Dafny)
4. Detects proof failures
5. Uses an LLM to analyze the failure
6. Generates a secure patch
7. Re-runs verification
8. Opens a Merge Request with explanation and fix

Unlike traditional AI code assistants that **guess**, ArgusV2 **proves correctness** for security-critical logic.

---

# 1. Vision

Modern DevOps pipelines rely heavily on automated testing and vulnerability scanners, but these tools cannot guarantee logical correctness or invariant preservation.

ArgusV2 introduces **formal reasoning into everyday development pipelines**, enabling teams to catch and automatically repair security-critical logic errors immediately after commits.

The long-term vision is an **AI-powered DevSecOps system capable of proving security properties and autonomously maintaining them across the software lifecycle.**

---

# 2. Goals

## Primary Goals

- Ensure **security invariants remain true across commits**
- Automatically detect **logical security violations**
- Automatically generate **secure code patches**
- Integrate seamlessly into **GitLab CI/CD workflows**
- Provide **explainable security reasoning**

## Secondary Goals

- Demonstrate feasibility of **AI + Formal Methods integration**
- Reduce time spent on **security debugging**
- Improve **developer trust in AI generated fixes**
- Enable **verifiable autonomous DevOps workflows**

---

# 3. Non-Goals

ArgusV2 will **not** attempt to:

- Fully verify arbitrary Python programs
- Replace traditional unit tests
- Perform full system theorem proving
- Automatically generate full formal specifications for complex applications

The system focuses on **security-critical modules with defined invariants.**

---

# 4. Problem Statement

Current DevOps pipelines rely on:

- Static analyzers
- Security scanners
- Unit tests
- LLM suggestions

However, these approaches cannot guarantee logical correctness.

### Example Failure

A developer accidentally removes an authorization check:

```python
def transfer_funds(user, from_account, to_account, amount):
    # missing ownership / permission check
    from_account.balance -= amount
    to_account.balance += amount

Tests may still pass, and security scanners may detect nothing, but the system becomes exploitable.

The root problem:

Security invariants are rarely formally enforced.

Examples of invariants:

Users cannot access accounts they do not own

Balances cannot become negative

Access tokens must be validated before state changes

State transitions must follow defined rules

ArgusV2 ensures that these invariants are provably preserved.

5. Target Users
Primary Users

Backend engineers

DevOps engineers

Security engineers

Platform engineering teams

Secondary Users

FinTech engineering teams

Healthcare software teams

Enterprise SaaS teams

High security environments

6. Key Value Proposition

ArgusV2 combines three technologies rarely used together:

Formal Verification

AI Reasoning

Automated DevOps Actions

Instead of:

AI suggests a fix

ArgusV2 provides:

Proof failure → AI diagnosis → verified repair

This produces trustworthy autonomous security fixes.

7. Core Features
7.1 Verification Agent
Description

The Verification Agent analyzes commits and verifies security invariants using formal methods.

Responsibilities

Detect security-critical functions

Extract specifications

Translate logic to verification model

Run Lean/Dafny verification

Trigger

Commit pushed

Merge request opened

Output

Pass verification

Proof failure report


7.2 Proof Diagnosis Agent
Description

When verification fails, this agent interprets proof errors and maps them back to the source code.

Responsibilities

Analyze proof failure

Identify violated invariant

Identify responsible code changes

Explain the failure

Example Output
Invariant violation detected:

User must own account before transfer.

Removed check:
if account.owner != user:
    raise UnauthorizedError


7.3 Secure Repair Agent
Description

Uses LLM reasoning to generate minimal patches that restore the violated invariant.

Responsibilities

Propose secure fix

Maintain minimal code changes

Preserve functionality

Re-run verification

Example Patch
if from_account.owner != user:
    raise UnauthorizedError


7.4 Verification Recheck

After repair:

Formal verification runs again.

If proof succeeds, patch is accepted.

7.5 Merge Request Generator

ArgusV2 automatically creates a merge request containing:

explanation

proof failure analysis

generated fix

verification results

Example MR Message
ArgusV2 Security Patch

Invariant violated:
Users cannot transfer funds from accounts they do not own.

Fix:
Restored ownership verification before balance mutation.

Verification:
Proof succeeded after patch.

8. Security Invariants Supported

Examples ArgusV2 can enforce:

Authorization
User must own resource before mutation
Financial Safety
Account balance >= 0
State Machine Validity
Order must be PAID before SHIPPED
Input Validation
Sanitized input required before DB query
Access Control
Token must be verified before protected action



9. Architecture
High Level System
GitLab Events
      ↓
Event Router
      ↓
Agent Orchestrator
      ↓
Verification Agent
      ↓
Proof Diagnosis Agent
      ↓
Secure Repair Agent
      ↓
Verification Recheck
      ↓
Merge Request Generator


10. Technical Stack
Backend

Python

FastAPI

Agent Orchestration

LangGraph or custom orchestration engine

Formal Verification

Lean

Dafny

LLM

Anthropic Claude (flexible)

Git Integration

GitLab API

GitLab Webhooks

GitLab CI/CD

11. Workflow Example
Scenario

A developer pushes a commit removing authorization logic.

Step 1

Commit pushed.

Step 2

Verification Agent detects invariant violation.

Step 3

Proof fails.

Step 4

Proof Diagnosis Agent analyzes failure.

Step 5

Secure Repair Agent proposes fix.

Step 6

Verification reruns.

Step 7

Merge request automatically created.

12. Demo Scenario (Hackathon)

Demo narrative:

Introduce security invariant.

Show working system.

Push commit breaking invariant.

Verification fails.

ArgusV2 diagnoses issue.

Patch generated.

Verification passes.

Merge request created.

Total demo time: ~2 minutes

This produces a clear and impressive demonstration.

13. Success Metrics
Technical

Verification accuracy

Repair success rate

Proof runtime

Developer Experience

Time saved fixing vulnerabilities

Reduction in security regressions

14. Risks
Technical Complexity

Formal verification translation may fail for complex Python constructs.

Mitigation

Limit verification to:

critical modules

pure functions

defined contracts

Incorrect AI Fixes

AI patches may not preserve semantics.

Mitigation

Re-run verification before accepting patch.

15. Future Roadmap
Phase 2

automatic invariant discovery

deeper AST verification

multi-language support

Phase 3

full DevSecOps agent ecosystem

compliance verification

incident response agents

16. Competitive Advantage

Traditional security tools rely on:

pattern-based detection

ArgusV2 relies on:

proof-based reasoning

Traditional AI assistants:

guess fixes

ArgusV2:

generate fixes that satisfy formal proofs

This combination makes ArgusV2 uniquely powerful.

18. One Sentence Summary

ArgusV2 is an AI DevSecOps agent that proves security invariants after every commit and automatically repairs code when those proofs fail.


19. Extra Clarification

Agents
1. Verification Agent

triggered on commit / PR

identifies critical functions

extracts specs/invariants

runs proof checks

2. Proof Diagnosis Agent

reads failed proof / counterexample

explains what invariant broke

maps failure back to source code

3. Secure Repair Agent

proposes minimal patch

re-runs verification

opens PR if proof passes

4. Risk Scoring Agent

prioritizes modules by impact

decides when formal verification is worth running
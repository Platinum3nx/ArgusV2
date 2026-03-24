# postFinalPlan.md — ArgusV2 Technical Hardening Plan (Post FinalPlan)

Date: 2026-03-19
Purpose: Close remaining technical risk before submission and improve real-world product reliability for engineering teams.

---

## Goals

1. Eliminate correctness ambiguity in UI and CI integrity checks.
2. Harden hosted proxy behavior for abuse resistance and operational reliability.
3. Increase confidence via targeted failure-mode testing.
4. Improve production readiness (token lifecycle, observability, quotas).

---

## Priority P0 (Must-Do ASAP)

### P0.1 — Fix Dashboard obligation default status (PASS -> UNKNOWN)

**Problem**
`src/core/dashboard.py` currently defaults missing obligation results to `PASS`:
- Line 523: `verified = result_map.get(obl_id, True)`
- Line 451: `failed = [o for o in obligations if not o.get("verified", True)]`

If result data is absent, UI can mislead users into thinking an obligation passed.

**Detailed Plan**

1. **`src/core/dashboard.py` — `_render_obligation_table()` (line 508-542)**
   - Change line 523 from `result_map.get(obl_id, True)` to `result_map.get(obl_id, None)`.
   - Update the status_html rendering (line 524) to handle three states:
     ```python
     if verified is None:
         status_html = "<span class='obl-unknown'>UNKNOWN</span>"
     elif verified:
         status_html = "<span class='obl-pass'>PASS</span>"
     else:
         status_html = "<span class='obl-fail'>FAIL</span>"
     ```

2. **`src/core/dashboard.py` — `_action_guidance()` (line 449-468)**
   - Change line 451 from `o.get("verified", True)` to `o.get("verified", False)` so missing results are treated as failures for action guidance purposes (fail-closed).

3. **`src/core/dashboard.py` — CSS (line 21-347)**
   - Add a new CSS class for UNKNOWN status after `.obl-fail` (around line 250):
     ```css
     .obl-unknown { color: var(--unverified); font-weight: 700; }
     ```

4. **`tests/test_dashboard.py`**
   - Add a test case where `obligation_results` is an empty list but `obligations` has entries. Assert the rendered HTML contains `UNKNOWN`, not `PASS`.
   - Add a test case where some obligations have results and others don't. Assert mixed PASS/UNKNOWN rendering.

---

### P0.2 — Fix mutation gate verifier-routing mismatch

**Problem**
In `src/core/ci_integrity.py:389-416`, `_evaluate_mutation_with_lean()` translates loop code with `DafnyTranslator()` (line 402) but always verifies with `LeanVerifier()` (line 409). Dafny syntax fed to Lean always fails.

**Detailed Plan**

1. **`src/core/ci_integrity.py` — `_evaluate_mutation_with_lean()` (line 389-416)**
   - Add `from .verifier import DafnyVerifier` to the imports (line 20 area).
   - Replace the fixed `LeanVerifier` at line 409-410 with engine-matched routing:
     ```python
     if _contains_loop(code):
         translation = DafnyTranslator().translate(code, policy_result.obligations, preconditions)
         verifier = DafnyVerifier(require_docker=False)
     else:
         translation = ASTTranslator().translate(code, policy_result.obligations, preconditions)
         verifier = LeanVerifier(require_docker=False)

     if not translation.success:
         return Verdict.UNVERIFIED

     result = verifier.verify(translation.code, policy_result.obligations)
     ```

2. **`tests/test_mutation_gate.py`**
   - Add a test with loop-containing code (e.g., `for i in range(n): total += i`).
   - Mock both `DafnyVerifier` and `LeanVerifier`.
   - Assert that `DafnyVerifier.verify` is called (not `LeanVerifier.verify`) when the code has loops.

---

### P0.3 — Proxy request size guardrails

**Problem**
`proxy/main.py:123-126` — `GenerateRequest` has no size constraints on `prompt`, `max_tokens`, or `model`.

**Detailed Plan**

1. **`proxy/main.py` — Add env-configurable limits (top of file, after line 20)**
   ```python
   MAX_PROMPT_CHARS = int(os.environ.get("ARGUS_MAX_PROMPT_CHARS", "80000"))
   MAX_TOKENS_CEILING = int(os.environ.get("ARGUS_MAX_TOKENS_CEILING", "16384"))
   ALLOWED_MODELS = {"claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-6"}
   ```

2. **`proxy/main.py` — Add validation to `GenerateRequest` model (line 123-126)**
   Use Pydantic `field_validator` or add manual validation in the endpoint:
   ```python
   class GenerateRequest(BaseModel):
       prompt: str
       model: str = "claude-sonnet-4-6"
       max_tokens: int = 4096
   ```

3. **`proxy/main.py` — Add validation at the top of `generate()` endpoint (after line 160)**
   ```python
   if len(body.prompt) > MAX_PROMPT_CHARS:
       raise HTTPException(
           status_code=413,
           detail=f"Prompt exceeds maximum size ({len(body.prompt)}/{MAX_PROMPT_CHARS} chars).",
       )
   body.max_tokens = min(body.max_tokens, MAX_TOKENS_CEILING)
   if body.model not in ALLOWED_MODELS:
       raise HTTPException(status_code=422, detail=f"Model '{body.model}' is not allowed.")
   ```

4. **Tests** (new file `tests/test_proxy.py` or inline in existing test)
   - Test oversized prompt returns 413.
   - Test `max_tokens` gets clamped to ceiling.
   - Test disallowed model returns 422.

---

### P0.4 — Retry behavior hardening (Retry-After + jitter)

**Problem**
`src/core/llm_provider.py:80` — backoff is deterministic (`BACKOFF_BASE ** attempt`, always 2/4/8s). No jitter. No `Retry-After` header support.

**Detailed Plan**

1. **`src/core/llm_provider.py` — Add `import random` at the top (line 1 area).**

2. **`src/core/llm_provider.py` — Replace the wait calculation at line 80-82:**
   ```python
   # Honor Retry-After header if present on 429 responses
   retry_after = None
   if isinstance(last_exc, requests.HTTPError) and hasattr(last_exc, 'response') and last_exc.response is not None:
       retry_after = last_exc.response.headers.get("Retry-After")

   if retry_after is not None:
       try:
           wait = min(float(retry_after), 60)
       except (ValueError, TypeError):
           wait = BACKOFF_BASE ** attempt
   else:
       wait = BACKOFF_BASE ** attempt

   # Add bounded jitter: +/- 25% of base wait
   jitter = wait * 0.25 * (2 * random.random() - 1)
   wait = max(1, wait + jitter)
   ```

3. **`tests/test_llm_provider.py`**
   - Add test: mock a 429 response with `Retry-After: 5` header. Assert sleep is called with a value near 5 (within jitter bounds).
   - Add test: verify jitter produces non-identical waits across multiple invocations.
   - Add test: verify `Retry-After` values above 60 are clamped.

---

## Audit-Discovered P0 Items

### A0.1 — Pipeline translation/verification engine decoupling

**Problem**
In `src/core/pipeline.py`, translation (lines 427-440) and verification (lines 238-243) engines are selected via independent code paths. If `DafnyTranslator` fails and `LLMTranslator` fallback produces Lean code, the router at line 238 still picks `DafnyVerifier`.

**Detailed Plan**

1. **`src/core/pipeline.py` — Replace lines 238-243:**
   Remove the independent `router.select_engine()` call. Use `translation.language` directly:
   ```python
   # was: engine_selection = self.router.select_engine(python_code)
   verification = (
       self.lean_verifier.verify(translation.code, policy.obligations)
       if translation.language == "lean"
       else self.dafny_verifier.verify(translation.code, policy.obligations)
   )
   ```

2. **`src/core/pipeline.py` — Update `engine` field in finalize result (line 384):**
   Replace `engine=engine_selection.engine` with `engine=translation.language`.

3. **`tests/test_pipeline.py`**
   - Add test: mock `DafnyTranslator.translate()` to return `success=False`, and `LLMTranslator.translate()` to return `language="lean"`. Assert `LeanVerifier.verify` is called, not `DafnyVerifier.verify`.

---

### A0.2 — ValueError escapes retry loop in LLM client

**Problem**
`src/core/llm_provider.py:74` raises `ValueError` for invalid payloads. The `except` at line 77 only catches `requests.ConnectionError` and `requests.Timeout`, so `ValueError` escapes the retry loop.

**Detailed Plan**

1. **`src/core/llm_provider.py` — Expand the except clause at line 77:**
   ```python
   except (requests.ConnectionError, requests.Timeout, ValueError) as exc:
       last_exc = exc
   ```

2. **`tests/test_llm_provider.py`**
   - Add test: mock proxy to return 200 with `{"wrong_key": "value"}` on first call, valid response on second. Assert retry happens and final result is valid.
   - Add test: mock proxy to return 200 with non-JSON body. Assert retry happens.

---

### A0.3 — DafnyTranslator silently drops assumptions

**Problem**
`src/core/translator/dafny_translator.py:56` — `_translate_loop_fallback()` never receives `assumptions`. Preconditions are lost for loop code.

**Detailed Plan**

1. **`src/core/translator/dafny_translator.py` — Pass assumptions on line 56:**
   ```python
   return self._translate_loop_fallback(python_code, obligations, assumptions)
   ```

2. **`src/core/translator/dafny_translator.py` — Update `_translate_loop_fallback` signature (line 58-62):**
   ```python
   def _translate_loop_fallback(
       self,
       python_code: str,
       obligations: List[Obligation],
       assumptions: List[AssumedInput],
   ) -> TranslationOutcome:
   ```

3. **`src/core/translator/dafny_translator.py` — Pass assumptions to `_translate_function` (line 78):**
   ```python
   methods.append(self._translate_function(node, obligations, assumptions))
   ```

4. **`src/core/translator/dafny_translator.py` — Update `_translate_function` (line 105) to accept and emit assumptions:**
   ```python
   def _translate_function(self, fn: ast.FunctionDef, obligations: List[Obligation], assumptions: List[AssumedInput]) -> str:
   ```
   After the params/return_type lines (line 117), before the `lines.append("{")` (line 123), add:
   ```python
   for assumption in assumptions:
       lines.append(f"  requires {assumption.property}")
   ```

5. **`tests/test_dafny_translator.py`**
   - Add test: translate code with assumptions. Assert `requires` clauses appear in output.
   - Add test: translate loop code with assumptions via fallback path. Assert `requires` clauses appear.

---

### A0.4 — Semantic guard silently passes on unrecognized code format

**Problem**
`src/core/semantic_guard.py:63-64` — if translated code matches neither Lean (`theorem`/`def`) nor Dafny (`method`) keywords, all per-obligation checks skip silently. Guard returns `passed=True` incorrectly.

**Detailed Plan**

1. **`src/core/semantic_guard.py` — Add unrecognized format check after line 64:**
   ```python
   is_lean = bool(re.search(r"\btheorem\b|\bdef\b", stripped))
   is_dafny = bool(re.search(r"\bmethod\b", stripped))

   if obligations and not is_lean and not is_dafny:
       issues.append(
           SemanticGuardIssue(
               code="UNRECOGNIZED_TRANSLATION_FORMAT",
               message="Translated code matches neither Lean nor Dafny patterns",
           )
       )
   ```

2. **`tests/test_semantic_guard.py`**
   - Add test: pass `translated_code="some random text without theorem or method"` with one obligation. Assert `passed=False` and issue code is `UNRECOGNIZED_TRANSLATION_FORMAT`.

---

## Priority P1 (Strongly Recommended)

### P1.1 — Add end-to-end correlation IDs

**Detailed Plan**

1. **`proxy/main.py` — Add `import uuid` at top.**

2. **`proxy/main.py` — Update `GenerateResponse` model (line 129-130):**
   ```python
   class GenerateResponse(BaseModel):
       text: str
       request_id: str
       provider: str = "anthropic"
       model: str = ""
   ```

3. **`proxy/main.py` — Generate and return `request_id` in `generate()` endpoint (line 154-188):**
   - Generate ID at top of function: `req_id = str(uuid.uuid4())`
   - Include in log line (line 181-186): add `request_id=%s` and `req_id` argument.
   - Return in response: `GenerateResponse(text=text, request_id=req_id, provider="anthropic", model=body.model)`

4. **`src/core/llm_provider.py` — Parse and log `request_id` from proxy response (line 71-75):**
   ```python
   payload = response.json()
   text = payload.get("text") if isinstance(payload, dict) else None
   request_id = payload.get("request_id", "") if isinstance(payload, dict) else ""
   if request_id:
       log.info("proxy_request_id=%s", request_id)
   ```

---

### P1.2 — Expand hosted-mode integration tests (failure-path focused)

**Detailed Plan**

1. **Create `tests/test_hosted_failures.py`** with these test cases using `unittest.mock.patch` to mock `requests.post`:

   - **`test_401_unauthorized`**: Mock returns 401. Assert `requests.HTTPError` is raised after retries exhaust (or immediately since 401 is not in `RETRYABLE_STATUS`).
   - **`test_429_rate_limit`**: Mock returns 429 three times. Assert all retries are used and final exception is raised.
   - **`test_502_upstream_failure`**: Mock returns 502 on first two calls, 200 on third. Assert successful text is returned.
   - **`test_malformed_payload`**: Mock returns 200 with `{"wrong": "shape"}`. Assert retry occurs (after A0.2 fix).
   - **`test_timeout_then_success`**: Mock raises `requests.Timeout` on first call, returns 200 on second. Assert success.
   - **`test_connection_error`**: Mock raises `requests.ConnectionError`. Assert all retries attempted.

---

### P1.3 — Proxy response schema tightening

**Detailed Plan**

1. **`proxy/main.py` — Already covered by P1.1 changes** (expanding `GenerateResponse` to include `request_id`, `provider`, `model`).

2. **`src/core/llm_provider.py` — Add schema validation after line 71:**
   ```python
   payload = response.json()
   if not isinstance(payload, dict) or "text" not in payload:
       raise ValueError(f"Proxy response missing 'text' field: {list(payload.keys()) if isinstance(payload, dict) else type(payload)}")
   text = payload["text"]
   if not isinstance(text, str) or not text.strip():
       raise ValueError("Proxy returned empty or non-string 'text'.")
   ```

3. **`tests/test_llm_provider.py`**
   - Add test: mock response with `{"text": ""}` — assert `ValueError` raised.
   - Add test: mock response with `[1, 2, 3]` (list not dict) — assert `ValueError` raised.

---

## Audit-Discovered P1 Items

### A1.1 — IR lowerer silently defaults unknown types to Int

**Problem**
`src/core/ir/lowerer.py:295,300` — `_annotation_to_type()` returns `IRType.INT` for `float`, `str`, or any custom type.

**Detailed Plan**

1. **`src/core/ir/lowerer.py` — Change `_annotation_to_type()` lines 287-300:**
   ```python
   def _annotation_to_type(self, annotation: ast.AST | None) -> IRType:
       if annotation is None:
           return IRType.INT
       if isinstance(annotation, ast.Name):
           if annotation.id == "int":
               return IRType.INT
           if annotation.id == "bool":
               return IRType.BOOL
           raise LoweringError(f"Unsupported type annotation: {annotation.id}")
       if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
           container = annotation.value.id
           if container in {"list", "List"}:
               return IRType.LIST_INT
       raise LoweringError(f"Unsupported type annotation: {ast.dump(annotation)}")
   ```

2. **`tests/test_ir_lowerer.py`**
   - Add test: code with `def foo(x: float) -> float:` — assert `LoweringOutcome.success` is `False` and `"Unsupported type"` in error.
   - Add test: code with `def foo(x: str) -> str:` — same assertion.

---

### A1.2 — `lean_render.py` missing return after IRUnaryOp branches

**Problem**
`src/core/ir/lean_render.py:30-34` — `IRUnaryOp` returns inside `if` branches but falls through silently.

**Detailed Plan**

1. **`src/core/ir/lean_render.py` — Add fallthrough raise after line 34:**
   Change:
   ```python
   if isinstance(expr, IRUnaryOp):
       if expr.op == "-":
           return f"(-{render_expr(expr.operand)})"
       if expr.op == "not":
           return f"(¬ {render_expr(expr.operand)})"
   if isinstance(expr, IRBinaryOp):
   ```
   To:
   ```python
   if isinstance(expr, IRUnaryOp):
       if expr.op == "-":
           return f"(-{render_expr(expr.operand)})"
       if expr.op == "not":
           return f"(¬ {render_expr(expr.operand)})"
       raise TypeError(f"Unsupported unary op: {expr.op}")
   if isinstance(expr, IRBinaryOp):
   ```

---

### A1.3 — `equivalence.py` operator fallthrough returns None

**Problem**
`src/core/equivalence.py:287-305` — `IRUnaryOp` and `IRBinaryOp` branches fall through when operator is unrecognized, returning `None`.

**Detailed Plan**

1. **`src/core/equivalence.py` — Add fallthrough raises in `_eval_ir_expr()`:**

   After line 292 (end of `IRUnaryOp` block), add:
   ```python
       raise RuntimeError(f"Unsupported IR unary op: {expr.op}")
   ```

   After line 305 (end of `IRBinaryOp` block), add:
   ```python
       raise RuntimeError(f"Unsupported IR binary op: {expr.op}")
   ```

   Specifically, the `IRUnaryOp` block at lines 287-292 should become:
   ```python
   if isinstance(expr, IRUnaryOp):
       value = _eval_ir_expr(expr.operand, env)
       if expr.op == "-":
           return -value
       if expr.op == "not":
           return not value
       raise RuntimeError(f"Unsupported IR unary op: {expr.op}")
   ```

   And the `IRBinaryOp` block at lines 293-305 should become:
   ```python
   if isinstance(expr, IRBinaryOp):
       left = _eval_ir_expr(expr.left, env)
       right = _eval_ir_expr(expr.right, env)
       if expr.op == "+":
           return left + right
       if expr.op == "-":
           return left - right
       if expr.op == "*":
           return left * right
       if expr.op == "/":
           return left // right
       if expr.op == "%":
           return left % right
       raise RuntimeError(f"Unsupported IR binary op: {expr.op}")
   ```

---

### A1.4 — Proxy IP rate limiting bypassed behind reverse proxy

**Problem**
`proxy/main.py:162` — `request.client.host` doesn't account for `X-Forwarded-For` headers.

**Detailed Plan**

1. **`proxy/main.py` — Add a helper function after the rate limit functions (around line 110):**
   ```python
   def _resolve_client_ip(request: Request) -> str:
       forwarded = request.headers.get("X-Forwarded-For", "")
       if forwarded:
           return forwarded.split(",")[0].strip()
       real_ip = request.headers.get("X-Real-IP", "")
       if real_ip:
           return real_ip.strip()
       return request.client.host if request.client else "unknown"
   ```

2. **`proxy/main.py` — Replace line 162:**
   ```python
   # was: client_ip = request.client.host if request.client else "unknown"
   client_ip = _resolve_client_ip(request)
   ```

---

### A1.5 — Proxy Anthropic client initialized with empty key

**Problem**
`proxy/main.py:69` — silently creates client with `""` API key.

**Detailed Plan**

1. **`proxy/main.py` — Add validation after line 69:**
   ```python
   _anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
   if not _anthropic_key:
       log.warning("ANTHROPIC_API_KEY is not set — proxy will fail on /generate requests")
   client = anthropic.Anthropic(api_key=_anthropic_key)
   ```

2. **`proxy/main.py` — Add early check in `ready()` endpoint (line 144-150):**
   Already returns `has_anthropic` correctly, so `ready` endpoint already covers this. The warning at startup is the main improvement.

---

### A1.6 — `proof_search.py` sorry detection is over-broad

**Problem**
`src/core/proof_search.py:76-77` — lowercases entire code including comments, causing false rejects.

**Detailed Plan**

1. **`src/core/proof_search.py` — Replace lines 76-77:**
   ```python
   # Strip Lean single-line comments before checking for forbidden markers
   code_no_comments = re.sub(r"--.*$", "", candidate_code, flags=re.MULTILINE)
   lowered = code_no_comments.lower()
   if re.search(r"\b(sorry|admit|axiom)\b", lowered):
       return False, "Candidate contains forbidden proof bypass marker"
   ```

2. **`tests/test_proof_search.py`**
   - Add test: candidate with `-- sorry about this naming\ntheorem foo ... := by omega` — assert `validate_candidate` returns `(True, ...)`.
   - Add test: candidate with `sorry` as an actual tactic — assert `(False, ...)`.

---

### A1.7 — Mutation set too limited and hardcoded

**Problem**
`src/core/quality_gates.py:94-106` — only 5 mutations, one tied to variable name `"return balance"`.

**Detailed Plan**

1. **`src/core/quality_gates.py` — Replace `generate_simple_mutations()` (lines 94-106):**
   ```python
   def generate_simple_mutations(code: str) -> List[str]:
       mutations: List[str] = []
       replacements = [
           (">=", ">"),
           ("<=", "<"),
           (">", ">="),
           ("<", "<="),
           ("==", "!="),
           ("!=", "=="),
           ("+ ", "- "),
           ("- ", "+ "),
           ("if ", "if not "),
           ("and", "or"),
           ("or", "and"),
           ("True", "False"),
           ("False", "True"),
       ]
       for source, target in replacements:
           if source in code:
               mutations.append(code.replace(source, target, 1))
       return mutations
   ```
   This removes the variable-name-specific `"return balance"` mutation and adds: reverse boundary shifts, arithmetic sign flips, boolean logic swaps, and constant perturbations.

2. **`tests/test_mutation_gate.py`**
   - Update existing tests if they rely on the old mutation count.
   - Add test asserting no mutation is tied to a specific variable name.

---

### A1.8 — `requirements.txt` not fully pinned

**Detailed Plan**

1. **`requirements.txt` — Pin requests:**
   ```
   requests==2.32.3
   ```

2. **`proxy/requirements.txt` — Add pydantic, pin anthropic:**
   ```
   fastapi==0.115.0
   uvicorn==0.30.6
   anthropic==0.40.0
   pydantic==2.10.0
   ```

---

## Test Coverage Gaps

### A2.1 — Zero tests for three utility modules

**Detailed Plan**

1. **Create `tests/test_secrets_scanner.py`:**
   ```python
   # Tests to write:
   # - test_scan_text_detects_aws_key: input with "AKIA" pattern, assert finding returned
   # - test_scan_text_detects_github_token: input with "ghp_..." pattern
   # - test_scan_text_detects_generic_api_key: input with 'api_key = "secretvalue..."'
   # - test_scan_text_no_secrets: clean input, assert empty list
   # - test_scan_files: create tmp files, call scan_files, assert findings
   ```

2. **Create `tests/test_file_router.py`:**
   ```python
   # Tests to write:
   # - test_load_argusignore_missing_file: no .argusignore, returns empty PathSpec
   # - test_load_argusignore_with_patterns: .argusignore with "tests/", assert files in tests/ excluded
   # - test_discover_python_files_excludes_venv: create venv/foo.py, assert not discovered
   # - test_discover_python_files_excludes_pycache: __pycache__ excluded
   # - test_discover_python_files_respects_argusignore: file matching ignore pattern excluded
   ```

3. **Create `tests/test_git_ops.py`:**
   ```python
   # Tests to write:
   # - test_changed_python_files_returns_list: mock subprocess.run to return stdout with .py paths
   # - test_changed_python_files_subprocess_error: mock subprocess.run to raise, assert empty list
   # - test_changed_python_files_with_base_ref: assert git diff uses base_ref instead of HEAD^
   # - test_changed_python_files_filters_non_py: stdout includes .js files, assert only .py returned
   ```

---

### A2.2 — CLI `main()` entry point untested

**Detailed Plan**

1. **`tests/test_cli_adapter.py` — Add tests:**
   ```python
   # Tests to write:
   # - test_main_no_files_returns_zero: mock _collect_target_files to return [], assert main() returns 0
   # - test_main_configuration_error: mock create_llm_client to raise ConfigurationError, assert returns 1
   # - test_build_parser_defaults: call build_parser(), parse [], check default values
   # - test_collect_target_files_file_not_found: args.file = "/nonexistent.py", assert clean error
   ```

2. **`src/adapters/cli.py` — Add encoding error handling at lines 175, 187, 192:**
   Wrap `path.read_text(encoding="utf-8")` calls in try/except:
   ```python
   try:
       code = path.read_text(encoding="utf-8")
   except (OSError, UnicodeDecodeError) as exc:
       print(json.dumps({"warning": f"Skipping {rel}: {exc}"}, indent=2), file=sys.stderr)
       continue
   ```
   Apply at all three read_text locations.

---

### A2.3 — GitLab adapter test coverage thin

**Detailed Plan**

1. **`tests/test_gitlab_adapter.py` — Add tests:**
   ```python
   # Tests to write:
   # - test_derive_labels_verified: all files VERIFIED -> ["argus:verified"]
   # - test_derive_labels_fixed: one FIXED, rest VERIFIED -> ["argus:fixed"]
   # - test_derive_labels_vulnerable: one VULNERABLE -> ["argus:vulnerable"]
   # - test_derive_labels_unverified: one UNVERIFIED -> ["argus:vulnerable"]
   # - test_derive_labels_error: one ERROR -> ["argus:vulnerable"]
   # - test_derive_labels_mixed_fixed_vulnerable: VULNERABLE wins over FIXED -> ["argus:vulnerable"]
   # - test_build_comment_includes_commit: assert "Commit" appears in output
   # - test_build_comment_includes_timestamp: assert ISO timestamp format
   # - test_from_env: set CI_SERVER_URL etc., assert adapter.url matches
   # - test_configured_all_set: all 4 fields set -> True
   # - test_configured_missing_token: token missing -> False
   # - test_publish_dry_run: dry_run=True -> posted=False, labels present, reason mentions dry run
   ```

---

## Submission Polish

### A3.1 — No `.gitlab-ci.yml` in repo

**Detailed Plan**

1. **Create `.gitlab-ci.yml` in project root** with the content from README2.md:
   ```yaml
   argus-verify:
     stage: test
     image: registry.gitlab.com/platinum3nx/argusv2/argus-v2:latest
     script:
       - python -m src.adapters.cli --repo-path . --mode ci
     artifacts:
       reports:
         sast: gl-sast-report.json
       paths:
         - Argus_Audit_Report.md
         - argus-sarif-report.json
         - argus_dashboard.html
         - .argus-trace/
     rules:
       - if: $CI_MERGE_REQUEST_IID
   ```

---

### A3.2 — No `.argusignore` file (only example)

**Detailed Plan**

1. **Create `.argusignore` in project root:**
   ```gitignore
   tests/
   test_*.py
   legacy/
   proxy/
   demo_target/
   benchmarks/
   *.pyc
   ```

---

### A3.3 — Dashboard `_render_diff` is naive

**Problem**
`src/core/dashboard.py:486-505` — set-based diff breaks on duplicates and line moves.

**Detailed Plan**

1. **`src/core/dashboard.py` — Replace `_render_diff()` (lines 486-505):**
   ```python
   def _render_diff(original: str, repaired: str) -> str:
       """Sequential line-by-line diff rendering using difflib."""
       import difflib
       orig_lines = original.splitlines(keepends=True)
       rep_lines = repaired.splitlines(keepends=True)
       diff = difflib.unified_diff(orig_lines, rep_lines, lineterm="")

       html = ["<div class='code-body' style='white-space:pre;'>"]
       for line in diff:
           stripped = line.rstrip("\n")
           if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
               continue
           if line.startswith("-"):
               html.append(f"<div class='diff-line-remove'>{_html_escape(stripped)}</div>")
           elif line.startswith("+"):
               html.append(f"<div class='diff-line-add'>{_html_escape(stripped)}</div>")
           else:
               html.append(f"<div> {_html_escape(stripped)}</div>")
       html.append("</div>")
       return "".join(html)
   ```

2. **`tests/test_dashboard.py`**
   - Add test with duplicate lines in both original and repaired. Assert diff renders correctly.
   - Add test with moved lines. Assert both removal and addition are shown.

---

## Priority P2 (Product/Scale Readiness)

### P2.1 — Persistent quotas and usage accounting

**Problem**
`proxy/main.py:76-79` — rate counters are in-memory and reset on restart.

**Detailed Plan**

1. If Redis is available, replace `_token_counts`/`_ip_counts` dicts with Redis `INCR` + `EXPIRE`:
   - `INCR argus:token:{token}:daily` with `EXPIRE 86400`
   - `INCR argus:ip:{ip}:hourly` with `EXPIRE 3600`
2. If Redis is not available, fall back to current in-memory behavior.
3. Add `ARGUS_REDIS_URL` env var. If not set, use in-memory (current behavior).

---

### P2.2 — Token lifecycle tooling

**Detailed Plan**

1. Add `proxy/admin.py` CLI script:
   - `python -m proxy.admin issue --name team-x --daily-limit 500` — outputs a new random token and prints JSON to add to `ARGUS_PROXY_TOKENS_JSON`.
   - `python -m proxy.admin revoke --token <token>` — outputs updated JSON with token removed.
   - `python -m proxy.admin list` — lists all configured tokens and their limits.
2. This is a helper for generating env var content, not a live API.

---

### P2.3 — Supported-pattern detector + user guidance

**Detailed Plan**

1. **`src/core/ir/lowerer.py` — The `_collect_unsupported()` method (lines 94-113) already detects constructs.**
2. **`src/adapters/cli.py` — When verdict is UNVERIFIED, print the specific unsupported constructs and guidance:**
   - In the pipeline result, `obligations` and `message` already include construct names.
   - Add a mapping in cli.py from construct names to human guidance:
     ```python
     CONSTRUCT_GUIDANCE = {
         "for_loop": "For-loops are verified via the Dafny engine. Ensure loop is over range().",
         "class_definition": "OOP patterns are not supported. Extract logic into standalone functions.",
         "async_function": "Async functions are not supported. Use synchronous equivalents.",
         "comprehension": "List/dict/set comprehensions are not yet supported. Use explicit loops.",
     }
     ```

---

## Updated Execution Plan (6-Day Focus)

### Day 1
- P0.1 Dashboard UNKNOWN status
- P0.2 Mutation verifier routing fix
- A0.1 Pipeline engine decoupling fix
- A0.4 Semantic guard unrecognized format
- Add/update tests for all

### Day 2
- P0.3 Proxy request size guardrails
- P0.4 Retry-After + jitter in client
- A0.2 ValueError in retry loop
- A0.3 DafnyTranslator assumptions
- Add tests

### Day 3
- P1.2 Hosted failure-mode integration tests
- P1.3 Proxy response schema contract hardening
- A1.4 Proxy IP rate limiting
- A1.5 Proxy startup validation

### Day 4
- P1.1 Correlation IDs end-to-end
- A1.1 IR type defaults
- A1.2 lean_render return
- A1.3 equivalence fallthrough
- A1.6 proof_search sorry detection
- A1.8 requirements pinning

### Day 5
- A2.1-A2.3 Test coverage (utils, CLI, GitLab adapter)
- A1.7 Expand mutation set
- A3.3 Dashboard diff fix

### Day 6 (if time)
- P2.1 Persistent usage backend
- P2.2 Token lifecycle admin
- A3.1 `.gitlab-ci.yml`
- A3.2 `.argusignore`

---

## Updated Definition of Done (Technical)

- No misleading PASS statuses in dashboard.
- Mutation gate language/verifier alignment guaranteed.
- Pipeline translation language always matches verifier language.
- DafnyTranslator forwards assumptions into generated code.
- Semantic guard rejects unrecognized translation formats.
- Proxy rejects oversized requests and handles 429 retries robustly.
- ValueError and malformed payloads do not escape retry loop.
- Hosted-mode failure-path tests pass and verify fail-closed behavior.
- Correlation IDs available across proxy + client + trace.
- IR lowerer rejects unknown types instead of silent Int default.
- All utility modules have test coverage.
- Dependencies fully pinned for reproducibility.
- Documentation updated to reflect final runtime behavior and limits.

---

## Notes

- This plan focuses on **technical trust and reliability**, not only demo polish.
- Product remains fail-closed by design; improvements target correctness, operability, and scale robustness.
- Audit-discovered items (A-series) are interleaved with original items by priority in the updated execution plan.

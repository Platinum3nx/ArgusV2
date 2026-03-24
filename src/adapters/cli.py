from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

from src.adapters.gitlab_adapter import GitLabAdapter
from src.core.ci_integrity import CIGateReport, run_ci_integrity_suite
from src.core.dashboard import generate_dashboard
from src.core.llm_provider import ConfigurationError, create_llm_client
from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.reporter import (
    dump_json,
    render_gitlab_sast_report,
    render_json_report,
    render_markdown_report,
    render_mr_comment,
    render_sarif_report,
)
from src.utils.file_router import discover_python_files
from src.utils.git_ops import changed_python_files

CONSTRUCT_GUIDANCE = {
    "for_loop": "For-loops are verified via the Dafny engine. Ensure loop is over range().",
    "class_definition": "OOP patterns are not supported. Extract logic into standalone functions.",
    "async_function": "Async functions are not supported. Use synchronous equivalents.",
    "comprehension": "List/dict/set comprehensions are not yet supported. Use explicit loops.",
    "try_except": "Try/except blocks are not yet supported. Handle errors outside the verified function.",
    "global_statement": "Global state mutations are not supported. Use function parameters instead.",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ArgusV2 CLI")
    parser.add_argument("--file", type=str, help="Single Python file to audit")
    parser.add_argument("--repo-path", type=str, default=".", help="Repository path")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "ci"])
    parser.add_argument(
        "--base-ref", type=str, default=None, help="Base ref for changed file detection in CI mode"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["anthropic"],
        help="LLM provider (hosted mode currently supports: anthropic)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model override (default: claude-sonnet-4-6 for anthropic hosted mode)",
    )
    parser.add_argument("--output-json", type=str, default="argus_report.json")
    parser.add_argument("--output-md", type=str, default="Argus_Audit_Report.md")
    parser.add_argument("--output-sarif", type=str, default="argus-sarif-report.json")
    parser.add_argument("--output-gl-sast", type=str, default="gl-sast-report.json")
    parser.add_argument("--output-ci-gates", type=str, default="argus-ci-gates.json")
    parser.add_argument(
        "--output-html",
        type=str,
        default="argus_dashboard.html",
        help="Path for Mission Control HTML dashboard output",
    )
    parser.add_argument("--allow-local-verify", action="store_true")
    parser.add_argument("--skip-gitlab-publish", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_path).resolve()
    files = _collect_target_files(args, repo_root)

    if not files:
        print(json.dumps({"status": "no-python-files-found"}, indent=2))
        return 0

    # Resolve provider: CLI arg > LLM_PROVIDER env var > default "anthropic"
    provider = args.provider or os.getenv("LLM_PROVIDER", "anthropic")
    model = args.model  # None means use provider default

    try:
        llm_client = create_llm_client(provider, model)
    except ConfigurationError as exc:
        print(json.dumps({"status": "configuration-error", "error": str(exc)}, indent=2))
        return 1

    config = PipelineConfig(
        provider=provider,
        model=llm_client.model_id,
        require_docker_verify=not args.allow_local_verify,
    )
    pipeline = ArgusPipeline(config=config, llm_client=llm_client)
    reports = pipeline.run_many(files)

    prov = llm_client.provider_name
    mdl = llm_client.model_id

    # Collect code dicts from pipeline public API for enhanced reports
    original_code = pipeline.original_code_map
    repaired_code = pipeline.repaired_code_map

    # Standard machine-readable artifacts (format unchanged)
    json_payload = render_json_report(reports, provider=prov, model=mdl)
    sarif_payload = render_sarif_report(reports, provider=prov, model=mdl)
    gl_sast_payload = render_gitlab_sast_report(reports)

    # Enhanced human-readable artifacts
    markdown = render_markdown_report(
        reports,
        provider=prov,
        model=mdl,
        repaired_code=repaired_code,
        original_code=original_code,
    )

    dump_json(args.output_json, json_payload)
    Path(args.output_md).write_text(markdown, encoding="utf-8")
    dump_json(args.output_sarif, sarif_payload)
    dump_json(args.output_gl_sast, gl_sast_payload)

    # Mission Control HTML dashboard
    try:
        generate_dashboard(
            report_path=args.output_json,
            trace_root=str(config.trace_root),
            run_id=pipeline.last_run_id,
            output_path=args.output_html,
            original_code=original_code,
        )
    except Exception as exc:
        # Dashboard generation is non-blocking — all other artifacts are already written
        print(json.dumps({"dashboard_warning": f"Dashboard generation failed: {exc}"}, indent=2))

    ci_gate_report: CIGateReport | None = None
    if args.mode == "ci":
        ci_gate_report = run_ci_integrity_suite(
            files=files,
            reports=reports,
            trace_root=Path(config.trace_root),
            run_id=pipeline.last_run_id,
            benchmark_root=repo_root / "benchmarks" / "seeded",
        )
        dump_json(args.output_ci_gates, ci_gate_report.to_dict())

        if not args.skip_gitlab_publish:
            gitlab_result = GitLabAdapter.from_env().publish_results(
                reports,
                provider=prov,
                model=mdl,
                original_code=original_code,
                repaired_code=repaired_code,
            )
            print(json.dumps({"gitlab_publish": gitlab_result.reason}, indent=2))

    print(json.dumps(json_payload["summary"], indent=2))

    # Print construct guidance for UNVERIFIED results
    for report in reports:
        if report.verdict.name == "UNVERIFIED" and report.message:
            for construct, guidance in CONSTRUCT_GUIDANCE.items():
                if construct in report.message.lower():
                    print(json.dumps({"guidance": {report.filename: guidance}}, indent=2))

    if ci_gate_report is not None:
        print(
            json.dumps(
                {
                    "ci_integrity": ci_gate_report.to_dict(),
                },
                indent=2,
            )
        )

    has_blocking_verdicts = json_payload["summary"]["vulnerable"] > 0 or (
        json_payload["summary"]["unverified"] + json_payload["summary"]["error"] > 0
    )
    gates_failed = ci_gate_report is not None and not ci_gate_report.passed
    return 1 if has_blocking_verdicts or gates_failed else 0


def _collect_target_files(args: argparse.Namespace, repo_root: Path) -> List[Tuple[str, str]]:
    if args.file:
        path = Path(args.file).resolve()
        try:
            rel = str(path.relative_to(repo_root))
        except ValueError:
            rel = path.name
        try:
            code = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(json.dumps({"warning": f"Skipping {rel}: {exc}"}, indent=2), file=sys.stderr)
            return []
        return [(rel, code)]

    if args.mode == "ci":
        changed = changed_python_files(repo_root, base_ref=args.base_ref)
        if changed:
            items: List[Tuple[str, str]] = []
            for rel in changed:
                if not _is_audit_target(rel):
                    continue
                path = repo_root / rel
                if not path.exists():
                    continue
                try:
                    code = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    print(json.dumps({"warning": f"Skipping {rel}: {exc}"}, indent=2), file=sys.stderr)
                    continue
                items.append((rel, code))
            return items

    discovered = discover_python_files(repo_root)
    items: List[Tuple[str, str]] = []
    for path in discovered:
        rel = str(path.relative_to(repo_root))
        if not _is_audit_target(rel):
            continue
        try:
            code = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(json.dumps({"warning": f"Skipping {rel}: {exc}"}, indent=2), file=sys.stderr)
            continue
        items.append((rel, code))
    return items


def _is_audit_target(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    if not normalized.endswith(".py"):
        return False
    excluded_prefixes = (
        "legacy/",
        "tests/",
        "benchmarks/",
    )
    if normalized.startswith(excluded_prefixes):
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())

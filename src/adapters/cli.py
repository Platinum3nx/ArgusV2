from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

from src.adapters.gitlab_adapter import GitLabAdapter
from src.core.ci_integrity import CIGateReport, run_ci_integrity_suite
from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.reporter import (
    dump_json,
    render_gitlab_sast_report,
    render_json_report,
    render_markdown_report,
    render_sarif_report,
)
from src.utils.file_router import discover_python_files
from src.utils.git_ops import changed_python_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ArgusV2 CLI")
    parser.add_argument("--file", type=str, help="Single Python file to audit")
    parser.add_argument("--repo-path", type=str, default=".", help="Repository path")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "ci"])
    parser.add_argument("--base-ref", type=str, default=None, help="Base ref for changed file detection in CI mode")
    parser.add_argument("--output-json", type=str, default="argus_report.json")
    parser.add_argument("--output-md", type=str, default="Argus_Audit_Report.md")
    parser.add_argument("--output-sarif", type=str, default="argus-sarif-report.json")
    parser.add_argument("--output-gl-sast", type=str, default="gl-sast-report.json")
    parser.add_argument("--output-ci-gates", type=str, default="argus-ci-gates.json")
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

    config = PipelineConfig(require_docker_verify=not args.allow_local_verify)
    pipeline = ArgusPipeline(config=config)
    reports = pipeline.run_many(files)

    json_payload = render_json_report(reports)
    markdown = render_markdown_report(reports)
    sarif_payload = render_sarif_report(reports)
    gl_sast_payload = render_gitlab_sast_report(reports)

    dump_json(args.output_json, json_payload)
    Path(args.output_md).write_text(markdown, encoding="utf-8")
    dump_json(args.output_sarif, sarif_payload)
    dump_json(args.output_gl_sast, gl_sast_payload)

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
            gitlab_result = GitLabAdapter.from_env().publish_results(reports)
            print(json.dumps({"gitlab_publish": gitlab_result.reason}, indent=2))

    print(json.dumps(json_payload["summary"], indent=2))
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
        return [(rel, path.read_text(encoding="utf-8"))]

    if args.mode == "ci":
        changed = changed_python_files(repo_root, base_ref=args.base_ref)
        if changed:
            items: List[Tuple[str, str]] = []
            for rel in changed:
                path = repo_root / rel
                if not path.exists() or "legacy" in path.parts:
                    continue
                items.append((rel, path.read_text(encoding="utf-8")))
            return items

    discovered = discover_python_files(repo_root)
    return [
        (str(path.relative_to(repo_root)), path.read_text(encoding="utf-8"))
        for path in discovered
    ]


if __name__ == "__main__":
    raise SystemExit(main())

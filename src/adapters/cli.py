from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.reporter import dump_json, render_json_report, render_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ArgusV2 CLI")
    parser.add_argument("--file", type=str, help="Single Python file to audit")
    parser.add_argument("--repo-path", type=str, default=".", help="Repository path")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "ci"])
    parser.add_argument("--output-json", type=str, default="argus_report.json")
    parser.add_argument("--output-md", type=str, default="Argus_Audit_Report.md")
    parser.add_argument("--allow-local-verify", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = PipelineConfig(require_docker_verify=not args.allow_local_verify)
    pipeline = ArgusPipeline(config=config)

    files: list[tuple[str, str]] = []
    if args.file:
        path = Path(args.file)
        files.append((path.name, path.read_text(encoding="utf-8")))
    else:
        for path in Path(args.repo_path).rglob("*.py"):
            if "legacy" in path.parts:
                continue
            files.append((str(path.relative_to(args.repo_path)), path.read_text(encoding="utf-8")))

    reports = pipeline.run_many(files)
    json_payload = render_json_report(reports)
    markdown = render_markdown_report(reports)

    dump_json(args.output_json, json_payload)
    Path(args.output_md).write_text(markdown, encoding="utf-8")
    print(json.dumps(json_payload["summary"], indent=2))

    has_blocking = json_payload["summary"]["vulnerable"] > 0 or (
        json_payload["summary"]["unverified"] + json_payload["summary"]["error"] > 0
    )
    return 1 if has_blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())


from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from src.adapters.cli import _collect_target_files, _is_audit_target, build_parser, main


def test_is_audit_target_filters_non_product_paths() -> None:
    assert _is_audit_target("src/core/pipeline.py")
    assert not _is_audit_target("tests/test_pipeline.py")
    assert not _is_audit_target("legacy/backend/main.py")
    assert not _is_audit_target("benchmarks/seeded/safe/sample.py")


def test_collect_target_files_excludes_tests_and_legacy(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "src" / "core").mkdir(parents=True)
    (repo / "tests").mkdir(parents=True)
    (repo / "legacy").mkdir(parents=True)

    (repo / "src" / "core" / "app.py").write_text("def f(x: int) -> int:\n    return x\n", encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    (repo / "legacy" / "old.py").write_text("def old():\n    return 1\n", encoding="utf-8")

    args = Namespace(file=None, mode="single", base_ref=None)
    files = _collect_target_files(args, repo)
    rels = {name for name, _ in files}

    assert "src/core/app.py" in rels
    assert "tests/test_app.py" not in rels
    assert "legacy/old.py" not in rels


@patch("src.adapters.cli._collect_target_files", return_value=[])
def test_main_no_files_returns_zero(mock_collect) -> None:
    with patch("src.adapters.cli.build_parser") as mock_bp:
        mock_bp.return_value.parse_args.return_value = Namespace(
            file=None, mode="single", base_ref=None, repo_path=".",
            provider=None, model=None, output_json="argus_report.json",
            output_md="Argus_Audit_Report.md", output_sarif="argus-sarif-report.json",
            output_gl_sast="gl-sast-report.json", output_ci_gates="argus-ci-gates.json",
            output_html="argus_dashboard.html", allow_local_verify=False,
            skip_gitlab_publish=True,
        )
        result = main()
    assert result == 0


@patch("src.adapters.cli._collect_target_files", return_value=[("app.py", "x = 1")])
@patch("src.adapters.cli.create_llm_client")
def test_main_configuration_error(mock_create, mock_collect) -> None:
    from src.core.llm_provider import ConfigurationError

    mock_create.side_effect = ConfigurationError("Missing API key")

    with patch("src.adapters.cli.build_parser") as mock_bp:
        mock_bp.return_value.parse_args.return_value = Namespace(
            file=None, mode="single", base_ref=None, repo_path=".",
            provider=None, model=None, output_json="argus_report.json",
            output_md="Argus_Audit_Report.md", output_sarif="argus-sarif-report.json",
            output_gl_sast="gl-sast-report.json", output_ci_gates="argus-ci-gates.json",
            output_html="argus_dashboard.html", allow_local_verify=False,
            skip_gitlab_publish=True,
        )
        result = main()
    assert result == 1


def test_build_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([])

    assert args.file is None
    assert args.repo_path == "."
    assert args.mode == "single"
    assert args.base_ref is None
    assert args.provider is None
    assert args.model is None
    assert args.output_json == "argus_report.json"
    assert args.output_md == "Argus_Audit_Report.md"
    assert args.allow_local_verify is False
    assert args.skip_gitlab_publish is False

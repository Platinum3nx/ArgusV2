from argparse import Namespace
from pathlib import Path

from src.adapters.cli import _collect_target_files, _is_audit_target


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

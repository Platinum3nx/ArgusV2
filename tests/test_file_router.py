from __future__ import annotations

from pathlib import Path

from src.utils.file_router import discover_python_files, load_argusignore


def test_discover_python_files_basic(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "lib.py").write_text("y = 2\n", encoding="utf-8")

    files = discover_python_files(tmp_path)
    names = {f.name for f in files}
    assert "app.py" in names
    assert "lib.py" in names


def test_discover_python_files_excludes_venv(tmp_path: Path) -> None:
    venv_dir = tmp_path / "venv" / "lib"
    venv_dir.mkdir(parents=True)
    (venv_dir / "foo.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("y = 2\n", encoding="utf-8")

    files = discover_python_files(tmp_path)
    names = {f.name for f in files}
    assert "foo.py" not in names
    assert "main.py" in names


def test_discover_python_files_excludes_pycache(tmp_path: Path) -> None:
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "cached.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "real.py").write_text("y = 2\n", encoding="utf-8")

    files = discover_python_files(tmp_path)
    names = {f.name for f in files}
    assert "cached.py" not in names
    assert "real.py" in names


def test_discover_python_files_excludes_legacy(tmp_path: Path) -> None:
    legacy_dir = tmp_path / "legacy"
    legacy_dir.mkdir()
    (legacy_dir / "old.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "new.py").write_text("y = 2\n", encoding="utf-8")

    files = discover_python_files(tmp_path)
    names = {f.name for f in files}
    assert "old.py" not in names
    assert "new.py" in names


def test_load_argusignore_empty(tmp_path: Path) -> None:
    spec = load_argusignore(tmp_path)
    assert not spec.match_file("anything.py")


def test_argusignore_excludes_matching_files(tmp_path: Path) -> None:
    (tmp_path / ".argusignore").write_text("generated/*.py\n", encoding="utf-8")
    gen_dir = tmp_path / "generated"
    gen_dir.mkdir()
    (gen_dir / "auto.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "manual.py").write_text("y = 2\n", encoding="utf-8")

    files = discover_python_files(tmp_path)
    names = {f.name for f in files}
    assert "auto.py" not in names
    assert "manual.py" in names

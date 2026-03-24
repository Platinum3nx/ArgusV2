from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from src.utils.git_ops import changed_python_files


def _make_completed_process(stdout: str):
    """Build a fake subprocess.CompletedProcess."""
    import subprocess
    return subprocess.CompletedProcess(
        args=["git", "diff", "--name-only", "HEAD^", "HEAD"],
        returncode=0,
        stdout=stdout,
        stderr="",
    )


@patch("src.utils.git_ops.subprocess.run")
def test_changed_python_files_returns_list(mock_run, tmp_path: Path) -> None:
    # Create the .py files so the existence check passes
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "src" / "utils.py").write_text("y = 2\n", encoding="utf-8")

    mock_run.return_value = _make_completed_process("src/app.py\nsrc/utils.py\n")

    result = changed_python_files(tmp_path)
    assert result == ["src/app.py", "src/utils.py"]


@patch("src.utils.git_ops.subprocess.run")
def test_changed_python_files_subprocess_error(mock_run, tmp_path: Path) -> None:
    mock_run.side_effect = Exception("git not found")

    result = changed_python_files(tmp_path)
    assert result == []


@patch("src.utils.git_ops.subprocess.run")
def test_changed_python_files_filters_non_py(mock_run, tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    # Do NOT create the .js file as a real file - it should be filtered by extension

    mock_run.return_value = _make_completed_process(
        "src/app.py\nsrc/index.js\nREADME.md\n"
    )

    result = changed_python_files(tmp_path)
    assert result == ["src/app.py"]
    assert "src/index.js" not in result
    assert "README.md" not in result


@patch("src.utils.git_ops.subprocess.run")
def test_changed_python_files_with_base_ref(mock_run, tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")

    mock_run.return_value = _make_completed_process("a.py\n")

    result = changed_python_files(tmp_path, base_ref="origin/main")
    assert result == ["a.py"]
    # Verify the base_ref was used in the command
    call_args = mock_run.call_args[0][0]
    assert "origin/main" in call_args

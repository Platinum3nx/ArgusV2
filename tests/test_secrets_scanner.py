from __future__ import annotations

from pathlib import Path

from src.utils.secrets_scanner import SecretFinding, scan_files, scan_text


def test_scan_text_detects_aws_key() -> None:
    content = "aws_access_key_id = AKIAIOSFODNN7EXAMPLE"
    findings = scan_text(content, "config.py")
    assert len(findings) >= 1
    assert any(f.kind == "aws_access_key" for f in findings)
    assert findings[0].file_path == "config.py"
    assert findings[0].line_number == 1


def test_scan_text_detects_github_token() -> None:
    content = "token = ghp_ABCDEFGHIJKLMNOPQRSTuvwx"
    findings = scan_text(content, "auth.py")
    assert len(findings) >= 1
    assert any(f.kind == "github_token" for f in findings)


def test_scan_text_detects_generic_api_key() -> None:
    content = 'api_key = "secretvalue1234567890"'
    findings = scan_text(content, "settings.py")
    assert len(findings) >= 1
    assert any(f.kind == "generic_api_key" for f in findings)


def test_scan_text_no_secrets() -> None:
    content = "def hello():\n    return 'world'\n"
    findings = scan_text(content, "clean.py")
    assert findings == []


def test_scan_files(tmp_path: Path) -> None:
    repo_root = tmp_path
    secret_file = repo_root / "leaked.py"
    secret_file.write_text(
        'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n', encoding="utf-8"
    )
    clean_file = repo_root / "safe.py"
    clean_file.write_text("x = 1\n", encoding="utf-8")

    findings = scan_files([secret_file, clean_file], repo_root)
    assert len(findings) >= 1
    assert all(isinstance(f, SecretFinding) for f in findings)
    assert any("leaked.py" in f.file_path for f in findings)
    assert not any("safe.py" in f.file_path for f in findings)

from __future__ import annotations

import os

from src.adapters.gitlab_adapter import GitLabAdapter
from src.core.models import Verdict
from src.core.reporter import FileReport


class _FakeNotes:
    def __init__(self) -> None:
        self.created = []

    def create(self, payload):  # noqa: ANN001 - test double
        self.created.append(payload)


class _FakeMergeRequest:
    def __init__(self) -> None:
        self.notes = _FakeNotes()
        self.labels = ["team:backend", "argus:verified"]
        self.saved = False

    def save(self) -> None:
        self.saved = True


class _FakeMergeRequests:
    def __init__(self, mr: _FakeMergeRequest) -> None:
        self._mr = mr

    def get(self, iid: str) -> _FakeMergeRequest:
        assert iid == "7"
        return self._mr


class _FakeProject:
    def __init__(self, mr: _FakeMergeRequest) -> None:
        self.mergerequests = _FakeMergeRequests(mr)


class _FakeProjects:
    def __init__(self, project: _FakeProject) -> None:
        self._project = project

    def get(self, project_id: str) -> _FakeProject:
        assert project_id == "42"
        return self._project


class _FakeClient:
    def __init__(self, project: _FakeProject) -> None:
        self.projects = _FakeProjects(project)


def _file(verdict: Verdict) -> FileReport:
    return FileReport(
        filename="withdraw.py",
        verdict=verdict,
        obligations=[],
        assumptions=[],
        engine="lean",
        message="demo",
    )


def test_gitlab_adapter_publish_results_posts_comment_and_sets_labels() -> None:
    mr = _FakeMergeRequest()
    project = _FakeProject(mr)

    adapter = GitLabAdapter(
        url="https://gitlab.example.com",
        token="token",
        project_id="42",
        merge_request_iid="7",
        client_factory=lambda **_: _FakeClient(project),
    )
    result = adapter.publish_results([_file(Verdict.VULNERABLE)], dry_run=False)

    assert result.posted
    assert result.labels_applied == ["argus:vulnerable"]
    assert len(mr.notes.created) == 1
    assert "Argus Formal Verification Report" in mr.notes.created[0]["body"]
    assert mr.labels == ["team:backend", "argus:vulnerable"]
    assert mr.saved


def test_gitlab_adapter_skips_when_not_configured() -> None:
    adapter = GitLabAdapter(
        url="",
        token="",
        project_id="",
        merge_request_iid="",
    )
    result = adapter.publish_results([_file(Verdict.VERIFIED)], dry_run=False)
    assert not result.posted
    assert "not configured" in result.reason


# --- New tests ---


def test_derive_labels_verified() -> None:
    adapter = GitLabAdapter(url="", token="", project_id="", merge_request_iid="")
    files = [_file(Verdict.VERIFIED), _file(Verdict.VERIFIED)]
    labels = adapter.derive_labels(files)
    assert labels == ["argus:verified"]


def test_derive_labels_fixed() -> None:
    adapter = GitLabAdapter(url="", token="", project_id="", merge_request_iid="")
    files = [_file(Verdict.FIXED), _file(Verdict.VERIFIED)]
    labels = adapter.derive_labels(files)
    assert labels == ["argus:fixed"]


def test_derive_labels_vulnerable() -> None:
    adapter = GitLabAdapter(url="", token="", project_id="", merge_request_iid="")
    files = [_file(Verdict.VULNERABLE), _file(Verdict.VERIFIED)]
    labels = adapter.derive_labels(files)
    assert labels == ["argus:vulnerable"]


def test_derive_labels_unverified() -> None:
    adapter = GitLabAdapter(url="", token="", project_id="", merge_request_iid="")
    files = [_file(Verdict.UNVERIFIED)]
    labels = adapter.derive_labels(files)
    assert labels == ["argus:vulnerable"]


def test_derive_labels_error() -> None:
    adapter = GitLabAdapter(url="", token="", project_id="", merge_request_iid="")
    files = [_file(Verdict.ERROR)]
    labels = adapter.derive_labels(files)
    assert labels == ["argus:vulnerable"]


def test_configured_all_set() -> None:
    adapter = GitLabAdapter(
        url="https://gitlab.example.com",
        token="glpat-xxxxx",
        project_id="42",
        merge_request_iid="7",
    )
    assert adapter.configured() is True


def test_configured_missing_token() -> None:
    adapter = GitLabAdapter(
        url="https://gitlab.example.com",
        token="",
        project_id="42",
        merge_request_iid="7",
    )
    assert adapter.configured() is False


def test_configured_missing_project_id() -> None:
    adapter = GitLabAdapter(
        url="https://gitlab.example.com",
        token="glpat-xxxxx",
        project_id="",
        merge_request_iid="7",
    )
    assert adapter.configured() is False


def test_from_env(monkeypatch) -> None:
    monkeypatch.setenv("CI_SERVER_URL", "https://custom.gitlab.io")
    monkeypatch.setenv("GITLAB_TOKEN", "test-token-123")
    monkeypatch.setenv("CI_PROJECT_ID", "99")
    monkeypatch.setenv("CI_MERGE_REQUEST_IID", "15")

    adapter = GitLabAdapter.from_env()

    assert adapter.url == "https://custom.gitlab.io"
    assert adapter.token == "test-token-123"
    assert adapter.project_id == "99"
    assert adapter.merge_request_iid == "15"

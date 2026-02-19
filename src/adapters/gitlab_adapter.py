from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Sequence

from src.core.reporter import FileReport, render_mr_comment

try:
    import gitlab
except Exception:  # pragma: no cover - optional dependency in test envs
    gitlab = None


@dataclass(frozen=True)
class GitLabPublishResult:
    posted: bool
    labels_applied: List[str]
    reason: str
    comment: str


class GitLabAdapter:
    """
    Thin adapter for GitLab MR interactions.
    """

    def __init__(
        self,
        url: str | None,
        token: str | None,
        project_id: str | None,
        merge_request_iid: str | None,
        client_factory: Callable[..., object] | None = None,
    ) -> None:
        self.url = (url or "").strip()
        self.token = (token or "").strip()
        self.project_id = (project_id or "").strip()
        self.merge_request_iid = (merge_request_iid or "").strip()
        self.client_factory = client_factory

    @classmethod
    def from_env(cls) -> "GitLabAdapter":
        return cls(
            url=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
            token=os.getenv("GITLAB_TOKEN"),
            project_id=os.getenv("CI_PROJECT_ID"),
            merge_request_iid=os.getenv("CI_MERGE_REQUEST_IID"),
        )

    def configured(self) -> bool:
        return all([self.url, self.token, self.project_id, self.merge_request_iid])

    def publish_results(self, files: Sequence[FileReport], dry_run: bool = False) -> GitLabPublishResult:
        comment = self.build_comment(files)
        labels = self.derive_labels(files)

        if not self.configured():
            return GitLabPublishResult(
                posted=False,
                labels_applied=[],
                reason="GitLab adapter not configured; skipping MR publish",
                comment=comment,
            )

        if dry_run:
            return GitLabPublishResult(
                posted=False,
                labels_applied=labels,
                reason="Dry run enabled; no MR publish performed",
                comment=comment,
            )

        if self.client_factory is None:
            if gitlab is None:
                return GitLabPublishResult(
                    posted=False,
                    labels_applied=[],
                    reason="python-gitlab is unavailable",
                    comment=comment,
                )
            client = gitlab.Gitlab(url=self.url, private_token=self.token)
        else:
            client = self.client_factory(url=self.url, private_token=self.token)

        try:
            project = client.projects.get(self.project_id)
            mr = project.mergerequests.get(self.merge_request_iid)
            mr.notes.create({"body": comment})

            existing = list(getattr(mr, "labels", []) or [])
            preserved = [item for item in existing if not item.startswith("argus:")]
            mr.labels = preserved + labels
            mr.save()
            return GitLabPublishResult(
                posted=True,
                labels_applied=labels,
                reason="Posted MR comment and applied labels",
                comment=comment,
            )
        except Exception as exc:  # pragma: no cover - network/API failures
            return GitLabPublishResult(
                posted=False,
                labels_applied=[],
                reason=f"GitLab publish failed: {exc}",
                comment=comment,
            )

    def build_comment(self, files: Sequence[FileReport]) -> str:
        commit = (os.getenv("CI_COMMIT_SHA") or "local")[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        body = render_mr_comment(list(files))
        return f"**Commit**: `{commit}` | **Generated**: {timestamp}\n\n{body}"

    def derive_labels(self, files: Sequence[FileReport]) -> List[str]:
        verdicts = {item.verdict.value for item in files}
        if {"VULNERABLE", "UNVERIFIED", "ERROR"} & verdicts:
            return ["argus:vulnerable"]
        if "FIXED" in verdicts:
            return ["argus:fixed"]
        return ["argus:verified"]

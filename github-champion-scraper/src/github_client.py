from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests

class GitHubClient:
    """
    Minimal GitHub API v3 wrapper focused on scraping contribution metrics
    needed for the Github Champion Scraper.
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        per_page: int = 100,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.per_page = per_page
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "github-champion-scraper",
            }
        )
        self.log = logger or logging.getLogger("github_champion.github_client")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        url = f"{self.base_url}{path}"
        results: List[Dict[str, Any]] = []
        page = 1

        while True:
            merged_params = {"per_page": self.per_page, "page": page}
            if params:
                merged_params.update(params)

            self.log.debug("GET %s params=%s", url, merged_params)
            resp = self.session.get(url, params=merged_params, timeout=30)
            if resp.status_code == 401:
                raise RuntimeError("Unauthorized: invalid GitHub token")
            if resp.status_code == 403:
                raise RuntimeError(
                    "Forbidden: you may have hit a rate limit or lack permissions"
                )
            if resp.status_code == 404:
                # For some endpoints, 404 indicates missing repo or insufficient permissions
                raise RuntimeError(f"Resource not found at {url}")

            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                # Some endpoints return a dict; in this wrapper, we only paginate list responses.
                return data  # type: ignore[return-value]

            results.extend(data)
            if len(data) < self.per_page:
                break
            page += 1

        return results

    def get_org_repos(self, org: str) -> List[str]:
        """
        Fetch repository names for an organization.
        """
        path = f"/orgs/{org}/repos"
        repos = self._get(path)
        repo_names = [r["name"] for r in repos if not r.get("archived", False)]
        self.log.info("Fetched %d repositories for org %s", len(repo_names), org)
        return repo_names

    def _filter_items_by_date(
        self,
        items: List[Dict[str, Any]],
        since: datetime,
        until: datetime,
        date_key: str = "created_at",
    ) -> List[Dict[str, Any]]:
        filtered: List[Dict[str, Any]] = []
        for item in items:
            date_str = item.get(date_key)
            if not date_str:
                continue
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                continue
            if since <= dt <= until:
                filtered.append(item)
        return filtered

    def get_closed_issues(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get closed issues (excluding PRs) in the time range.
        """
        path = f"/repos/{owner}/{repo}/issues"
        issues = self._get(path, params={"state": "closed"})
        issues = [i for i in issues if "pull_request" not in i]  # exclude PRs
        return self._filter_items_by_date(
            issues, since=since, until=until, date_key="closed_at"
        )

    def get_pulls(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get pull requests in the time range.
        """
        path = f"/repos/{owner}/{repo}/pulls"
        pulls = self._get(path, params={"state": "all", "sort": "created", "direction": "desc"})
        return self._filter_items_by_date(pulls, since=since, until=until, date_key="created_at")

    def get_pull_reviews(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        since: datetime,
        until: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get reviews for a specific pull request in the time range.
        """
        path = f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        reviews = self._get(path)
        return self._filter_items_by_date(reviews, since=since, until=until, date_key="submitted_at")

    def get_commits(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get commits in the time range.
        """
        path = f"/repos/{owner}/{repo}/commits"
        commits = self._get(
            path,
            params={
                "since": since.isoformat(),
                "until": until.isoformat(),
            },
        )
        return commits

    def collect_repository_contributions(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate contribution metrics for a single repository.
        Returns a dict keyed by contributor id (login).
        """
        self.log.info(
            "Collecting contributions for %s/%s from %s to %s",
            owner,
            repo,
            since.isoformat(),
            until.isoformat(),
        )

        contributors: Dict[str, Dict[str, Any]] = {}

        # Closed issues
        try:
            issues = self.get_closed_issues(owner, repo, since, until)
        except RuntimeError as e:
            self.log.error("Failed to fetch issues for %s/%s: %s", owner, repo, e)
            issues = []

        for issue in issues:
            assignee = issue.get("assignee") or {}
            login = assignee.get("login")
            if not login:
                continue
            data = contributors.setdefault(
                login,
                {
                    "issuesClosed": 0,
                    "pullReviews": 0,
                    "pullsCreated": 0,
                    "additions": 0,
                    "deletions": 0,
                    "commits": 0,
                },
            )
            data["issuesClosed"] += 1

        # Pull requests and reviews
        try:
            pulls = self.get_pulls(owner, repo, since, until)
        except RuntimeError as e:
            self.log.error("Failed to fetch pulls for %s/%s: %s", owner, repo, e)
            pulls = []

        for pull in pulls:
            user = pull.get("user") or {}
            login = user.get("login")
            if not login:
                continue
            data = contributors.setdefault(
                login,
                {
                    "issuesClosed": 0,
                    "pullReviews": 0,
                    "pullsCreated": 0,
                    "additions": 0,
                    "deletions": 0,
                    "commits": 0,
                },
            )
            data["pullsCreated"] += 1

            # Reviews for each pull
            number = pull.get("number")
            if number is None:
                continue
            try:
                reviews = self.get_pull_reviews(owner, repo, number, since, until)
            except RuntimeError as e:
                self.log.error(
                    "Failed to fetch reviews for PR #%s in %s/%s: %s",
                    number,
                    owner,
                    repo,
                    e,
                )
                reviews = []
            for review in reviews:
                user = review.get("user") or {}
                login = user.get("login")
                if not login:
                    continue
                data = contributors.setdefault(
                    login,
                    {
                        "issuesClosed": 0,
                        "pullReviews": 0,
                        "pullsCreated": 0,
                        "additions": 0,
                        "deletions": 0,
                        "commits": 0,
                    },
                )
                data["pullReviews"] += 1

        # Commits and line stats
        try:
            commits = self.get_commits(owner, repo, since, until)
        except RuntimeError as e:
            self.log.error("Failed to fetch commits for %s/%s: %s", owner, repo, e)
            commits = []

        for commit in commits:
            author = commit.get("author") or {}
            login = author.get("login")
            if not login:
                continue
            data = contributors.setdefault(
                login,
                {
                    "issuesClosed": 0,
                    "pullReviews": 0,
                    "pullsCreated": 0,
                    "additions": 0,
                    "deletions": 0,
                    "commits": 0,
                },
            )
            data["commits"] += 1
            stats = commit.get("stats") or {}
            data["additions"] += int(stats.get("additions", 0))
            data["deletions"] += int(stats.get("deletions", 0))

        self.log.info(
            "Collected metrics for %d contributors in %s/%s",
            len(contributors),
            owner,
            repo,
        )
        return contributors
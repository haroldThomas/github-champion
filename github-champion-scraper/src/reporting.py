from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Iterable, Optional

from .scoring import ContributorScore

def generate_leaderboard_report(
    organization_label: str,
    per_repo_leaderboards: Dict[str, List[Dict[str, Any]]],
    org_leaderboard: List[Dict[str, Any]],
    time_range: Optional[Dict[str, str]] = None,
    generated_at: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Build a leaderboard structure matching the example in the README.
    """
    report: List[Dict[str, Any]] = []

    report.append({organization_label: org_leaderboard})

    for repo_name, leaderboard in per_repo_leaderboards.items():
        report.append({repo_name: leaderboard})

    # timeRange and generatedAt can be added as metadata in a separate entry if desired
    if time_range or generated_at:
        metadata: Dict[str, Any] = {}
        if time_range:
            metadata["timeRange"] = time_range
        if generated_at:
            metadata["generatedAt"] = generated_at.isoformat()
        report.append({"_metadata": metadata})

    return report

def generate_detailed_metrics_report(
    per_repo_scores: Dict[str, Dict[str, ContributorScore]],
    time_range: Optional[Dict[str, str]] = None,
    generated_at: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Build a flat array of detailed metrics per contributor, per repository.
    """
    detailed: List[Dict[str, Any]] = []

    for repo_name, scores in per_repo_scores.items():
        for contributor_id, score in scores.items():
            base = {
                "repository": repo_name,
                "id": contributor_id,
                "additions": score.additions,
                "deletions": score.deletions,
                "commits": score.commits,
                "pullsCreated": score.pulls_created,
                "pullReviews": score.pull_reviews,
                "issuesClosed": score.issues_closed,
                "total": round(score.total, 2),
            }
            if time_range:
                base["timeRange"] = time_range
            if generated_at:
                base["generatedAt"] = generated_at.isoformat()
            detailed.append(base)

    return detailed

def save_json(data: Any, path: Path) -> None:
    """
    Serialize `data` to JSON at `path`, creating parent dirs as needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
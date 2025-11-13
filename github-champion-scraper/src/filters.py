from __future__ import annotations

from typing import Dict, Any

def filter_contributors_by_min_score(
    metrics: Dict[str, Dict[str, Any]], min_score: float
) -> Dict[str, Dict[str, Any]]:
    """
    Filter a dictionary of contributor metrics by minimum total score.
    Expects each metrics entry to optionally include a 'total' key.
    """
    filtered: Dict[str, Dict[str, Any]] = {}
    for contributor_id, data in metrics.items():
        total = data.get("total", 0.0)
        if total >= min_score:
            filtered[contributor_id] = data
    return filtered

def filter_repositories_by_activity(
    repo_metrics: Dict[str, Dict[str, Dict[str, Any]]],
    min_events: int = 1,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Remove repositories that have fewer than `min_events` qualifying events
    across all contributors.
    """
    filtered: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for repo, contributors in repo_metrics.items():
        total_events = 0
        for data in contributors.values():
            total_events += (
                int(data.get("issuesClosed", 0))
                + int(data.get("pullReviews", 0))
                + int(data.get("pullsCreated", 0))
            )
        if total_events >= min_events:
            filtered[repo] = contributors
    return filtered
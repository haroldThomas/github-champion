from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

ISSUES_CLOSED_WEIGHT = 1.0
PULL_REVIEWS_WEIGHT = 0.75
PULLS_CREATED_WEIGHT = 0.5

@dataclass
class ContributorScore:
    id: str
    total: float
    issues_closed: int
    pull_reviews: int
    pulls_created: int
    additions: int
    deletions: int
    commits: int

def _compute_total_score(
    issues_closed: int,
    pull_reviews: int,
    pulls_created: int,
) -> float:
    return (
        issues_closed * ISSUES_CLOSED_WEIGHT
        + pull_reviews * PULL_REVIEWS_WEIGHT
        + pulls_created * PULLS_CREATED_WEIGHT
    )

def compute_scores_for_repo(
    repo_contributors: Dict[str, Dict[str, Any]]
) -> Dict[str, ContributorScore]:
    """
    Convert raw per-contributor metrics for a repository into ContributorScore objects.
    """
    result: Dict[str, ContributorScore] = {}
    for contributor_id, metrics in repo_contributors.items():
        issues_closed = int(metrics.get("issuesClosed", 0))
        pull_reviews = int(metrics.get("pullReviews", 0))
        pulls_created = int(metrics.get("pullsCreated", 0))
        additions = int(metrics.get("additions", 0))
        deletions = int(metrics.get("deletions", 0))
        commits = int(metrics.get("commits", 0))

        total = _compute_total_score(
            issues_closed=issues_closed,
            pull_reviews=pull_reviews,
            pulls_created=pulls_created,
        )

        result[contributor_id] = ContributorScore(
            id=contributor_id,
            total=total,
            issues_closed=issues_closed,
            pull_reviews=pull_reviews,
            pulls_created=pulls_created,
            additions=additions,
            deletions=deletions,
            commits=commits,
        )

    return result

def aggregate_organization_scores(
    per_repo_scores: Dict[str, Dict[str, ContributorScore]]
) -> Dict[str, ContributorScore]:
    """
    Given scores per repo, aggregate them to the organization level.
    """
    aggregated: Dict[str, ContributorScore] = {}
    for repo_scores in per_repo_scores.values():
        for contributor_id, score in repo_scores.items():
            if contributor_id not in aggregated:
                aggregated[contributor_id] = ContributorScore(
                    id=contributor_id,
                    total=score.total,
                    issues_closed=score.issues_closed,
                    pull_reviews=score.pull_reviews,
                    pulls_created=score.pulls_created,
                    additions=score.additions,
                    deletions=score.deletions,
                    commits=score.commits,
                )
            else:
                agg = aggregated[contributor_id]
                agg.total += score.total
                agg.issues_closed += score.issues_closed
                agg.pull_reviews += score.pull_reviews
                agg.pulls_created += score.pulls_created
                agg.additions += score.additions
                agg.deletions += score.deletions
                agg.commits += score.commits
    return aggregated

def leaderboard_from_scores(
    scores: Dict[str, ContributorScore],
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """
    Convert ContributorScore objects into a top-N leaderboard list, sorted by total desc.
    """
    sorted_scores = sorted(
        scores.values(),
        key=lambda s: (s.total, s.issues_closed, s.pull_reviews, s.pulls_created),
        reverse=True,
    )
    leaderboard: List[Dict[str, Any]] = []
    for score in sorted_scores[:top_n]:
        leaderboard.append(
            {
                "name": score.id,
                "total": round(score.total, 2),
                "pullReviews": score.pull_reviews,
                "issuesClosed": score.issues_closed,
                "pullsCreated": score.pulls_created,
            }
        )
    return leaderboard

def compute_all_leaderboards(
    repo_metrics: Dict[str, Dict[str, Dict[str, Any]]],
    top_n: int = 3,
) -> Tuple[
    Dict[str, Dict[str, ContributorScore]],
    Dict[str, ContributorScore],
    Dict[str, List[Dict[str, Any]]],
    List[Dict[str, Any]],
]:
    """
    High-level helper:
        - compute scores per repo,
        - aggregate to organization,
        - build leaderboards.
    """
    per_repo_scores: Dict[str, Dict[str, ContributorScore]] = {}
    for repo_name, contributors in repo_metrics.items():
        per_repo_scores[repo_name] = compute_scores_for_repo(contributors)

    org_scores = aggregate_organization_scores(per_repo_scores)

    per_repo_leaderboards: Dict[str, List[Dict[str, Any]]] = {}
    for repo_name, scores in per_repo_scores.items():
        per_repo_leaderboards[repo_name] = leaderboard_from_scores(scores, top_n=top_n)

    org_leaderboard = leaderboard_from_scores(org_scores, top_n=top_n)

    return per_repo_scores, org_scores, per_repo_leaderboards, org_leaderboard
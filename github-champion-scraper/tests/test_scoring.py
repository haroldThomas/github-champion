import sys
from pathlib import Path

# Ensure src is on the import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from scoring import (
    compute_scores_for_repo,
    aggregate_organization_scores,
    leaderboard_from_scores,
)

def test_compute_scores_for_repo_and_leaderboard():
    repo_metrics = {
        "gandalf": {
            "issuesClosed": 3,
            "pullReviews": 25,
            "pullsCreated": 3,
            "additions": 15652,
            "deletions": 16589,
            "commits": 13,
        },
        "samwise": {
            "issuesClosed": 5,
            "pullReviews": 16,
            "pullsCreated": 7,
            "additions": 17,
            "deletions": 4,
            "commits": 1,
        },
        "frodo": {
            "issuesClosed": 1,
            "pullReviews": 16,
            "pullsCreated": 6,
            "additions": 123,
            "deletions": 54,
            "commits": 2,
        },
    }

    scores = compute_scores_for_repo(repo_metrics)
    assert "gandalf" in scores
    assert scores["gandalf"].issues_closed == 3
    assert scores["gandalf"].pull_reviews == 25
    assert scores["gandalf"].pulls_created == 3

    leaderboard = leaderboard_from_scores(scores, top_n=3)
    assert len(leaderboard) == 3
    # Gandalf should be the top contributor by score
    assert leaderboard[0]["name"] == "gandalf"

def test_aggregate_organization_scores():
    repo_a = {
        "gandalf": {
            "issuesClosed": 1,
            "pullReviews": 2,
            "pullsCreated": 3,
            "additions": 10,
            "deletions": 5,
            "commits": 1,
        }
    }
    repo_b = {
        "gandalf": {
            "issuesClosed": 2,
            "pullReviews": 1,
            "pullsCreated": 0,
            "additions": 5,
            "deletions": 2,
            "commits": 2,
        }
    }

    scores_a = compute_scores_for_repo(repo_a)
    scores_b = compute_scores_for_repo(repo_b)
    per_repo_scores = {"repo-a": scores_a, "repo-b": scores_b}

    aggregated = aggregate_organization_scores(per_repo_scores)
    assert "gandalf" in aggregated
    agg = aggregated["gandalf"]
    assert agg.issues_closed == 3  # 1 + 2
    assert agg.pull_reviews == 3  # 2 + 1
    assert agg.pulls_created == 3  # 3 + 0
    assert agg.commits == 3  # 1 + 2
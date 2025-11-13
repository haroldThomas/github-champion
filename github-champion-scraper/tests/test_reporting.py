import sys
from pathlib import Path
from datetime import datetime

# Ensure src is on the import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from reporting import (
    generate_leaderboard_report,
    generate_detailed_metrics_report,
)
from scoring import ContributorScore

def test_generate_leaderboard_report():
    per_repo_leaderboards = {
        "repo-one": [
            {"name": "gandalf", "total": 10.0, "pullReviews": 5, "issuesClosed": 3, "pullsCreated": 2}
        ]
    }
    org_leaderboard = [
        {"name": "gandalf", "total": 25.0, "pullReviews": 15, "issuesClosed": 7, "pullsCreated": 4}
    ]
    time_range = {"since": "2025-01-01", "until": "2025-01-31"}
    generated_at = datetime(2025, 1, 31)

    report = generate_leaderboard_report(
        organization_label="Organization All-stars",
        per_repo_leaderboards=per_repo_leaderboards,
        org_leaderboard=org_leaderboard,
        time_range=time_range,
        generated_at=generated_at,
    )

    assert isinstance(report, list)
    assert report[0].get("Organization All-stars") is not None
    assert report[1].get("repo-one") is not None
    assert report[-1].get("_metadata") is not None

def test_generate_detailed_metrics_report():
    per_repo_scores = {
        "repo-one": {
            "gandalf": ContributorScore(
                id="gandalf",
                total=10.0,
                issues_closed=3,
                pull_reviews=5,
                pulls_created=2,
                additions=100,
                deletions=50,
                commits=3,
            )
        }
    }
    time_range = {"since": "2025-01-01", "until": "2025-01-31"}
    generated_at = datetime(2025, 1, 31)

    detailed = generate_detailed_metrics_report(
        per_repo_scores=per_repo_scores,
        time_range=time_range,
        generated_at=generated_at,
    )

    assert isinstance(detailed, list)
    assert detailed
    item = detailed[0]
    assert item["id"] == "gandalf"
    assert item["repository"] == "repo-one"
    assert "timeRange" in item
    assert "generatedAt" in item
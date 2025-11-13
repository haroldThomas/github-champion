from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .github_client import GitHubClient
from .scoring import compute_all_leaderboards
from .reporting import (
    generate_leaderboard_report,
    generate_detailed_metrics_report,
    save_json,
)
from .utils.date_ranges import parse_date_range
from .utils.logging_setup import setup_logging
from .filters import filter_repositories_by_activity

def _load_settings(settings_path: Optional[str]) -> Dict[str, Any]:
    if not settings_path:
        return {}
    settings_file = Path(settings_path)
    if not settings_file.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    with settings_file.open("r", encoding="utf-8") as f:
        return json.load(f)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Github Champion Scraper - rank contributors across an organization."
    )
    parser.add_argument(
        "--org",
        dest="organization",
        help="GitHub organization name",
    )
    parser.add_argument(
        "--repos",
        nargs="*",
        dest="repos",
        help="Optional list of repository names. If omitted, all org repos are used.",
    )
    parser.add_argument(
        "--since",
        help="Start date (YYYY-MM-DD). If provided, must be used with --until.",
    )
    parser.add_argument(
        "--until",
        help="End date (YYYY-MM-DD). If provided, must be used with --since.",
    )
    parser.add_argument(
        "--preset",
        default=None,
        help="Date range preset (last_7_days, last_30_days, last_90_days, this_month, this_year).",
    )
    parser.add_argument(
        "--settings",
        dest="settings",
        help="Optional path to a settings JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="data",
        help="Directory where JSON outputs will be written.",
    )
    parser.add_argument(
        "--top-n",
        dest="top_n",
        type=int,
        default=3,
        help="Number of top contributors to include in leaderboards.",
    )
    parser.add_argument(
        "--min-events",
        dest="min_events",
        type=int,
        default=1,
        help="Minimum number of contribution events required for a repository to be included.",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    logger = setup_logging(args.log_level)

    settings = _load_settings(args.settings) if args.settings else {}

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable is required to authenticate with GitHub."
        )

    organization = args.organization or settings.get("organization")
    if not organization:
        raise RuntimeError("Organization name must be provided via --org or settings.")

    # Resolve repositories
    repos: List[str]
    if args.repos:
        repos = args.repos
    else:
        repos = settings.get("repositories") or []

    client = GitHubClient(
        token=token,
        base_url=settings.get("github_api", {}).get("base_url", "https://api.github.com"),
        per_page=int(settings.get("github_api", {}).get("per_page", 100)),
        logger=logger,
    )

    if not repos:
        logger.info("No repositories specified, fetching all repositories for %s", organization)
        repos = client.get_org_repos(organization)
        if not repos:
            raise RuntimeError(f"No repositories found for organization {organization}")

    # Date range
    preset = args.preset or settings.get("time_range", {}).get("preset")
    since_str = args.since or settings.get("time_range", {}).get("since")
    until_str = args.until or settings.get("time_range", {}).get("until")

    date_range = parse_date_range(preset=preset, since_str=since_str, until_str=until_str)
    since, until = date_range.since, date_range.until
    time_range_meta = {
        "since": since.date().isoformat(),
        "until": until.date().isoformat(),
    }

    logger.info("Using date range %s to %s", since.isoformat(), until.isoformat())

    # Collect metrics per repo
    per_repo_metrics: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for repo_name in repos:
        try:
            metrics = client.collect_repository_contributions(
                owner=organization,
                repo=repo_name,
                since=since,
                until=until,
            )
        except RuntimeError as e:
            logger.error("Error collecting contributions for %s/%s: %s", organization, repo_name, e)
            continue
        if metrics:
            per_repo_metrics[repo_name] = metrics

    if not per_repo_metrics:
        raise RuntimeError("No metrics collected for any repository.")

    # Filter repositories with very low activity
    per_repo_metrics = filter_repositories_by_activity(
        per_repo_metrics, min_events=args.min_events
    )
    if not per_repo_metrics:
        raise RuntimeError(
            "All repositories filtered out due to insufficient activity. "
            "Try lowering --min-events."
        )

    # Compute scores and leaderboards
    (
        per_repo_scores,
        org_scores,
        per_repo_leaderboards,
        org_leaderboard,
    ) = compute_all_leaderboards(per_repo_metrics, top_n=args.top_n)

    organization_label = (
        settings.get("leaderboard", {}).get("organization_label") or "Organization All-stars"
    )

    generated_at = datetime.utcnow()

    leaderboard_report = generate_leaderboard_report(
        organization_label=organization_label,
        per_repo_leaderboards=per_repo_leaderboards,
        org_leaderboard=org_leaderboard,
        time_range=time_range_meta,
        generated_at=generated_at,
    )

    detailed_report = generate_detailed_metrics_report(
        per_repo_scores=per_repo_scores,
        time_range=time_range_meta,
        generated_at=generated_at,
    )

    output_dir = Path(args.output_dir)
    top_contributors_path = output_dir / "top-contributors.json"
    detailed_metrics_path = output_dir / "detailed-metrics.json"

    save_json(leaderboard_report, top_contributors_path)
    save_json(detailed_report, detailed_metrics_path)

    logger.info("Wrote leaderboard to %s", top_contributors_path)
    logger.info("Wrote detailed metrics to %s", detailed_metrics_path)

if __name__ == "__main__":
    main()
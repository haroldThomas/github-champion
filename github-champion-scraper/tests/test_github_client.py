import sys
from pathlib import Path
from datetime import datetime, timezone

import types

# Ensure src is on the import path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from github_client import GitHubClient

class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or []

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")

class DummySession:
    def __init__(self, responses):
        self.headers = {}
        self._responses = responses
        self._calls = []

    def get(self, url, params=None, timeout=30):
        self._calls.append((url, params, timeout))
        return self._responses.pop(0)

def test_get_org_repos_uses_correct_endpoint_and_parses_names(monkeypatch):
    responses = [
        DummyResponse(
            json_data=[
                {"name": "repo-one", "archived": False},
                {"name": "repo-two", "archived": True},
                {"name": "repo-three", "archived": False},
            ]
        )
    ]
    client = GitHubClient(token="dummy-token")
    dummy_session = DummySession(responses=responses)
    client.session = dummy_session  # type: ignore[assignment]

    repos = client.get_org_repos("my-org")
    assert repos == ["repo-one", "repo-three"]
    assert len(dummy_session._calls) == 1
    url, params, timeout = dummy_session._calls[0]
    assert "/orgs/my-org/repos" in url
    assert params["per_page"] == client.per_page

def test_filter_items_by_date_range(monkeypatch):
    now = datetime(2025, 1, 31, tzinfo=timezone.utc)
    since = now.replace(day=1)
    until = now

    # Provide a single response list
    responses = [DummyResponse(json_data=[])]
    client = GitHubClient(token="dummy-token")
    client.session = DummySession(responses=responses)  # type: ignore[assignment]

    items = [
        {"created_at": "2025-01-05T12:00:00Z"},
        {"created_at": "2025-02-01T12:00:00Z"},
        {"created_at": "invalid-date"},
    ]
    filtered = client._filter_items_by_date(items, since=since, until=until)
    assert len(filtered) == 1
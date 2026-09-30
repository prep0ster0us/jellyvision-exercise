import pytest
from collections import Counter
from unittest.mock import Mock, patch

from github_activity import (
    analyze_events,
    fetch_public_events,
    get_activity_type,
    print_results,
    user_owns_repo,
)

def test_event_classification():
    """verify that github push events map to the chosen commit activity category."""

    event1 = {
        "type": "PushEvent",
        "payload": {},
    }
    assert get_activity_type(event1) == "commits/pushes"
    
    event2 = {
        "type": "IssueCommentEvent",
        "payload": {},
    }
    assert get_activity_type(event2) == "comments"


def test_merged_pull_request():
    """verify that a successfully merged pull request is counted as a merge."""

    event = {
        "type": "PullRequestEvent",
        "payload": {
            "action": "closed",
            "pull_request": {
                "merged": True,
            },
        },
    }

    assert get_activity_type(event) == "merges"


def test_closed_unmerged_pull_request():
    """ensure that closing a pull request without merging it does not count as a merge."""

    event = {
        "type": "PullRequestEvent",
        "payload": {
            "action": "closed",
            "pull_request": {
                "merged": False,
            },
        },
    }

    assert get_activity_type(event) == "pull requests"


def test_events_grouped_by_repository():
    """verify that contribution events are grouped by repo and counted by activity type."""

    events = [
        {
            "type": "PushEvent",
            "repo": {"name": "alice/project"},
            "payload": {},
        },
        {
            "type": "PushEvent",
            "repo": {"name": "alice/project"},
            "payload": {},
        },
        {
            "type": "IssuesEvent",
            "repo": {"name": "alice/project"},
            "payload": {},
        },
    ]

    result = analyze_events(events)

    assert result["alice/project"]["commits/pushes"] == 2
    assert result["alice/project"]["issues"] == 1


def test_non_contribution_events():
    """verify that public activity such as starring a repo is not treated as contribution."""

    events = [
        {
            "type": "WatchEvent",
            "repo": {"name": "alice/project"},
            "payload": {},
        },
    ]

    assert analyze_events(events) == {}


def test_repository_ownership():
    """verify that ownership is determined from the owner portion of owner/repo."""

    assert user_owns_repo("alice", "alice/project") is True
    assert user_owns_repo("alice", "bob/project") is False


def test_show_top_common_only(capsys):
    """verify that output follows the requirement to show only the top three activities."""

    repo_activity = {
        "alice/project": Counter({
            "commits/pushes": 10,
            "comments": 8,
            "pull requests": 6,
            "issues": 2,
        }),
    }

    print_results("alice", repo_activity)

    # capsys captures text printed to stdout by print_results
    output = capsys.readouterr().out

    assert "commits/pushes: 10" in output
    assert "comments: 8" in output
    assert "pull requests: 6" in output
    assert "issues: 2" not in output


@patch("github_activity.requests.get")
def test_fetch_public_events_response(mock_get):
    """verify successful api data is returned without making a real network request."""

    expected_events = [
        {
            "type": "PushEvent",
            "repo": {
                "name": "alice/project",
            },
        },
    ]

    # create a fake requests response so the test does not depend on github
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_events
    mock_get.return_value = mock_response

    result = fetch_public_events("alice")

    assert result == expected_events


@patch("github_activity.requests.get")
def test_fetch_public_events_exception(mock_get):
    """verify that a github 404 is translated into the expected user-facing error."""

    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(ValueError):
        fetch_public_events("missing-user")
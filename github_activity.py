import requests
from collections import Counter, defaultdict
from typing import Any
import argparse

GITHUB_API_URL = "https://api.github.com"
# restrict events that count as contributing to a repository
# assumption: starring or forking a repository shouldn't count as contribution
CONTRIBUTION_EVENT_TYPES = {
    "PushEvent",
    "PullRequestEvent",
    "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent",
    "IssueCommentEvent",
    "CommitCommentEvent",
    "IssuesEvent",
    "CreateEvent",
    "DeleteEvent",
    "ReleaseEvent",
    # documentations lists events by General activity, Issue and Timeline
}

def fetch_public_events(username: str) -> list[dict[str, Any]]:
    url = f"{GITHUB_API_URL}/users/{username}/events/public"
    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise ValueError(f"github user '{username}' was not found")

    if response.status_code == 403:
        raise RuntimeError(
            "github rejected the request\n"
            "possibly because the unauthenticated api rate limit was reached"
        )

    # raise exception for failed request
    response.raise_for_status()

    return response.json()

# categorize events into commits, PRs, comments and merges
def get_activity_type(event):
    event_type = event.get("type", "")
    payload = event.get("payload") or {}

    # Map specific event types to clean categories
    mapping = {
        "PushEvent": "commits/pushes",
        "PullRequestEvent": "pull requests",
        "IssueCommentEvent": "comments",
        "PullRequestReviewCommentEvent": "comments",
        "CommitCommentEvent": "comments",
        "PullRequestReviewEvent": "reviews",
        "IssuesEvent": "issues",
        "CreateEvent": "creates",
        "DeleteEvent": "deletes",
        "ReleaseEvent": "releases",
    }

    # Return mapped value (if it exists)
    if event_type in mapping:
        # explicitly flag merge events (from broader PR event)
        if event_type == 'PullRequestEvent':
            pull_request = payload.get("pull_request") or {}

            if (payload.get("action") == "closed" or pull_request.get("merged") is True):
                return "merges"
                
        return mapping[event_type]

    # fallback for unmapped events
    return event_type.removesuffix("Event").lower() or "unknown"

def user_owns_repo(username, repo_name):
    if "/" not in repo_name:
        return False

    owner, _ = repo_name.split("/", 1)

    return owner.casefold() == username.casefold()

def analyze_events(
    events: list[dict[str, Any]],
) -> dict[str, Counter[str]]:
    repo_activity: dict[str, Counter[str]] = defaultdict(Counter)

    for event in events:
        if event.get("type") not in CONTRIBUTION_EVENT_TYPES:
            continue

        repo = event.get("repo") or {}
        repo_name = repo.get("name")

        if not repo_name:
            continue

        activity_type = get_activity_type(event)
        repo_activity[repo_name][activity_type] += 1

    return dict(repo_activity)

def print_results(
    username: str,
    repo_activity: dict[str, Counter[str]],
) -> None:
    if not repo_activity:
        print(f"No recent public contribution activity found for '{username}'.")
        return

    print(f"Recent public GitHub activity for {username}\n")

    for repo_name in sorted(repo_activity):
        activity_counts = repo_activity[repo_name]
        top_three = activity_counts.most_common(3)      # by count/frequency
        owned = "yes" if user_owns_repo(username, repo_name) else "no"

        print(repo_name)
        print(f"owned by user: {owned}")

        for pos, (activity_type, count) in enumerate(top_three, start=1):
            print(f"\t{pos}. {activity_type}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show a GitHub user's recent public repository activity."
    )
    parser.add_argument(
        "username",
        help="GitHub username to inspect",
    )

    args = parser.parse_args()

    try:
        events = fetch_public_events(args.username)
        repo_activity = analyze_events(events)
        print_results(args.username, repo_activity)

    except (ValueError, RuntimeError, requests.RequestException) as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()

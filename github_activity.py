import requests
from collections import Counter, defaultdict

# sample username
username = "ge0ffrey"

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


response = requests.get(
    f"https://api.github.com/users/{username}/events/public",
    timeout=10,
)
# raise exception for failed request
response.raise_for_status()

# if valid response, view events
events = response.json()
events_by_repo = defaultdict(list)
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

for event in events:
    if event.get("type") not in CONTRIBUTION_EVENT_TYPES:
        continue
    repo = event.get("repo") or {}
    repo_name = repo.get("name")

    if not repo_name:
        continue

    activity_type = get_activity_type(event)
    events_by_repo[repo_name].append(activity_type)


for repo_name, activity_types in events_by_repo.items():
    event_counts = Counter(activity_types)
    top_three = event_counts.most_common(3)     # by count/frequency
    owned = "yes" if user_owns_repo(username, repo_name) else "no"

    print(repo_name)
    print(f"owned by user: {owned}")

    for pos, (activity_type, count) in enumerate(top_three, start=1):
        print(f"\t{pos}. {activity_type}: {count}")
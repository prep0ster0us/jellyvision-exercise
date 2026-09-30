import requests
from collections import Counter, defaultdict

# sample username
username = "ge0ffrey"

# categorize events into commits, PRs, comments and merges
def get_activity_type(event):
    event_type = event.get("type", "")

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
        return mapping[event_type]

    # fallback for unmapped events
    return event_type.removesuffix("Event").lower() or "unknown"

response = requests.get(
    f"https://api.github.com/users/{username}/events/public",
    timeout=10,
)
# raise exception for failed request
response.raise_for_status()

# if valid response, view events
events = response.json()
events_by_repo = defaultdict(list)

for event in events:
    repo_name = event["repo"]["name"]
    activity_type = get_activity_type(event)
    events_by_repo[repo_name].append(activity_type)


for repo_name, activity_types in events_by_repo.items():
    event_counts = Counter(activity_types)
    top_three = event_counts.most_common(3)     # by count/frequency

    print(repo_name)

    for pos, (activity_type, count) in enumerate(top_three, start=1):
        print(f"\t{pos}. {activity_type}: {count}")
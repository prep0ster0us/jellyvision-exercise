import requests
from collections import defaultdict

# sample username
username = "ge0ffrey"

response = requests.get(
    f"https://api.github.com/users/{username}/events/public",
    timeout=10,
)
# raise exception for failed request
response.raise_for_status()

# if valid response, view events
events_by_repo = defaultdict(list)

for event in response.json():
    repo_name = event["repo"]["name"]
    events_by_repo[repo_name].append(event["type"])

for repo_name, event_types in events_by_repo.items():
    print(repo_name, event_types)
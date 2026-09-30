import requests

# sample username
username = "ge0ffrey"

response = requests.get(
    f"https://api.github.com/users/{username}/events/public",
    timeout=10,
)
# raise exception for failed request
response.raise_for_status()

# if valid response, view events
# print(response.json()[0])
for event in response.json():
    print(event["type"], event["repo"]["name"])
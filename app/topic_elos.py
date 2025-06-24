import requests
from collections import defaultdict
import numpy as np

url = "https://codeforces.com/api/problemset.problems"
response = requests.get(url)
data = response.json()

if data["status"] != "OK":
    raise Exception("API request failed")

problems = data["result"]["problems"]

tag_ratings = defaultdict(list)
distinct_tags = set()

for problem in problems:
    tags = problem.get("tags", [])
    rating = problem.get("rating", None)

    for tag in tags:
        distinct_tags.add(tag)
        if rating is not None:
            tag_ratings[tag].append(rating)

print(f"Number of distinct tags: {len(distinct_tags)}\n")

percentile = 20
print(f"{percentile}th percentile (Q1) rating per tag:")
for tag in sorted(distinct_tags):
    ratings = tag_ratings[tag]
    if len(ratings) >= 1:
        q1 = np.percentile(ratings, percentile  )
        print(f"{tag}: {round(q1, 2)}")
    else:
        print(f"{tag}: No rated problems")

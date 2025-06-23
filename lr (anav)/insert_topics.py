from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load your Supabase credentials from a .env file or set them directly here
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Define your data
topic_names = [
    "DFS", "BFS", "Shortest paths", "Minimum spanning trees", "Strongly connected components",
    "Biconnected components", "2-SAT", "Matroids", "Dynamic programming (DP)", "DP optimizations (Knuth)",
    "Union-Find", "Monotone queue", "Range Min Query", "Lowest Common Ancestor", "Eulerian tour",
    "Centroids", "Heavy-light decomposition", "Square root decomposition", "Segment trees",
    "Lazy segment trees", "Sparse table", "Union of rectangles", "Matching algorithms", "Ford-Fulkerson",
    "Hungarian algorithm", "Min-cost flow", "Sweep line algorithm", "Binary search", "Ternary search",
    "Backtracking", "Dealing with big numbers modulo prime", "Trie (prefix tree)", "Suffix tree",
    "Suffix array", "Cartesian tree", "Rabin-Karp (rolling hash)", "Convex Hull",
    "Checking if point is in polygon", "Pick's theorem", "Computing a winning strategy (Nim)",
    "Fast Fourier Transform", "Interactive problems"
]

topic_difficulties = {
    0: 1200, 1: 1200, 2: 1500, 3: 1700, 4: 1800, 5: 1900,
    6: 2000, 7: 2300, 8: 1500, 9: 2100, 10: 1500, 11: 1800,
    12: 1700, 13: 1900, 14: 1900, 15: 2200, 16: 2200, 17: 1900,
    18: 1800, 19: 2100, 20: 1900, 21: 2400, 22: 2200, 23: 1900,
    24: 2300, 25: 2400, 26: 2100, 27: 1200, 28: 1500, 29: 1500,
    30: 2200, 31: 1700, 32: 2200, 33: 2200, 34: 1800, 35: 1800,
    36: 2200, 37: 1800, 38: 1900, 39: 1500, 40: 2400, 41: 2100
}

# Create list of rows
rows = [
    {"id": i, "name": topic_names[i], "difficulty": topic_difficulties[i]}
    for i in range(len(topic_names))
]

# Insert into Supabase
response = supabase.table("topic_info").insert(rows).execute()

# Check for errors
print(response)

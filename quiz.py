from flask import Flask, request, render_template
from sklearn.linear_model import LogisticRegression
import numpy as np

concepts = ["DFS", "BFS", "Shortest paths", "Minimum spanning trees", "Strongly connected components", "Biconnected components", "2-SAT", "Matroids", "Dynamic programming (DP)", "DP optimizations (Knuth)", "Union-Find", "Monotone queue", "Range Min Query", "Lowest Common Ancestor", "Eulerian tour", "Centroids", "Heavy-light decomposition", "Square root decomposition", "Segment trees", "Lazy segment trees", "Sparse table", "Union of rectangles", "Matching algorithms", "Ford-Fulkerson", "Hungarian algorithm", "Min-cost flow", "Sweep line algorithm", "Binary search", "Ternary search", "Backtracking", "Dealing with big numbers modulo prime", "Trie (prefix tree)", "Suffix tree", "Suffix array", "Cartesian tree", "Rabin-Karp (rolling hash)", "Convex Hull", "Checking if point is in polygon", "Pick's theorem", "Computing a winning strategy (Nim)", "Fast Fourier Transform", "Interactive problems"]
elo_values = [range(2000, 3000, 1000 // len(concepts))]

app = Flask(__name__)

def estimate_elo(encoded_history):
    lr = LogisticRegression(C=1e10)
    history = encoded_history.split(',')
    X = np.array(history[::2]).reshape(-1, 1)
    y = history[1::2]
    lr.fit(X, y)
    return -lr.intercept_/ lr.coef_, lr


@app.route("/quiz")
def choose_next_question():
    elo, _ = estimate_elo(request.args.get('q'))
    return f"<p>{elo}</p>"

@app.route("/report")
def generate_report():
    user_elo, lr = estimate_elo(request.args.get('q'))
    preds = np.round(100 * lr.predict_proba(np.array(elo_values).reshape(-1, 1))[:, 1])
    abilities = []
    for concept, proba in zip(concepts, preds):
        abilities.append(dict(concept=concept, proba=proba))
    return render_template("report.html", abilities=abilities)

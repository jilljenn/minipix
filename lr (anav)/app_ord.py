from flask import Flask, request, redirect, render_template, session
import numpy as np
from sklearn.linear_model import LogisticRegression
from statsmodels.miscmodels.ordinal_model import OrderedModel
from mord import LogisticAT

app = Flask(__name__)
app.secret_key = "secret_key"

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

topics = {i: name for i, name in enumerate(topic_names)}

topic_difficulties = {0:1200, 1:1200, 2:1500, 3:1700, 4:1800, 5:1900,
            6:2000, 7:2300, 8:1500, 9:2100, 10:1500, 11:1800,
            12:1700, 13:1900, 14:1900, 15:2200, 16:2200, 17:1900,
            18:1800, 19:2100, 20:1900, 21:2400, 22:2200, 23:1900,
            24:2300, 25:2400, 26:2100, 27:1200, 28:1500,29:1500,
            30:2200, 31:1700, 32:2200, 33:2200,34:1800, 35:1800,
            36:2200, 37:1800, 38:1900,39:1500, 40:2400, 41:2100}

@app.route("/")
def start():
    return redirect("/quiz?q=")

@app.route("/quiz")
def quiz():
    q_str = request.args.get("q", "")
    tokens = list(map(int, q_str.split(","))) if q_str else []
    q_a_pairs = list(zip(tokens[::2], tokens[1::2]))

    asked_ids = [q for q, _ in q_a_pairs]

    if len(q_a_pairs) >= 10:
        return redirect(f"/report?q={q_str}")

    if q_a_pairs:
        X = np.array([[topic_difficulties[q]] for q, _ in q_a_pairs])
        y = np.array([1 if a == 2 else 0 for _, a in q_a_pairs])

        X = np.append(X, [[1000], [3000]], axis=0)
        y = np.append(y, [1, 0])

        # Fit ordinal logistic regression model
        model = OrderedModel(endog=y, exog=X, distr='logit')
        res = model.fit(method='bfgs', disp=False)

        # Retrieve estimated user ELO by solving: X*beta ≈ threshold for response = 1.5
        beta = res.params[0]
        thresholds = res.model.cutoffs
        threshold = np.mean(thresholds)  # Midpoint between 1 and 2

        elo = threshold / beta

        # elo = -model.intercept_[0] / model.coef_[0][0]
    else:
        elo = 2000

    remaining = [tid for tid in topics if tid not in asked_ids]
    next_q = min(remaining, key=lambda q: abs(topic_difficulties[q] - elo))

    return render_template("question.html", q=next_q, q_str=q_str, topic_name=topics[next_q], elo=elo)

@app.route("/answer", methods=["POST"])
def answer():
    prev_q_str = request.form["q_str"]
    question_id = int(request.form["q_id"])
    answer = int(request.form["answer"])
    new_q_str = prev_q_str + f",{question_id},{answer}" if prev_q_str else f"{question_id},{answer}"
    return redirect(f"/quiz?q={new_q_str}")

@app.route("/report")
def report():
    q_str = request.args.get("q", "")
    tokens = list(map(int, q_str.split(","))) if q_str else []
    q_a_pairs = list(zip(tokens[::2], tokens[1::2]))

    if not q_a_pairs:
        return "No data."

    X = np.array([[topic_difficulties[q]] for q, _ in q_a_pairs])
    y = np.array([1 if a == 2 else 0 for _, a in q_a_pairs])

    X = np.append(X, [[1000], [3000]], axis=0)
    y = np.append(y, [1, 0])
    
    # model = LogisticRegression().fit(X, y)
    model = LogisticAT()
    model.fit(X, y)

    mastery = {
        q: round(model.predict_proba([[diff]])[0][1], 3)
        for q, diff in topic_difficulties.items()
    }
    sorted_mastery = sorted(mastery.items(), key=lambda x: x[1], reverse=True)
    elo = -model.intercept_[0] / model.coef_[0][0]

    return render_template("report.html", mastery=sorted_mastery, topics=topics, elo=elo)

if __name__ == "__main__":
    app.run(debug=True)

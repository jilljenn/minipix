from flask import Flask, request
from sklearn.linear_model import LogisticRegression
import numpy as np


app = Flask(__name__)

@app.route("/quiz")
def choose_next_question():
    lr = LogisticRegression(C=1e10)
    history = request.args.get('q').split(',')
    X = np.array(history[::2]).reshape(-1, 1)
    y = history[1::2]
    lr.fit(X, y)
    return f"<p>{-lr.intercept_/ lr.coef_}</p>"

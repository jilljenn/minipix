from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template, session
import os
import numpy as np
import pytz
from sklearn.linear_model import LogisticRegression
import uuid
from app import db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# initialize local sqlite DB and ensure topics are seeded
db.init_db()

app = Flask(__name__)
app.secret_key = SECRET_KEY

topics = {}
topic_difficulties = {}
for row in db.get_topics():
    topic_id = row["id"]
    topics[topic_id] = row["name"]
    topic_difficulties[topic_id] = row["difficulty"]

@app.route("/", methods=["GET"])
def home():
    session.clear()
    return render_template("start.html")

@app.route("/start-quiz", methods=["POST"])
def start_quiz():
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        
    data = {
        "id": str(uuid.uuid4()),
        "name": request.form["name"],
        "keyboard": request.form["keyboard_other"] or request.form["keyboard"],
        "language": request.form["language_other"] or request.form["language"],
        "ide": request.form["ide_other"] or request.form["ide"],
        "discord": request.form["discord"],
        "kattis": request.form["kattis"],
        "timestamp": datetime.now(pytz.timezone('UTC')).isoformat(timespec='seconds'),
        "ip_address": ip_address
    }

    session["quiz_started"] = True
    session["user_id"] = data["id"]
    db.insert_user_info(data)

    return redirect("/quiz?q=")

@app.route("/quiz")
def quiz():
    
    if not session.get("quiz_started"):
        return redirect("/")  
    
    q_str = request.args.get("q", "")
    tokens = list(map(int, q_str.split(","))) if q_str else []
    q_a_pairs = list(zip(tokens[::2], tokens[1::2]))
    previous_elo = None

    asked_ids = [q for q, _ in q_a_pairs]

    if len(q_a_pairs) >= 6:
        return redirect(f"/report?q={q_str}")

    if q_a_pairs:
        X = np.array([[topic_difficulties[q]] for q, _ in q_a_pairs])
        y = np.array([1 if a == 2 else 0 for _, a in q_a_pairs])

        X_prev_train = np.append(X[:-1], [[1000], [3800]], axis=0)
        y_prev_train = np.append(y[:-1], [1, 0])

        X_train = np.append(X, [[1000], [3800]], axis=0)
        y_train = np.append(y, [1, 0])

        model = LogisticRegression(C=1e10).fit(X_prev_train, y_prev_train)
        previous_elo = -model.intercept_[0] / model.coef_[0][0]
        model.fit(X_train, y_train)
        elo = -model.intercept_[0] / model.coef_[0][0]

        if len(q_a_pairs) >= 5 and abs(elo - previous_elo) < 2:
            return redirect(f"/report?q={q_str}")
    else:
        previous_elo = elo = 2400

    remaining = [tid for tid in topics if tid not in asked_ids]
    next_q = min(remaining, key=lambda q: abs(topic_difficulties[q] - elo))

    return render_template("question.html", q=next_q, q_str=q_str, topic_name=topics[next_q], elo=int(round(elo)))

@app.route("/answer", methods=["POST"])
def answer():
    prev_q_str = request.form["q_str"]
    question_id = int(request.form["q_id"])
    answer = int(request.form["answer"])
    user_id = session.get("user_id")

    response_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "topic_id": question_id,
        "answer": answer,
        "timestamp": datetime.now(pytz.timezone('UTC')).isoformat(),
    }

    db.insert_quiz_response(response_data)

    new_q_str = prev_q_str + f",{question_id},{answer}" if prev_q_str else f"{question_id},{answer}"
    return redirect(f"/quiz?q={new_q_str}")

@app.route("/report")
def report():

    q_str = request.args.get("q", "")
    tokens = list(map(int, q_str.split(","))) if q_str else []
    q_a_pairs = list(zip(tokens[::2], tokens[1::2]))

    if not q_a_pairs:
        return redirect("/")
    
    X = np.array([[topic_difficulties[q]] for q, _ in q_a_pairs])
    y = np.array([1 if a == 2 else 0 for _, a in q_a_pairs])

    X = np.append(X, [[1000], [3800]], axis=0)
    y = np.append(y, [1, 0])
    
    model = LogisticRegression(C=1e10).fit(X, y)

    mastery = {
        q: round(model.predict_proba([[diff]])[0][1], 2)
        for q, diff in topic_difficulties.items()
    }
    sorted_mastery = sorted(mastery.items(), key=lambda x: x[1], reverse=True)
    session["original_probs"] = mastery
    elo = -model.intercept_[0] / model.coef_[0][0]

    return render_template("report.html", mastery=sorted_mastery, topics=topics, elo=int(round(elo)))

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    user_id = session.get("user_id", "anonymous")
    records = []

    for key, value in request.form.items():
        if key.startswith("feedback_"):
            qid = key.split("feedback_")[1]
            predicted = session["original_probs"].get(qid, 0)  
            predicted = round(predicted, 2)
            feedback = float(value) / 100.0
            if feedback != predicted :
                records.append({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "topic_id": qid,
                    "predicted_value": predicted,
                    "feedback_value": feedback,
                    "timestamp": datetime.now(pytz.timezone('UTC')).isoformat()
                })
                
    if records:
        db.insert_mastery_feedback(records)

    return redirect("/thanks")

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


if __name__ == "__main__":
    app.run(debug=True)

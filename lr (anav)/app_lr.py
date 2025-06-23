from flask import Flask, request, redirect, render_template, session
import numpy as np
from sklearn.linear_model import LogisticRegression
from supabase import create_client, Client
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = "secret_key"

response = supabase.table("topic_info").select("*").execute()
topics = {}
topic_difficulties = {}

if response.data:
    for row in response.data:
        topic_id = row["id"]
        topics[topic_id] = row["name"]
        topic_difficulties[topic_id] = row["difficulty"]
else:
    print("No data found or error occurred:", response)

@app.route("/", methods=["GET"])
def home():
    return render_template("start.html")

@app.route("/start-quiz", methods=["POST"])
def start_quiz():
    data = {
        "id": str(uuid.uuid4()),
        "name": request.form["name"],
        "keyboard": request.form["keyboard"],
        "language": request.form["language_other"] or request.form["language"],
        "ide": request.form["ide"],
        "discord": request.form["discord"],
        "kattis": request.form["kattis"],
    }

    session["user_id"] = data["id"] 
    supabase.table("user_info").insert(data).execute()

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

        model = LogisticRegression().fit(X, y)
        elo = -model.intercept_[0] / model.coef_[0][0]
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
    user_id = session.get("user_id")

    response_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "topic_id": question_id,
        "answer": answer,
    }

    supabase.table("quiz_responses").insert(response_data).execute()

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
    
    model = LogisticRegression().fit(X, y)

    mastery = {
        q: round(model.predict_proba([[diff]])[0][1], 2)
        for q, diff in topic_difficulties.items()
    }
    sorted_mastery = sorted(mastery.items(), key=lambda x: x[1], reverse=True)
    session["original_probs"] = mastery
    elo = -model.intercept_[0] / model.coef_[0][0]

    return render_template("report.html", mastery=sorted_mastery, topics=topics, elo=elo)

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
                })

    supabase.table("mastery_feedback").insert(records).execute()

    return redirect("/thanks")

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


if __name__ == "__main__":
    app.run(debug=True)

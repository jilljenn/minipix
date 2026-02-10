# Minipix

Install dependencies:

    pip install flask numpy scikit-learn python-dotenv

(To make your life easier, [install uv](https://docs.astral.sh/uv/#highlights).)

Initialize the local SQLite database (seeds `topic_info` from `app/topics.csv` if empty):

    python -m app.db

Run the Flask app :

    FLASK_APP=app.app_lr uv run flask run

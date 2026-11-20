import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE = Path(__file__).resolve().with_name('ham_spam_predictions.db')

def init_db():
    """Initialize or upgrade the predictions table before the API starts."""
    with sqlite3.connect(str(DATABASE)) as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_content TEXT NOT NULL,
                result TEXT NOT NULL,
                prediction_date TEXT NOT NULL DEFAULT '',
                prediction_time TEXT NOT NULL DEFAULT ''
            )
        ''')
        # Upgrade databases created by earlier versions of the app.
        columns = {row[1] for row in cursor.execute('PRAGMA table_info(predictions)')}
        if 'prediction_date' not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN prediction_date TEXT NOT NULL DEFAULT ''")
        if 'prediction_time' not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN prediction_time TEXT NOT NULL DEFAULT ''")

def insert_prediction(email_content, result):
    """Inserts a prediction into the database."""
    now = datetime.now().astimezone()
    with sqlite3.connect(str(DATABASE)) as db:
        db.execute('''
            INSERT INTO predictions (email_content, result, prediction_date, prediction_time)
            VALUES (?, ?, ?, ?)
        ''', (email_content, result, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')))

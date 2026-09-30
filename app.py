from flask import Flask, request, redirect
import mysql.connector
import os
import time

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

def init_db():
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("Database table ready")
            break
        except Exception as e:
            print("Waiting for database...", e)
            time.sleep(3)

@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()
    cursor.close()
    conn.close()

    notes_html = ""

    for note in notes:
        notes_html += f"""
        <div class="note-card">
            <h3>{note["title"]}</h3>
            <p>{note["content"]}</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask Notes App</title>
        <style>
            body {{
                margin: 0;
                min-height: 100vh;
                background: #000;
                color: #fff;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                padding-top: 50px;
            }}

            .container {{
                width: 480px;
                background: #111;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 0 25px rgba(255, 140, 0, 0.35);
            }}

            h1 {{
                text-align: center;
                color: orange;
                font-size: 34px;
                margin-bottom: 25px;
            }}

            .form-group {{
                display: flex;
                flex-direction: column;
                margin-bottom: 18px;
            }}

            label {{
                font-size: 21px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #ffb347;
            }}

            input,
            textarea {{
                font-size: 18px;
                padding: 14px;
                border-radius: 8px;
                border: 1px solid #444;
                background: #1a1a1a;
                color: white;
            }}

            textarea {{
                min-height: 120px;
                resize: vertical;
            }}

            button {{
                width: 100%;
                padding: 15px;
                background: orange;
                color: black;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: bold;
                cursor: pointer;
            }}

            button:hover {{
                background: #ff8c00;
            }}

            .notes {{
                margin-top: 30px;
            }}

            .note-card {{
                background: #1a1a1a;
                padding: 18px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 5px solid orange;
            }}

            .note-card h3 {{
                font-size: 24px;
                color: orange;
                margin: 0 0 8px;
            }}

            .note-card p {{
                font-size: 18px;
                line-height: 1.5;
                margin: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Flask Notes App</h1>

            <form action="/add" method="POST">
                <div class="form-group">
                    <label>Note Title</label>
                    <input type="text" name="title" placeholder="Enter note title" required>
                </div>

                <div class="form-group">
                    <label>Note Content</label>
                    <textarea name="content" placeholder="Write your note" required></textarea>
                </div>

                <button type="submit">Add Note</button>
            </form>

            <div class="notes">
                {notes_html}
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/add", methods=["POST"])
def add_note():
    title = request.form["title"]
    content = request.form["content"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s)",
        (title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

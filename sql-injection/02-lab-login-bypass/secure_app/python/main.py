import sqlite3
from contextlib import closing
from flask import Flask, request, render_template_string

app = Flask(__name__)
DB_PATH = "users.db"


def init_db():
    """Initialize the database with a sample user."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        # Insert a sample user (in real life, password should be hashed)
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("administrator", "super_secret_password_123"),
        )
        conn.commit()


init_db()


LOGIN_PAGE = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<form method="post">
  <label>Username: <input name="username"></label><br>
  <label>Password: <input name="password" type="password"></label><br>
  <button type="submit">Log in</button>
</form>
{% if message %}<p><b>{{ message }}</b></p>{% endif %}
"""


@app.route("/", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = "SELECT * FROM users WHERE username = ? AND password = ?"

        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                user = conn.execute(query, (username, password)).fetchone()
                if user:
                    message = f"Welcome, {user['username']}! (id={user['id']})"
                else:
                    message = "Invalid credentials"
            except sqlite3.Error as e:
                app.logger.exception("login query failed")
                message = "Login failed, please try again."

    return render_template_string(LOGIN_PAGE, message=message)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
"""
curl -s http://localhost:8001 --cookie "TrackingId=TFYzlWqLrDp413AF"
"""
import sqlite3
from contextlib import closing
import logging
from flask import Flask, request, render_template_string


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
DB_PATH = "users.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )               
        """)
        # Insert a sample user
        connection.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("administrator", "supersecretpassword123"),
        )
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tracked_users (
                id INTEGER PRIMARY KEY,
                tracking_id TEXT NOT NULL UNIQUE
            )               
        """)
        # Insert a sample tracking ID
        connection.execute(
            "INSERT OR IGNORE INTO tracked_users (tracking_id) VALUES (?)",
            ("TFYzlWqLrDp413AF",),
        )
        connection.commit()

init_db()

LOGIN_PAGE = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<section>
    <a href="/">Home</a><p>|</p>
    {% if traced_msg %}<div>{{ traced_msg }}</div><p>|</p>{% endif %}
    <a href="/my-account">My account</a><p>|</p>
</section>
<form method="post" action="login">
  <label>Username: <input name="username"></label><br>
  <label>Password: <input name="password" type="password"></label><br>
  <button type="submit">Log in</button>
</form>
{% if message %}<p><b>{{ message }}</b></p>{% endif %}
"""

@app.route("/", methods=["GET"])
def get_page():
    traced_msg = None

    tracking_id = request.cookies.get("TrackingId", "")

    query = "SELECT tracking_id FROM tracked_users WHERE tracking_id = ?"
    
    # For learning: print the actual query that gets executed
    logging.debug(f"[DEBUG] Executing: {query}")

    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        try:
            tracked_user = conn.execute(query, (tracking_id,)).fetchone()
            if tracked_user:
                traced_msg = "Welcome back"
            else:
                traced_msg = ""
        except sqlite3.Error as e:
            # Leaking error messages also helps attackers — another bad practice
            logging.exception("[GetSession] Query tracked user failed, error=%s", e)

    return render_template_string(LOGIN_PAGE, traced_msg=traced_msg)

@app.route("/login", methods=["POST"])
def login():
    message = None
    
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
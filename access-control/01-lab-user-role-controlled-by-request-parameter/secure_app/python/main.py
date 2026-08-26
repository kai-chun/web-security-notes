import secrets
import sqlite3
import redis
from contextlib import closing
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)
DB_PATH = "users.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                is_admin BOOL NOT NULL
            )               
        """)
        # Insert admin
        connection.execute(
            "INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("administrator", "super_secret_password_123", True),
        )
        # Insert user: wiener
        connection.execute(
            "INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("wiener", "peter", False),
        )
        # Insert user: carlos
        connection.execute(
            "INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("carlos", "carlos_secret_password_123", False),
        )
        connection.commit()

init_db()

session_redis = None

def init_redis()  -> None:
    global session_redis
    session_redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

init_redis()

def get_user_info_by_session(session_id: str) -> tuple[str,str]:
    value = session_redis.get(session_id)
    try:
        pair_info = value.split(':')
    except Exception:
        

    return pair_info[0], pair_info[1]


LOGIN_PAGE = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<form method="post">
    <label>Username: <input name="username"></label><br>
    <label>Password: <input name="password" type="password"></label><br>
    <button type="submit">Log in</button>
</form>
"""

ADMIN_PAGE="""
<!doctype html>
<title>Admin</title>
<h1>Admin</h1>
<section>
    <h1>Users</h1>
    {% for user in users%}
    {% if not user["is_admin"] %}
    <div>
        <span>{{ user["username"] }} - </span>
        <a href="/admin/delete?username={{ user["username"] }}">Delete</a>
    </div>
    {% endif %}
    {% endfor %}
</section>
"""

ADMIN_FAILED_PAGE = """
<!doctype html>
<title>Admin</title>
<h1>Admin</h1>
<p>
Admin interface only available if logged in as an administrator
</p>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = "SELECT * FROM users WHERE username = ? AND password = ?"

        user = None
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                user = conn.execute(query, (username, password)).fetchone()
            except sqlite3.Error as e:
                app.logger.exception("login query failed")
        
        if user:
            session_id = secrets.token_hex(32)
            session_redis.setex(session_id, 3600, f"{username}:{password}")
            response = make_response("Login success!")
            response.set_cookie("Session", session_id, max_age=3600)
            return response
        else:
            response = make_response("Login failed!")
            return response
    else:
        return render_template_string(LOGIN_PAGE)


def _is_admin_user(username: str, password: str) -> bool:
    query = "SELECT * FROM users WHERE username = ? and password = ?"
    users = []
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        try:
            users = conn.execute(query, (username, password)).fetchone()
        except sqlite3.Error as e:
            app.logger.exception("users query failed")
    return users["is_admin"]

def _get_non_admin_users() -> list:
    query = "SELECT * FROM users WHERE is_admin = False"
    users = []
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        try:
            users = conn.execute(query).fetchall()
        except sqlite3.Error as e:
            app.logger.exception("users query failed")
    return users

@app.route("/admin", methods=["GET"])
def get_admin_page():
    session_id = request.cookies.get("Session", "")
    username, password = get_user_info_by_session(session_id)

    if _is_admin_user(username, password):
        users = _get_non_admin_users()
        return render_template_string(ADMIN_PAGE, users=users)

    return render_template_string(ADMIN_FAILED_PAGE)

@app.route("/admin/delete", methods=["GET"])
def delete_admin():
    deleted_user = request.args.get("username")
    session_id = request.cookies.get("Session", "")
    username, password = get_user_info_by_session(session_id)
    if deleted_user and _is_admin_user(username, password):
        delete_query = "DELETE FROM users WHERE username = ?"
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                users = conn.execute(delete_query, (deleted_user,))
                conn.commit()
            except sqlite3.Error as e:
                app.logger.exception("delete user failed, %s", deleted_user)
    if _is_admin_user(username, password):
        users = _get_non_admin_users()
        return render_template_string(ADMIN_PAGE, users=users)
    
    return render_template_string(ADMIN_FAILED_PAGE)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
from flask import Flask, render_template, request, redirect, session, g
import sqlite3
from models import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "unsafe-secret-key"  # ❌ Unsafe, needs to be fixed later

@app.before_request
def before_request():
    """Open database connection before each request"""
    g.db = get_db_connection()

@app.teardown_request
def teardown_request(exception):
    """Close database connection after each request"""
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login page if user is not logged in

    if request.method == "POST":
        content = request.form.get("content")
        user_id = session["user_id"]

        cursor = g.db.cursor()
        cursor.execute("INSERT INTO messages (user_id, content) VALUES (?, ?)", (user_id, content))
        g.db.commit()

    cursor = g.db.cursor()
    cursor.execute("SELECT messages.id, messages.content, messages.user_id, users.username FROM messages JOIN users ON messages.user_id = users.id")
    messages = cursor.fetchall()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    return render_template("index.html", messages=messages, users=users, session=session)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = 1 if username == "admin" else 0  # Make "admin" account an administrator

        try:
            cursor = g.db.cursor()
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
                           (username, password, is_admin))
            g.db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists, please choose another username"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor = g.db.cursor()
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]
            return redirect("/")
        else:
            return "Login failed, incorrect username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "is_admin" in session and session["is_admin"]:
        cursor = g.db.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        cursor.execute("DELETE FROM messages WHERE user_id=?", (user_id,))  # Cascade delete user's messages
        g.db.commit()
        return redirect("/")
    return "Insufficient permissions"

@app.route("/delete_message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if "user_id" in session:
        cursor = g.db.cursor()
        cursor.execute("SELECT user_id FROM messages WHERE id=?", (message_id,))
        message = cursor.fetchone()

        if message:
            if session["is_admin"] or session["user_id"] == message["user_id"]:
                cursor.execute("DELETE FROM messages WHERE id=?", (message_id,))
                g.db.commit()
                return redirect("/")
            else:
                return "No permission to delete"
    return "Please log in first"

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if "user_id" not in session:
        return redirect("/login")  # Unlogged users cannot edit comments

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM messages WHERE id=?", (message_id,))
    message = cursor.fetchone()

    if not message:
        return "Message does not exist"

    # Only the author of the comment can edit it
    if message["user_id"] != session["user_id"]:
        return "No permission to edit this message"

    if request.method == "POST":
        new_content = request.form.get("content")
        cursor.execute("UPDATE messages SET content=? WHERE id=?", (new_content, message_id))
        g.db.commit()
        return redirect("/")  # Return to homepage after editing

    return render_template("edit_message.html", message=message)

if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, session, g, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from models import get_db_connection
import init_db as init_database
import webbrowser
import threading
import time


app = Flask(__name__)
app.secret_key = "unsafe-secret-key"  # ❌ Hardcoded secret key (vulnerability)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists

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
    """Render chat page with messages"""
    if "user_id" not in session:
        return redirect("/login")

    cursor = g.db.cursor()

    # Store new messages
    if request.method == "POST":
        content = request.form.get("content")
        user_id = session["user_id"]
        cursor.execute("INSERT INTO messages (user_id, content) VALUES (?, ?)", (user_id, content))
        g.db.commit()

    # Fetch messages
    cursor.execute("SELECT messages.id, messages.content, messages.timestamp, messages.user_id, users.username FROM messages JOIN users ON messages.user_id = users.id")
    messages = cursor.fetchall()

    # Fetch all users for Admin Panel
    cursor.execute("SELECT id, username, is_admin FROM users")
    users = cursor.fetchall()

    return render_template("chat.html", messages=messages, users=users, session=session)

@app.route("/files", methods=["GET", "POST"])
def file_management():
    """Render file upload and download page"""
    if "user_id" not in session:
        return redirect("/login")

    cursor = g.db.cursor()

    if request.method == "POST":
        if "file" not in request.files:
            return "No file selected", 400

        file = request.files["file"]
        if file.filename == "":
            return "Empty file", 400

        if file and file.filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            cursor.execute("INSERT INTO files (filename, user_id) VALUES (?, ?)", (filename, session["user_id"]))
            g.db.commit()
            return redirect("/files")

    # Fetch files along with uploader's username
    cursor.execute("""
        SELECT files.id, files.filename, files.timestamp, files.user_id, users.username
        FROM files
        JOIN users ON files.user_id = users.id
    """)
    files = cursor.fetchall()

    return render_template("files.html", files=files, session=session)

@app.route("/uploads/<path:filename>")
def download_file(filename):
    """Allow users to download files"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Admin deletes a user"""
    if "is_admin" not in session or not session["is_admin"]:
        return "Unauthorized: You do not have permission to delete users", 403

    cursor = g.db.cursor()

    # Prevent admin from deleting themselves
    if session["user_id"] == user_id:
        return "You cannot delete your own account", 403

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Delete the user and their messages/files
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        cursor.execute("DELETE FROM messages WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM files WHERE user_id=?", (user_id,))
        g.db.commit()
        return redirect("/")
    
    return "User not found", 404

@app.route("/delete_message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    """Delete a message"""
    if "user_id" not in session:
        return redirect("/login")

    cursor = g.db.cursor()
    cursor.execute("SELECT user_id FROM messages WHERE id=?", (message_id,))
    message = cursor.fetchone()

    if message:
        if session["is_admin"] or session["user_id"] == message["user_id"]:
            cursor.execute("DELETE FROM messages WHERE id=?", (message_id,))
            g.db.commit()
            return redirect("/")
        else:
            return "No permission to delete", 403
    
    return "Message not found", 404

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    """Edit a message"""
    if "user_id" not in session:
        return redirect("/login")

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM messages WHERE id=?", (message_id,))
    message = cursor.fetchone()

    if not message:
        return "Message does not exist", 404

    # Only the author of the message can edit it
    if message["user_id"] != session["user_id"]:
        return "No permission to edit this message", 403

    if request.method == "POST":
        new_content = request.form.get("content")
        cursor.execute("UPDATE messages SET content=? WHERE id=?", (new_content, message_id))
        g.db.commit()
        return redirect("/")  # Return to homepage after editing

    return render_template("edit_message.html", message=message)

@app.route("/logout")
def logout():
    """Log out the current user"""
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = 1 if username.lower() == "admin" else 0  # ❌ Weak admin control

        try:
            cursor = g.db.cursor()
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
                           (username, password, is_admin))
            g.db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login (Vulnerable to SQL Injection)"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cursor = g.db.cursor()
        
        # ❌ Using string concatenation (unsafe)
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)  # ⚠️ This allows SQL injection
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            return redirect("/")
        else:
            return "Login failed"

    return render_template("login.html")

# SQL Injection Example:
# To bypass login, you can enter the following in the username field:
# ' OR 1=1 --
# And leave the password field empty. This will make the query always true and log you in without a valid password.

@app.route("/delete_file/<int:file_id>", methods=["POST"])
def delete_file(file_id):
    """Admin deletes an uploaded file"""
    if "is_admin" not in session or not session["is_admin"]:
        return "Unauthorized: You do not have permission to delete files", 403

    cursor = g.db.cursor()

    # Check if file exists
    cursor.execute("SELECT filename FROM files WHERE id=?", (file_id,))
    file = cursor.fetchone()

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)  # Delete the file from storage

        cursor.execute("DELETE FROM files WHERE id=?", (file_id,))
        g.db.commit()
        return redirect("/files")

    return "File not found", 404

def open_browser():
    """在 Flask 启动后自动打开浏览器"""
    time.sleep(1)  # 稍作等待，确保 Flask 已启动
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    init_database.init_db()
    app.run(debug=True, use_reloader=False)
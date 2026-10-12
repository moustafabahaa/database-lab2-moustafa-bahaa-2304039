import os

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("todos"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    name = ""
    email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")
        if not confirm:
            errors.append("Confirm password is required")
        if password and confirm and password != confirm:
            errors.append("Passwords do not match")

        if not errors:
            hashed = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            db = get_db()
            try:
                with db.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                        (email, name, hashed),
                    )
                    db.commit()
                    new_id = cur.lastrowid
                session["user_id"] = new_id
                session["name"] = name
                return redirect(url_for("todos"))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:
                    errors.append("Email Already Exists")
                else:
                    errors.append("Something went wrong, please try again")
            finally:
                db.close()

    return render_template("register.html", errors=errors, name=name, email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    email = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")

        if not errors:
            db = get_db()
            try:
                with db.cursor() as cur:
                    cur.execute(
                        "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                        (email,),
                    )
                    user = cur.fetchone()
            finally:
                db.close()

            if user and bcrypt.checkpw(
                password.encode("utf-8"), user["password_hash"].encode("utf-8")
            ):
                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                return redirect(url_for("todos"))

            errors.append("Invalid email or password")

    return render_template("login.html", errors=errors, email=email)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def check_title(title):
    if not title:
        return "Title is required"
    if len(title) > 200:
        return "Title is too long (200 characters at most)"
    return None


def show_todos(errors=None):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT todo_id, title, is_done, created_at FROM todos "
                "WHERE user_id = %s ORDER BY todo_id DESC",
                (session["user_id"],),
            )
            rows = cur.fetchall()
    finally:
        db.close()
    return render_template("todos.html", todos=rows, errors=errors or [])


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return show_todos()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    error = check_title(title)
    if error:
        return show_todos([error])
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                (session["user_id"], title),
            )
            db.commit()
    finally:
        db.close()
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    error = check_title(title)
    if error:
        return show_todos([error])
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
                (title, todo_id, session["user_id"]),
            )
            db.commit()
    finally:
        db.close()
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    is_done = 1 if request.form.get("is_done") == "1" else 0
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                (is_done, todo_id, session["user_id"]),
            )
            db.commit()
    finally:
        db.close()
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"]),
            )
            db.commit()
    finally:
        db.close()
    return redirect(url_for("todos"))


if __name__ == "__main__":
    app.run(debug=True)
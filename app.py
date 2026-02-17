import sqlite3
from flask import Flask, render_template, request, redirect, make_response
import uuid
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS students (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   uuid TEXT UNIQUE,
                   name TEXT
                   last_active TIMESTAMP)
                   """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("join.html")

@app.route("/join", methods=["POST"])
def join():
    student_name = request.form.get("name")

    if not student_name:
        return redirect("/")
    
    student_uuid = str(uuid.uuid4())

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (uuid, name) VALUES (?, ?)", (student_uuid, student_name)
    )
    conn.commit()
    conn.close()

    response = make_response(render_template("success.html", name = student_name))
    response.set_cookie("student_uuid", student_uuid)

    return response

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

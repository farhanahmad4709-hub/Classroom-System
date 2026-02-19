import sqlite3
from flask import Flask, render_template, request, redirect, make_response, session
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "my_secret_key"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS students (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   uuid TEXT UNIQUE,
                   name TEXT,
                   last_active TIMESTAMP)
                   """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    student_id = request.cookies.get("student_id")

    if student_id:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()

        conn.close()

        if student:

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE students SET last_active = ? WHERE id = ?", (current_time, student_id))
            conn.commit()
            return render_template("success.html", name=student[0])
    
    return render_template("join.html")
@app.route("/join", methods=["POST"])
def join():
    student_name = request.form.get("name")

    if not student_name:
        return redirect("/")
    
    student_uuid = str(uuid.uuid4())
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (uuid, name, last_active) VALUES (?, ?, ?)", (student_uuid, student_name, current_time)
    )
    conn.commit()

    student_id = cursor.lastrowid
    session['student_id'] = student_id
    conn.close()

    response = make_response(render_template("success.html", name = student_name))
    response.set_cookie("student_uuid", student_uuid)

    return response

@app.route("/teacher")
def teacher():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, last_active FROM students")
    students = cursor.fetchall()

    conn.close()

    student_status = []
    now = datetime.now()
    for s in students:
        student_id, name, last_active_str = s
        if last_active_str:
            try:
               last_active_time = datetime.strptime(last_active_str, "%Y-%m-%d %H:%M:%S")
               status = "ACTIVE" if (now - last_active_time).total_seconds() <= 10 else "INACTIVE"
            except ValueError:
                status = "INACTIVE"           
    else:
        status = "INACTIVE"
        student_status.append((student_id, name, last_active_str, status))

    return render_template("teacher.html", students=student_status)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)


from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

students = []

@app.route("/")
def join():
    return render_template("join.html")

@app.route("/submit", methods=["POST"])
def submit():
    student_name = request.form.get("name")
    students.append(student_name)
    current_time = datetime.now()
    # return f"Welcome, {student_name}! You are marked present."
    return render_template("success.html", name = student_name, time = current_time)

if __name__ == "__main__":
    app.run(debug=True)

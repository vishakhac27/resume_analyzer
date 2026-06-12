from flask import Flask, render_template, request, redirect, url_for
import os
from resume_parser import parse_resume
from db import get_connection
from career_engine import get_career_data

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"


def analyze_text(text):
    keywords = [
        "python",
        "flask",
        "sql",
        "django",
        "api",
        "html",
        "css",
        "javascript"
    ]

    text = text.lower()

    matched = sum(1 for kw in keywords if kw in text)
    score = int((matched / len(keywords)) * 100)

    breakdown = {
        "skills_match": score,
        "formatting": min(score + 10, 100),
        "experience": max(score - 10, 0)
    }

    feedback = []

    if score >= 80:
        feedback.append("Excellent ATS optimization.")
        feedback.append("Strong keyword coverage.")
    elif score >= 50:
        feedback.append("Good resume but needs more relevant keywords.")
        feedback.append("Improve project descriptions.")
    else:
        feedback.append("Add more technical skills.")
        feedback.append("Improve ATS keyword matching.")
        feedback.append("Add stronger project experience.")

    return score, breakdown, feedback



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/resume", methods=["GET", "POST"])
def resume():

    if request.method == "POST":

        file = request.files.get("resume")

        if not file or file.filename == "":
            return redirect(url_for("resume"))

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        try:
            text = parse_resume(filepath)

            score, breakdown, feedback = analyze_text(text)

            return render_template(
                "resume_analyzer.html",
                show_result=True,
                score=score,
                breakdown=breakdown,
                feedback=feedback
            )

        except Exception as e:
            return render_template(
                "resume_analyzer.html",
                show_result=False,
                error=f"Error analyzing resume: {str(e)}"
            )

    return render_template(
        "resume_analyzer.html",
        show_result=False,
        score=None,
        breakdown=None,
        feedback=None
    )

@app.route("/assessment")
def take_assessment():
    return render_template("career_assessment.html")

@app.route("/result", methods=["POST"])
def result():

    name = request.form["name"]
    education = request.form["education"]
    skills = request.form["skills"]
    interests = request.form["interests"]
    goal = request.form["goal"]

    career_data = get_career_data(name, education, skills, interests, goal)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assessments
        (name, education, skills, interests, goal, career, score)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        name,
        education,
        skills,
        interests,
        goal,
        career_data["career"],
        career_data["score"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template(
        "assessment_result.html",
        name=name,
        education=education,
        skills=skills,
        interests=interests,
        goal=goal,
        career=career_data["career"],
        score=career_data["score"],
        technologies=career_data["technologies"],
        roadmap=career_data["roadmap"]
    )


@app.route("/history")
def history():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM assessments
        ORDER BY created_at DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("assessment_history.html", records=records)

if __name__ == "__main__":
    app.run(debug=True)
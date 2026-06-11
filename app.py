from flask import Flask, render_template, request, redirect, url_for
import os
from resume_parser import parse_resume

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


if __name__ == "__main__":
    app.run(debug=True)
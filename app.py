from flask import Flask, render_template, request, redirect, url_for, session
import os
from resume_parser import parse_resume

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session
app.config["UPLOAD_FOLDER"] = "uploads"


def analyze_text(text):
    keywords = ["python", "flask", "sql", "django", "api", "html", "css", "javascript"]

    text = text.lower()
    matched = sum(1 for kw in keywords if kw in text)
    score = int((matched / len(keywords)) * 100)

    breakdown = {
        "skills_match": score,
        "formatting": min(score + 10, 100),
        "experience": max(score - 10, 0)
    }

    feedback = ["Good resume 👍"] if score > 60 else ["Improve skills section"]

    return score, breakdown, feedback


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        file = request.files.get("resume")

        if not file or file.filename == "":
            return redirect(url_for("home"))

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        text = parse_resume(path)
        score, breakdown, feedback = analyze_text(text)

        # store in session (SAFE)
        session["show_result"] = True
        session["score"] = score
        session["breakdown"] = breakdown
        session["feedback"] = feedback

        return redirect(url_for("home"))

    # GET request → ALWAYS clean render
    return render_template(
        "index.html",
        show_result=session.pop("show_result", False),
        score=session.pop("score", None),
        breakdown=session.pop("breakdown", None),
        feedback=session.pop("feedback", None)
    )


if __name__ == "__main__":
    app.run(debug=True)
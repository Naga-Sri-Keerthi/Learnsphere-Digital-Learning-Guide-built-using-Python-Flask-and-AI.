from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from ai_service import (
    generate_learning_content,
    generate_quiz,
    ask_ai
)

from youtube_service import search_videos

from database import (
    init_db,
    save_quiz_result,
    save_progress,
    get_progress,
    get_topic_progress
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "learnsphere-development-secret-key"


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# LEARNING PAGE
# ============================================================

@app.route("/learning", methods=["POST"])
def learning():

    topic = request.form.get("topic", "").strip()

    level = request.form.get("level", "Beginner").strip()

    # If topic is empty, go back to home
    if not topic:
        return redirect(url_for("index"))

    # Generate AI learning content
    content = generate_learning_content(
        topic,
        level
    )

    # Search YouTube videos
    videos = search_videos(topic)

    # Store current learning information in session
    session["topic"] = topic
    session["level"] = level
    session["content"] = content
    session["videos"] = videos

    # Get progress for this topic
    topic_progress = get_progress(topic)

    return render_template(
        "learning.html",
        topic=topic,
        level=level,
        content=content,
        videos=videos,
        progress=topic_progress
    )


# ============================================================
# QUIZ PAGE
# ============================================================

@app.route("/quiz")
def quiz():

    # Get current topic and level
    topic = session.get(
        "topic",
        "Cyber Security"
    )

    level = session.get(
        "level",
        "Beginner"
    )

    # Generate quiz
    questions = generate_quiz(
        topic,
        level
    )

    # Make sure there are at least 5 questions
    if len(questions) < 5:

        extra_questions = fallback_quiz(topic)

        required = 5 - len(questions)

        questions = questions + extra_questions[:required]

    # Never allow more than 10 questions
    questions = questions[:10]

    # Store quiz in session
    session["quiz_questions"] = questions

    return render_template(
        "quiz.html",
        topic=topic,
        questions=questions
    )


# ============================================================
# SUBMIT QUIZ
# ============================================================

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    # Get topic
    topic = session.get(
        "topic",
        "Unknown Topic"
    )

    # Get quiz questions
    questions = session.get(
        "quiz_questions",
        []
    )

    score = 0

    answers = []


    # --------------------------------------------------------
    # CHECK EACH QUESTION
    # --------------------------------------------------------

    for i, question in enumerate(questions):

        # Get selected answer
        selected = request.form.get(
            f"q{i}"
        )

        # Get correct answer
        correct = str(
            question.get("answer", "")
        )

        # Check answer
        is_correct = (
            selected == correct
        )

        if is_correct:
            score += 1

        # Store answer information
        answers.append({

            "question": question.get(
                "question",
                ""
            ),

            "selected": selected,

            "correct": correct,

            "is_correct": is_correct,

            "options": question.get(
                "options",
                []
            )
        })


    # --------------------------------------------------------
    # CALCULATE SCORE
    # --------------------------------------------------------

    total = len(questions)

    if total > 0:
        percentage = round(
            (score / total) * 100
        )
    else:
        percentage = 0


    # --------------------------------------------------------
    # SAVE QUIZ RESULT
    # --------------------------------------------------------

    save_quiz_result(
        topic,
        score,
        total,
        percentage
    )


    # --------------------------------------------------------
    # SAVE LEARNING PROGRESS
    # --------------------------------------------------------

    save_progress(
        topic,
        percentage,
        completed=True
    )


    # Store latest result in session
    session["last_score"] = score
    session["last_total"] = total
    session["last_percentage"] = percentage


    # --------------------------------------------------------
    # SHOW RESULT PAGE
    # --------------------------------------------------------

    return render_template(
        "quiz_result.html",

        topic=topic,

        score=score,

        total=total,

        percentage=percentage,

        answers=answers
    )


# ============================================================
# ASK AI
# ============================================================

@app.route("/ask-ai", methods=["POST"])
def ask():

    data = request.get_json(
        silent=True
    ) or {}

    # Get topic
    topic = (
        data.get("topic")
        or session.get("topic", "")
    )

    # Get question
    question = (
        data.get("question", "")
        .strip()
    )

    # Empty question
    if not question:

        return jsonify({
            "answer": "Please enter a question."
        })


    # Ask Gemini
    answer = ask_ai(
        topic,
        question
    )

    return jsonify({
        "answer": answer
    })


# ============================================================
# PROGRESS PAGE
# ============================================================

@app.route("/progress")
def progress():

    # Get all saved progress records
    records = get_progress()

    return render_template(
        "progress.html",
        records=records
    )


# ============================================================
# COMPANY PAGE
# ============================================================

@app.route("/company")
def company():

    return render_template(
        "company.html"
    )


# ============================================================
# FALLBACK QUIZ
# ============================================================

def fallback_quiz(topic):

    return [

        {
            "question":
                f"What is the main purpose of learning {topic}?",

            "options": [
                "To understand and apply its concepts",
                "To avoid practice",
                "Only to memorize terms",
                "None of these"
            ],

            "answer":
                "To understand and apply its concepts"
        },


        {
            "question":
                f"Which approach is useful when studying {topic}?",

            "options": [
                "Learn step by step",
                "Skip all basics",
                "Avoid examples",
                "Never practice"
            ],

            "answer":
                "Learn step by step"
        },


        {
            "question":
                f"What helps improve understanding of {topic}?",

            "options": [
                "Practice and examples",
                "Ignoring feedback",
                "Skipping exercises",
                "Guessing everything"
            ],

            "answer":
                "Practice and examples"
        },


        {
            "question":
                f"Why are real-world examples useful for {topic}?",

            "options": [
                "They connect theory with practical use",
                "They replace all learning",
                "They make practice unnecessary",
                "They are unrelated"
            ],

            "answer":
                "They connect theory with practical use"
        },


        {
            "question":
                f"What is a good final step after studying {topic}?",

            "options": [
                "Take a quiz and review mistakes",
                "Stop immediately",
                "Delete your notes",
                "Avoid revision"
            ],

            "answer":
                "Take a quiz and review mistakes"
        }

    ]


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

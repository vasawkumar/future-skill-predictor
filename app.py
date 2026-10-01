from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "database/database.db"


# -----------------------------
# Skill Recommendation System
# -----------------------------

def recommend_skills(student):

    recommendations = []

    interests = (student["interests"] or "").lower()
    subjects = (student["subjects"] or "").lower()
    career = (student["career"] or "").lower()
    skills = (student["skills"] or "").lower()

    if "technology" in interests or "computer" in subjects or "technology" in career:
        recommendations.append("Python Programming")
        recommendations.append("Artificial Intelligence")
        recommendations.append("Web Development")

    if "science" in interests or "science" in subjects or "science" in career:
        recommendations.append("Data Science")
        recommendations.append("Research Skills")

    if "design" in interests or "design" in career:
        recommendations.append("UI/UX Design")
        recommendations.append("Graphic Design")

    if "business" in interests or "business" in career:
        recommendations.append("Business Analytics")
        recommendations.append("Communication Skills")

    if "cybersecurity" in career:
        recommendations.append("Cybersecurity")
        recommendations.append("Networking")

    if "python" not in skills:
        recommendations.append("Python Programming")

    # Remove duplicate recommendations
    recommendations = list(dict.fromkeys(recommendations))

    return recommendations[:6]


# -----------------------------
# Database
# -----------------------------
def create_roadmap(student):

    career = (student["career"] or "").lower()
    interests = (student["interests"] or "").lower()

    roadmap = []

    # Technology / Computer
    if "technology" in career or "technology" in interests:
        roadmap = [
            ("Step 1", "Learn Python Basics",
             "Learn variables, loops, functions and basic programming."),

            ("Step 2", "Practice Problem Solving",
             "Solve simple coding and logical problems."),

            ("Step 3", "Explore Artificial Intelligence",
             "Learn the basic concepts of AI and machine learning."),

            ("Step 4", "Build a Small Project",
             "Create a simple Python or AI project.")
        ]

    # Cybersecurity
    elif "cybersecurity" in career:
        roadmap = [
            ("Step 1", "Learn Computer Basics",
             "Understand computers, operating systems and networks."),

            ("Step 2", "Learn Networking",
             "Understand IP addresses, protocols and basic networking."),

            ("Step 3", "Learn Cybersecurity Basics",
             "Explore common security concepts and threats."),

            ("Step 4", "Build a Security Project",
             "Create a small cybersecurity-related project.")
        ]

    # Design
    elif "design" in career or "design" in interests:
        roadmap = [
            ("Step 1", "Learn Design Basics",
             "Learn color, typography and visual design principles."),

            ("Step 2", "Learn UI/UX",
             "Understand how to design user-friendly interfaces."),

            ("Step 3", "Practice Design Tools",
             "Create designs using digital design tools."),

            ("Step 4", "Build a Design Portfolio",
             "Create small projects to showcase your design skills.")
        ]

    # Default roadmap
    else:
        roadmap = [
            ("Step 1", "Explore Your Interests",
             "Identify subjects and skills you enjoy."),

            ("Step 2", "Learn a New Skill",
             "Choose one useful skill and learn its basics."),

            ("Step 3", "Practice Problem Solving",
             "Apply your knowledge through exercises and challenges."),

            ("Step 4", "Build a Project",
             "Create a small project using what you learned.")
        ]

    return roadmap
def init_db():

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_class TEXT NOT NULL,
            subjects TEXT,
            interests TEXT,
            skills TEXT,
            hobbies TEXT,
            career TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            step INTEGER
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# Learning Progress
# -----------------------------

@app.route("/complete/<int:step>")
def complete_step(step):

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            step INTEGER
        )
    """)

    # Get latest student
    student = conn.execute(
        "SELECT id FROM students ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if student:
        student_id = student[0]

        # Check if step is already completed
        existing = conn.execute(
            "SELECT * FROM progress WHERE student_id = ? AND step = ?",
            (student_id, step)
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO progress (student_id, step) VALUES (?, ?)",
                (student_id, step)
            )

    conn.commit()
    conn.close()

    return redirect("/dashboard")
# -----------------------------
# Home Page
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# Profile Page
# -----------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        name = request.form.get("name")
        student_class = request.form.get("class")

        subjects = request.form.getlist("subjects")
        interests = request.form.getlist("interests")

        skills = request.form.get("skills")
        hobbies = request.form.get("hobbies")
        career = request.form.get("career")

        subjects = ", ".join(subjects)
        interests = ", ".join(interests)

        conn = sqlite3.connect(DATABASE)

        conn.execute("""
            INSERT INTO students
            (name, student_class, subjects, interests, skills, hobbies, career)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            student_class,
            subjects,
            interests,
            skills,
            hobbies,
            career
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("profile.html")


# -----------------------------
# Dashboard
# -----------------------------



@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    student = conn.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if student is None:
        conn.close()
        return redirect("/profile")

    # Get completed roadmap steps
    completed_rows = conn.execute(
        "SELECT step FROM progress WHERE student_id = ?",
        (student["id"],)
    ).fetchall()

    completed_steps = [row["step"] for row in completed_rows]

    conn.close()

    recommendations = recommend_skills(student)
    roadmap = create_roadmap(student)

    return render_template(
        "dashboard.html",
        student=student,
        recommendations=recommendations,
        roadmap=roadmap,
        completed_steps=completed_steps
    )
# -----------------------------
# Start Application
# -----------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
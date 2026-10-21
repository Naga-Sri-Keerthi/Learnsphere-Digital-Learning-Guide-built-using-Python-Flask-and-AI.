import os
import json
import re
import requests

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()


# ============================================================
# CALL GEMINI API
# ============================================================

def call_gemini(prompt):
    """
    Sends a prompt to Google Gemini and returns the generated text.
    """

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is missing.")
        return None

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=45
        )

        # Print response in terminal for debugging
        print("Gemini Status:", response.status_code)
        print("Gemini Response:", response.text)

        if response.status_code != 200:
            return None

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            print("ERROR: No candidates returned by Gemini.")
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        if not parts:
            print("ERROR: No response parts returned by Gemini.")
            return None

        answer = parts[0].get("text", "")

        if answer:
            return answer.strip()

        return None

    except requests.exceptions.Timeout:
        print("ERROR: Gemini request timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Gemini.")
        return None

    except Exception as e:
        print("Gemini Error:", e)
        return None


# ============================================================
# CLEAN JSON RESPONSE
# ============================================================

def clean_json(text):
    """
    Converts Gemini's response into Python JSON.
    """

    if not text:
        return None

    text = text.strip()

    # Remove markdown code blocks
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # First attempt
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to find JSON object
    object_match = re.search(r"\{.*\}", text, re.DOTALL)

    if object_match:
        try:
            return json.loads(object_match.group(0))
        except Exception:
            pass

    # Try to find JSON array
    array_match = re.search(r"\[.*\]", text, re.DOTALL)

    if array_match:
        try:
            return json.loads(array_match.group(0))
        except Exception:
            pass

    return None


# ============================================================
# GENERATE LEARNING CONTENT
# ============================================================

def generate_learning_content(topic, level):

    prompt = f"""
You are an AI educational assistant for LearnSphere.

Create a structured educational learning page for:

Topic: {topic}
Level: {level}

Return ONLY valid JSON.

Use exactly these keys:

{{
    "explanation": "string",

    "learning_path": [
        "step 1",
        "step 2",
        "step 3",
        "step 4",
        "step 5"
    ],

    "important_concepts": [
        "concept 1",
        "concept 2",
        "concept 3",
        "concept 4",
        "concept 5"
    ],

    "key_points": [
        "point 1",
        "point 2",
        "point 3",
        "point 4",
        "point 5"
    ],

    "real_world_examples": [
        "example 1",
        "example 2",
        "example 3"
    ],

    "quick_facts": [
        "fact 1",
        "fact 2",
        "fact 3",
        "fact 4"
    ]
}}

Requirements:

- Make everything specifically about {topic}.
- Use simple student-friendly language.
- Match the {level} level.
- Do not give generic study advice.
- learning_path must contain exactly 5 steps.
- important_concepts must contain exactly 5 concepts.
- key_points must contain exactly 5 points.
- real_world_examples must contain exactly 3 examples.
- quick_facts must contain exactly 4 facts.
- Return ONLY JSON.
"""

    response = call_gemini(prompt)

    data = clean_json(response)

    if isinstance(data, dict):
        return data

    print("Using fallback learning content.")

    return fallback_content(topic, level)


# ============================================================
# GENERATE QUIZ
# ============================================================

def generate_quiz(topic, level):

    prompt = f"""
You are an AI quiz generator for LearnSphere.

Create 10 multiple-choice questions about:

Topic: {topic}
Level: {level}

Return ONLY a valid JSON array.

Every question must have exactly this structure:

{{
    "question": "Question text",
    "options": [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4"
    ],
    "answer": "Correct option"
}}

Requirements:

- Create exactly 10 questions.
- Questions must be specifically about {topic}.
- Questions must match the {level} level.
- Each question must have exactly 4 options.
- The answer must exactly match one of the 4 options.
- Do not include explanations.
- Do not include markdown.
- Return ONLY JSON.
"""

    response = call_gemini(prompt)

    data = clean_json(response)

    if isinstance(data, list):

        valid_questions = []

        for question in data:

            if not isinstance(question, dict):
                continue

            options = question.get("options", [])
            answer = question.get("answer")
            question_text = question.get("question")

            if (
                isinstance(question_text, str)
                and isinstance(options, list)
                and len(options) == 4
                and isinstance(answer, str)
                and answer in options
            ):
                valid_questions.append({
                    "question": question_text,
                    "options": options,
                    "answer": answer
                })

        if len(valid_questions) >= 5:
            return valid_questions[:10]

    print("Using fallback quiz.")

    return fallback_quiz(topic)


# ============================================================
# ASK AI
# ============================================================

def ask_ai(topic, question):

    prompt = f"""
You are the AI learning assistant inside LearnSphere.

The student is currently learning:

Topic: {topic}

Student's question:

{question}

Answer the student's question clearly and accurately.

Rules:

- Use simple language.
- Explain difficult terms.
- Give an example when useful.
- Stay focused on {topic}.
- Do not give unnecessary information.
- Keep the answer easy for a student to understand.
"""

    answer = call_gemini(prompt)

    if answer:
        return answer

    if not GEMINI_API_KEY:
        return (
            "Gemini API key is missing. "
            "Please create a .env file in the LearnSphere project folder "
            "and add your GEMINI_API_KEY, then restart Flask."
        )

    return (
        "The AI service could not respond right now. "
        "Please check your API key, Gemini model, and internet connection."
    )


# ============================================================
# FALLBACK LEARNING CONTENT
# ============================================================

def fallback_content(topic, level):

    return {

        "explanation": (
            f"{topic} is an important subject that can be learned "
            f"step by step. This {level.lower()} learning guide introduces "
            f"the main ideas, practical uses, and important concepts of {topic}."
        ),

        "learning_path": [
            f"Introduction to {topic}",
            f"Basic concepts of {topic}",
            f"Important tools and techniques in {topic}",
            f"Practical applications of {topic}",
            "Review, practice and next steps"
        ],

        "important_concepts": [
            f"Fundamentals of {topic}",
            f"Core terminology in {topic}",
            f"Common methods used in {topic}",
            f"Practical applications of {topic}",
            f"Best practices in {topic}"
        ],

        "key_points": [
            f"Understand the basics of {topic} first.",
            f"Learn the important terminology of {topic}.",
            f"Practice the core concepts of {topic}.",
            f"Connect concepts with real-world examples.",
            f"Review mistakes and continue learning."
        ],

        "real_world_examples": [
            f"Real-world applications of {topic}",
            f"Industry use cases related to {topic}",
            f"Projects that demonstrate {topic}"
        ],

        "quick_facts": [
            f"{topic} is used in practical learning and professional work.",
            "Step-by-step learning improves understanding.",
            "Practice helps connect theory with application.",
            "Revision and quizzes help measure progress."
        ]
    }


# ============================================================
# FALLBACK QUIZ
# ============================================================

def fallback_quiz(topic):

    return [

        {
            "question": f"What is the main purpose of {topic}?",
            "options": [
                f"Understanding and applying {topic}",
                "Avoiding practice",
                "Only memorizing terms",
                "None of these"
            ],
            "answer": f"Understanding and applying {topic}"
        },

        {
            "question": f"Which is a useful way to learn {topic}?",
            "options": [
                "Step-by-step learning",
                "Skipping fundamentals",
                "Avoiding examples",
                "Never practicing"
            ],
            "answer": "Step-by-step learning"
        },

        {
            "question": f"What improves practical understanding of {topic}?",
            "options": [
                "Examples and practice",
                "Ignoring feedback",
                "Skipping exercises",
                "Guessing"
            ],
            "answer": "Examples and practice"
        },

        {
            "question": f"Why are real-world examples useful in {topic}?",
            "options": [
                "They connect theory to practice",
                "They replace learning",
                "They remove the need for revision",
                "They are unrelated"
            ],
            "answer": "They connect theory to practice"
        },

        {
            "question": f"What should a learner do after studying {topic}?",
            "options": [
                "Take a quiz and review mistakes",
                "Stop learning",
                "Delete notes",
                "Avoid revision"
            ],
            "answer": "Take a quiz and review mistakes"
        }

    ]

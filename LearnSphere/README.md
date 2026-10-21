# LearnSphere – Updated Project

## Features
- Search any topic and generate topic-specific learning content.
- Beginner, Intermediate and Advanced levels.
- Structured learning path, concepts, key points, examples and quick facts.
- Topic-related YouTube videos.
- AI assistant.
- Minimum 5-question multiple-choice quiz.
- Automatic score and percentage.
- SQLite progress tracking.
- Attractive responsive UI based on the supplied LearnSphere reference design.

## Run
1. Open a terminal in this folder.
2. Create a virtual environment:
   `python -m venv venv`
3. Activate it:
   Windows: `venv\Scripts\activate`
4. Install:
   `pip install -r requirements.txt`
5. Optional: set GEMINI_API_KEY and YOUTUBE_API_KEY.
6. Run:
   `python app.py`
7. Open `http://127.0.0.1:5000`

If API keys are not configured, the app still runs using fallback learning content, fallback quiz questions and YouTube search links. For fully topic-specific AI content and AI-generated quizzes, configure GEMINI_API_KEY.

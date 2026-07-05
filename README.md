# Finance Flashcards Web App

A Python Flask web application that presents finance facts as multiple-choice questions with automatic scoring.

## Features

- **Random Finance Questions**: 20 randomly selected finance questions per quiz
- **Multiple Choice**: Each question has 1 correct answer and 3 plausible incorrect answers
- **Score Tracking**: Real-time score tracking during the quiz
- **Session Memory**: Scores stored in session (no database required)

## Requirements

- Python 3.7+
- Flask
- Requests (for fetching finance data)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bigvillagesolutions/finance-flashcards.git
cd finance-flashcards
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

## Usage

1. Click "Start Quiz" to begin a new 20-question finance flashcard session
2. Answer each question by selecting one of the four options
3. Click "Submit" to check your answer
4. Your score updates automatically
5. Continue through all 20 questions
6. View your final score at the end

## Project Structure

```
finance-flashcards/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── finance_facts.json     # Finance facts database
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── quiz.html         # Quiz page
│   └── results.html      # Results page
└── static/
    └── style.css         # CSS styling
```

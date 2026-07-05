from flask import Flask, render_template, request, session, jsonify
import json
import random
import os
from datetime import timedelta

# Get the absolute path to the app directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = 'your-secret-key-change-this'
app.permanent_session_lifetime = timedelta(hours=1)

# Load finance facts
facts_file = os.path.join(BASE_DIR, 'finance_facts.json')
print(f"Loading facts from: {facts_file}")
print(f"File exists: {os.path.exists(facts_file)}")

try:
    with open(facts_file, 'r') as f:
        all_facts = json.load(f)
    print(f"Successfully loaded {len(all_facts)} finance facts")
except Exception as e:
    print(f"ERROR loading finance_facts.json: {e}")
    all_facts = []

def load_quiz_questions(num_questions=20):
    """Load random questions for the quiz"""
    if not all_facts:
        return []
    
    selected_facts = random.sample(all_facts, min(num_questions, len(all_facts)))
    quiz_questions = []
    
    for fact in selected_facts:
        # Create choices with correct and incorrect answers
        choices = [fact['correct_answer']] + fact['incorrect_answers']
        random.shuffle(choices)
        
        quiz_questions.append({
            'question': fact['question'],
            'choices': choices,
            'correct_answer': fact['correct_answer']
        })
    
    return quiz_questions

@app.route('/')
def index():
    """Home page"""
    print("Route: /")
    return render_template('index.html')

@app.route('/start_quiz')
def start_quiz():
    """Start a new quiz session"""
    print("Route: /start_quiz")
    session.permanent = True
    quiz_questions = load_quiz_questions(20)
    session['quiz_questions'] = quiz_questions
    session['current_question'] = 0
    session['score'] = 0
    session['answered'] = False
    session['selected_answer'] = None
    
    return render_template('quiz.html',
                         question_num=1,
                         total_questions=20,
                         score=0)

@app.route('/api/question')
def get_question():
    """Get current question"""
    if 'quiz_questions' not in session:
        return jsonify({'error': 'No quiz in progress'}), 400
    
    current_idx = session.get('current_question', 0)
    quiz_questions = session['quiz_questions']
    
    if current_idx >= len(quiz_questions):
        return jsonify({'error': 'Quiz completed'}), 400
    
    question = quiz_questions[current_idx]
    return jsonify({
        'question_num': current_idx + 1,
        'total_questions': len(quiz_questions),
        'question': question['question'],
        'choices': question['choices'],
        'score': session.get('score', 0),
        'answered': session.get('answered', False),
        'selected_answer': session.get('selected_answer')
    })

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    """Submit an answer"""
    data = request.json
    selected_answer = data.get('answer')
    
    if 'quiz_questions' not in session:
        return jsonify({'error': 'No quiz in progress'}), 400
    
    current_idx = session.get('current_question', 0)
    quiz_questions = session['quiz_questions']
    
    if current_idx >= len(quiz_questions):
        return jsonify({'error': 'Quiz completed'}), 400
    
    question = quiz_questions[current_idx]
    correct_answer = question['correct_answer']
    is_correct = selected_answer == correct_answer
    
    # Update score if answer is correct
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    session['answered'] = True
    session['selected_answer'] = selected_answer
    session.modified = True
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'score': session['score']
    })

@app.route('/api/next')
def next_question():
    """Move to next question"""
    if 'quiz_questions' not in session:
        return jsonify({'error': 'No quiz in progress'}), 400
    
    current_idx = session.get('current_question', 0)
    quiz_questions = session['quiz_questions']
    
    # Move to next question
    session['current_question'] = current_idx + 1
    session['answered'] = False
    session['selected_answer'] = None
    session.modified = True
    
    if current_idx + 1 >= len(quiz_questions):
        # Quiz completed
        return jsonify({
            'quiz_completed': True,
            'final_score': session['score'],
            'total_questions': len(quiz_questions)
        })
    
    return jsonify({'quiz_completed': False})

@app.route('/results')
def results():
    """Show quiz results"""
    score = session.get('score', 0)
    total = 20
    percentage = (score / total * 100) if total > 0 else 0
    
    return render_template('results.html',
                         score=score,
                         total=total,
                         percentage=percentage)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error', 'message': str(e)}), 500

if __name__ == '__main__':
    print(f"Template folder: {os.path.join(BASE_DIR, 'templates')}")
    print(f"Static folder: {os.path.join(BASE_DIR, 'static')}")
    print("Starting Flask app on http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000)

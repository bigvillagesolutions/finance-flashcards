from flask import Flask, render_template, request, session, jsonify
import json
import random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.permanent_session_lifetime = timedelta(hours=1)

# Load finance facts
with open('finance_facts.json', 'r') as f:
    all_facts = json.load(f)

def load_quiz_questions(num_questions=20):
    """Load random questions for the quiz"""
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
    return render_template('index.html')

@app.route('/start_quiz')
def start_quiz():
    """Start a new quiz session"""
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

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)

from flask import Flask, render_template, request, session, jsonify
import json
import random
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = 'finance-flashcards-secret'
app.permanent_session_lifetime = timedelta(hours=1)

# Load finance facts
facts_file = os.path.join(BASE_DIR, 'finance_facts.json')
with open(facts_file, 'r') as f:
    all_facts = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_quiz')
def start_quiz():
    session.permanent = True
    selected_facts = random.sample(all_facts, min(20, len(all_facts)))
    
    quiz = []
    for fact in selected_facts:
        choices = [fact['correct_answer']] + fact['incorrect_answers']
        random.shuffle(choices)
        quiz.append({
            'question': fact['question'],
            'choices': choices,
            'correct': fact['correct_answer']
        })
    
    session['quiz'] = quiz
    session['current'] = 0
    session['score'] = 0
    
    return render_template('quiz.html')

@app.route('/question')
def get_question():
    quiz = session.get('quiz', [])
    current = session.get('current', 0)
    
    if current >= len(quiz):
        return jsonify({'done': True, 'score': session.get('score', 0)})
    
    q = quiz[current]
    return jsonify({
        'done': False,
        'num': current + 1,
        'total': len(quiz),
        'question': q['question'],
        'choices': q['choices'],
        'score': session.get('score', 0)
    })

@app.route('/answer', methods=['POST'])
def check_answer():
    data = request.json
    answer = data.get('answer')
    
    quiz = session.get('quiz', [])
    current = session.get('current', 0)
    
    if current >= len(quiz):
        return jsonify({'error': 'Quiz done'})
    
    correct = quiz[current]['correct']
    is_correct = answer == correct
    
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    session['current'] = current + 1
    session.modified = True
    
    return jsonify({
        'correct': is_correct,
        'answer': correct,
        'new_score': session['score']
    })

@app.route('/results')
def results():
    score = session.get('score', 0)
    total = len(session.get('quiz', []))
    pct = round((score / total * 100) if total > 0 else 0)
    
    return render_template('results.html', score=score, total=total, pct=pct)

if __name__ == '__main__':
    app.run(debug=True, port=3000)

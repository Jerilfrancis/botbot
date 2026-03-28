import random
from flask import Blueprint, jsonify, request
from app.db import get_db
from app.services.ai_tools import summarize_text, generate_quiz, recommend_courses, build_roadmap

api = Blueprint('api', __name__)


@api.get('/health')
def health():
    return jsonify({'status': 'ok'})


@api.post('/auth/register')
def register():
    data = request.get_json(force=True)
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)',
            (data['name'], data['email'], data['password'], data.get('role', 'student'))
        )
        conn.commit()
        return jsonify({'message': 'registered'}), 201
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400
    finally:
        conn.close()


@api.post('/auth/login')
def login():
    data = request.get_json(force=True)
    conn = get_db()
    row = conn.execute('SELECT id,name,role FROM users WHERE email=? AND password=?', (data['email'], data['password'])).fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'user': dict(row), 'token': f"demo-token-{row['id']}"})


@api.get('/courses')
def list_courses():
    q = request.args.get('q', '')
    conn = get_db()
    rows = conn.execute(
        '''SELECT courses.id, courses.title, courses.topic, courses.description, users.name AS mentor_name
           FROM courses JOIN users ON users.id = courses.mentor_id
           WHERE courses.title LIKE ? OR courses.topic LIKE ? OR users.name LIKE ?
           ORDER BY courses.created_at DESC''',
        (f'%{q}%', f'%{q}%', f'%{q}%')
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@api.post('/courses')
def create_course():
    data = request.get_json(force=True)
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO courses(mentor_id,title,topic,description,thumbnail_url,is_published) VALUES(?,?,?,?,?,?)',
        (data['mentor_id'], data['title'], data['topic'], data['description'], data.get('thumbnail_url'), data.get('is_published', 0))
    )
    conn.commit()
    conn.close()
    return jsonify({'course_id': cur.lastrowid}), 201


@api.post('/enrollments')
def enroll():
    data = request.get_json(force=True)
    conn = get_db()
    try:
        conn.execute('INSERT INTO enrollments(user_id,course_id) VALUES(?,?)', (data['user_id'], data['course_id']))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'enrolled'}), 201


@api.post('/progress')
def save_progress():
    data = request.get_json(force=True)
    completed = 1 if data.get('completion_percent', 0) >= 95 else 0
    conn = get_db()
    conn.execute(
        '''INSERT INTO progress(enrollment_id,module_id,completion_percent,last_position_sec,completed)
           VALUES(?,?,?,?,?)
           ON CONFLICT(enrollment_id,module_id)
           DO UPDATE SET completion_percent=excluded.completion_percent,
                         last_position_sec=excluded.last_position_sec,
                         completed=excluded.completed''',
        (data['enrollment_id'], data['module_id'], data['completion_percent'], data.get('last_position_sec', 0), completed)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'saved'})


@api.post('/assignments/<int:assignment_id>/submit')
def submit_assignment(assignment_id: int):
    data = request.get_json(force=True)
    user_answers = data.get('answers', {})
    conn = get_db()
    questions = conn.execute('SELECT id,answer FROM assignment_questions WHERE assignment_id=?', (assignment_id,)).fetchall()
    assignment = conn.execute('SELECT pass_percent FROM assignments WHERE id=?', (assignment_id,)).fetchone()
    total = len(questions)
    correct = sum(1 for q in questions if user_answers.get(str(q['id'])) == q['answer'])
    score = round((correct / total) * 100) if total else 0
    passed = 1 if assignment and score >= assignment['pass_percent'] else 0
    conn.execute(
        'INSERT INTO assignment_attempts(assignment_id,user_id,score,passed) VALUES(?,?,?,?)',
        (assignment_id, data['user_id'], score, passed)
    )
    conn.commit()
    conn.close()
    return jsonify({'score': score, 'passed': bool(passed)})


@api.get('/leaderboard/<int:course_id>')
def leaderboard(course_id: int):
    conn = get_db()
    rows = conn.execute(
        '''SELECT users.name, MAX(assignment_attempts.score) AS best_score
           FROM assignment_attempts
           JOIN assignments ON assignments.id=assignment_attempts.assignment_id
           JOIN users ON users.id=assignment_attempts.user_id
           WHERE assignments.course_id=?
           GROUP BY users.id
           ORDER BY best_score DESC
           LIMIT 20''',
        (course_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@api.post('/reviews')
def review():
    data = request.get_json(force=True)
    conn = get_db()
    conn.execute(
        '''INSERT INTO reviews(course_id,user_id,rating,comment) VALUES(?,?,?,?)
           ON CONFLICT(course_id,user_id) DO UPDATE SET rating=excluded.rating, comment=excluded.comment''',
        (data['course_id'], data['user_id'], data['rating'], data.get('comment'))
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'review saved'})


@api.post('/notes')
def save_note():
    data = request.get_json(force=True)
    conn = get_db()
    conn.execute('INSERT INTO notes(module_id,user_id,note_text,at_second) VALUES(?,?,?,?)',
                 (data['module_id'], data['user_id'], data['note_text'], data.get('at_second')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'note saved'})


@api.post('/discussions')
def discussion_post():
    data = request.get_json(force=True)
    conn = get_db()
    cur = conn.execute('INSERT INTO discussions(course_id,user_id,parent_id,body) VALUES(?,?,?,?)',
                       (data['course_id'], data['user_id'], data.get('parent_id'), data['body']))
    conn.commit()
    conn.close()
    return jsonify({'discussion_id': cur.lastrowid}), 201


@api.post('/discussions/<int:discussion_id>/upvote')
def upvote(discussion_id: int):
    conn = get_db()
    conn.execute('UPDATE discussions SET upvotes = upvotes + 1 WHERE id=?', (discussion_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'upvoted'})


@api.get('/mentor/<int:mentor_id>/analytics')
def mentor_analytics(mentor_id: int):
    conn = get_db()
    courses = conn.execute('SELECT id,title FROM courses WHERE mentor_id=?', (mentor_id,)).fetchall()
    payload = []
    for course in courses:
        enroll_count = conn.execute('SELECT COUNT(*) AS c FROM enrollments WHERE course_id=?', (course['id'],)).fetchone()['c']
        completion = conn.execute(
            '''SELECT AVG(completed) AS done FROM progress
               JOIN enrollments ON enrollments.id=progress.enrollment_id
               WHERE enrollments.course_id=?''', (course['id'],)
        ).fetchone()['done']
        payload.append({'course_id': course['id'], 'title': course['title'], 'enrollments': enroll_count, 'completion_rate': completion or 0})
    conn.close()
    return jsonify(payload)


@api.get('/admin/analytics')
def admin_analytics():
    conn = get_db()
    users = conn.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
    courses = conn.execute('SELECT COUNT(*) AS c FROM courses').fetchone()['c']
    enrollments = conn.execute('SELECT COUNT(*) AS c FROM enrollments').fetchone()['c']
    conn.close()
    return jsonify({'users': users, 'courses': courses, 'enrollments': enrollments})


@api.post('/ai/summary')
def ai_summary():
    content = request.get_json(force=True).get('content', '')
    return jsonify({'summary': summarize_text(content)})


@api.post('/ai/quiz')
def ai_quiz():
    content = request.get_json(force=True).get('content', '')
    quiz = generate_quiz(content)
    random.shuffle(quiz)
    return jsonify({'quiz': quiz})


@api.post('/ai/recommendations')
def ai_recommendations():
    data = request.get_json(force=True)
    conn = get_db()
    courses = [dict(r) for r in conn.execute('SELECT id,title,topic FROM courses').fetchall()]
    conn.close()
    return jsonify({'recommendations': recommend_courses(data.get('interests', []), courses)})


@api.post('/ai/roadmap')
def ai_roadmap():
    goal = request.get_json(force=True).get('goal', 'Become job ready')
    return jsonify(build_roadmap(goal))

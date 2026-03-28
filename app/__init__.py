from flask import Flask, render_template
from .db import init_db
from .api.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'learnx-dev-secret'

    init_db()
    app.register_blueprint(api, url_prefix='/api')

    @app.get('/')
    def home():
      return render_template('index.html')

    @app.get('/dashboard')
    def dashboard():
      return render_template('dashboard.html')

    @app.get('/course/<int:course_id>')
    def course_page(course_id: int):
      return render_template('course.html', course_id=course_id)

    @app.get('/admin')
    def admin_page():
      return render_template('admin.html')

    @app.get('/mentor/<int:mentor_id>')
    def mentor_page(mentor_id: int):
      return render_template('mentor.html', mentor_id=mentor_id)

    return app

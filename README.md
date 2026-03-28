# LearnX (HTML/CSS/JS + Python Only)

LearnX is a full-stack e-learning platform implemented using:
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Database:** SQLite

No payment features are included.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://localhost:5000

## Folder structure

```
app/
  api/               # API routes for auth, courses, progress, assignments, AI, admin, mentor
  services/          # AI helper logic
  static/
    css/
    js/
    uploads/
    certificates/
  templates/         # HTML pages
  db.py              # SQLite schema + connection
run.py               # App entrypoint
database/            # SQLite file created on first run
docs/
```

## Included modules

- Authentication + role support (student/mentor/admin)
- Course creation + search
- Enrollment + progress tracking
- Assignments + automatic scoring + leaderboard
- Ratings/reviews + notes + discussions/upvotes
- Certificates table support
- Mentor analytics
- Admin analytics
- AI endpoints (summary, quiz generation, recommendations, roadmap)
- Dark mode + responsive UI
